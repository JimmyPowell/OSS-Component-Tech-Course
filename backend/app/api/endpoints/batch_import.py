from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io

from app import models, crud
from app.schemas.user import (
    BatchImportPreviewResponse, 
    BatchImportRequest, 
    BatchImportResult, 
    UserResponse,
    BatchImportUserData,
    ConflictUser
)
from app.api import deps
from app.utils.response import Success, BadRequest, Created

router = APIRouter()

def process_excel_file(file_content: bytes) -> List[dict]:
    """Process uploaded Excel file and return list of user data"""
    try:
        # Read Excel file
        df = pd.read_excel(io.BytesIO(file_content))
        
        # Expected columns: 支持中文和英文列名
        chinese_columns = ['学号', '姓名', '班级']
        english_columns = ['STUDENT_ID', 'STUDENT_NAME', 'STUDENT_CLASS']
        
        # 检查列名映射
        column_mapping = {}
        if all(col in df.columns for col in chinese_columns):
            column_mapping = {'student_id': '学号', 'real_name': '姓名', 'student_class': '班级'}
        elif all(col in df.columns for col in english_columns):
            column_mapping = {'student_id': 'STUDENT_ID', 'real_name': 'STUDENT_NAME', 'student_class': 'STUDENT_CLASS'}
        else:
            # 检查缺少的列
            missing_cn = [col for col in chinese_columns if col not in df.columns]
            missing_en = [col for col in english_columns if col not in df.columns]
            raise ValueError(f"Missing required columns. Expected either: {', '.join(chinese_columns)} or {', '.join(english_columns)}")
        
        # Convert to list of dictionaries
        users_data = []
        for index, row in df.iterrows():
            student_id_col = column_mapping['student_id']
            real_name_col = column_mapping['real_name']
            student_class_col = column_mapping['student_class']
            
            if pd.isna(row[student_id_col]) or pd.isna(row[real_name_col]):
                continue  # Skip rows with missing critical data
                
            user_data = {
                'student_id': str(row[student_id_col]).strip(),
                'real_name': str(row[real_name_col]).strip(),
                'student_class': str(row[student_class_col]).strip() if not pd.isna(row[student_class_col]) else ''
            }
            users_data.append(user_data)
        
        return users_data
        
    except Exception as e:
        raise ValueError(f"Failed to process Excel file: {str(e)}")

@router.post("/preview", response_model=BatchImportPreviewResponse)
async def preview_batch_import(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user)
):
    """
    Preview batch import - parse Excel file and check for conflicts
    """
    if not file.filename.endswith(('.xlsx', '.xls')):
        return BadRequest(message="Only Excel files (.xlsx, .xls) are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process Excel file
        users_data = process_excel_file(file_content)
        
        if not users_data:
            return BadRequest(message="No valid user data found in the file")
        
        # Check for conflicts
        conflicts = crud.crud_user.check_batch_import_conflicts(db, users_data)
        
        # Separate valid users and conflicts
        conflict_indices = {conflict['row_index'] for conflict in conflicts}
        valid_users = [
            BatchImportUserData(**user_data) 
            for i, user_data in enumerate(users_data) 
            if i not in conflict_indices
        ]
        
        conflict_objects = [ConflictUser(**conflict) for conflict in conflicts]
        
        response_data = BatchImportPreviewResponse(
            total_users=len(users_data),
            valid_users=valid_users,
            conflicts=conflict_objects,
            errors=[]
        )
        
        return Success(data=response_data.dict())
        
    except ValueError as e:
        return BadRequest(message=str(e))
    except Exception as e:
        return BadRequest(message=f"Failed to process file: {str(e)}")

@router.post("/execute", response_model=BatchImportResult)
def execute_batch_import(
    request: BatchImportRequest,
    db: Session = Depends(deps.get_db),
    current_manager: models.User = Depends(deps.get_current_manager_user)
):
    """
    Execute batch import with specified conflict resolution strategy
    """
    try:
        # Convert BatchImportUserData to dict
        users_data = [user.dict() for user in request.users]
        
        # If conflict resolution is "cancel", check for conflicts first
        if request.conflict_resolution == "cancel":
            conflicts = crud.crud_user.check_batch_import_conflicts(db, users_data)
            if conflicts:
                return BadRequest(message="Conflicts found. Please resolve them first.")
        
        # Execute batch creation
        result = crud.crud_user.batch_create_users(
            db=db, 
            users_data=users_data, 
            conflict_resolution=request.conflict_resolution
        )
        
        # Convert created users to response format
        created_users_response = [
            UserResponse.from_orm(user).dict() 
            for user in result['created_users']
        ]
        
        response_data = BatchImportResult(
            success_count=result['success_count'],
            error_count=result['error_count'],
            errors=result['errors'],
            created_users=created_users_response
        )
        
        return Created(
            data=response_data.dict(),
            message=f"Successfully created {result['success_count']} users"
        )
        
    except Exception as e:
        return BadRequest(message=f"Batch import failed: {str(e)}")
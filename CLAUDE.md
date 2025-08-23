# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a comprehensive educational platform built with FastAPI backend and Vue.js frontends. It includes:
- Course resource management (PPTs, videos, attachments)
- Homework assignment system
- Student showcase and portfolio features
- Forum discussion system (backend implemented, frontend in progress)
- Separate admin panel for content management

## Architecture

### Backend (FastAPI)
- **Location**: `backend/`
- **Main entry**: `backend/app/main.py`
- **Architecture pattern**: Clean architecture with separation of concerns
- **Key layers**:
  - `models/` - SQLAlchemy ORM models
  - `schemas/` - Pydantic schemas for API validation
  - `crud/` - Database operations layer
  - `api/endpoints/` - API route handlers
  - `services/` - Business logic services
  - `config/` - Database and application configuration

### Frontend (Vue 3)
Two separate Vue.js applications:
1. **User Frontend** (`frontend/`):
   - Main educational platform interface
   - Uses Vue 3 + Vite + Pinia + Bootstrap
   - Ports: dev=5173, preview=5174

2. **Admin Frontend** (`frontend-admin/`):
   - Administrative interface
   - Uses Vue 3 + Vite + Ant Design Vue
   - Ports: dev=5173, preview=5174

### Database
- **Primary**: MySQL with SQLAlchemy ORM
- **Cache**: Redis for JWT blacklisting and caching
- **Schema**: `sql/schema.sql`

## Development Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend (User)
```bash
cd frontend
npm install
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview built app
```

### Frontend Admin
```bash
cd frontend-admin
npm install
npm run dev      # Development server
npm run build    # Production build  
npm run preview  # Preview built app
```

## Configuration
- Backend config via environment variables (see `backend/app/config/settings.py`)
- Required .env file in `backend/` directory with:
  - MySQL credentials
  - Redis connection
  - JWT secrets
  - Email service settings
  - Qiniu cloud storage keys

## API Structure
- Base URL: `/api/v1`
- Authentication: JWT Bearer tokens
- Key endpoints:
  - `/auth` - User authentication
  - `/course-resources` - Course materials
  - `/homeworks` - Assignment management
  - `/showcases` - Student work portfolios
  - `/forum` - Discussion system
  - `/admin/*` - Administrative functions

## Database Models
Core entities include:
- `User` - User accounts with role-based permissions
- `CourseResource` - Educational materials (PPT, video, attachments)
- `Homework` - Assignments and submissions
- `Showcase` - Student portfolio items with comments/replies
- `ForumCategory/Post/Reply` - Discussion forum system
- Like system for showcases and comments

## Key Features
- JWT-based authentication with refresh tokens
- Role-based access control (user/manager)
- File upload via Qiniu cloud storage
- Email verification system
- Soft delete pattern for most entities
- Rich text content support
- Comment and reply threading
- Like/unlike functionality

## Current Development Status
- Backend: Fully implemented including forum system
- User Frontend: Core features implemented, forum UI pending
- Admin Frontend: Management interfaces for all content types
- Database: Complete schema with all relationships

## Notes for Development
- Follow the existing CRUD pattern when adding new features
- All API endpoints should include proper error handling via `app.utils.response`
- Use UUID fields for public-facing identifiers
- Implement proper authorization checks using dependencies in `app.api.deps`
- Frontend state management uses Pinia stores
- Both frontends use Vite for build tooling


## Development History & Feature Updates

### 2025-08-22: Showcase Module Complete Overhaul
**Issue**: 作品展示模块存在多个功能问题和显示错误
**Completed Fixes**:
- ✅ 修复登录状态管理 - 解决用户登录后状态保持问题
- ✅ 修复作品详情页面评论获取逻辑 - 使用正确的数字ID替代UUID
- ✅ 修复后端作品响应数据 - 添加完整的作者信息
- ✅ 修复SQLAlchemy数据库关系映射警告 - 完善外键约束和关系定义
- ✅ 优化点赞功能交互 - 实现完整的点赞/取消点赞实时更新
- ✅ 完善评论系统显示 - 添加错误处理，确保评论正常显示
- ✅ 优化前端页面布局和样式 - 改进用户体验
- ✅ 测试完整的作品展示功能流程 - 验证所有功能正常工作

**Technical Changes**:
- Frontend: 修复ShowcaseDetailPage.vue中的评论回复获取错误处理
- Backend: 完善数据库模型关系映射 (Showcase, ShowcaseComment, User)
- API: 确保所有showcase相关端点正常工作 (200 OK responses)
- Database: 添加缺失的外键约束和关系定义

**Current Status**: 作品展示模块完全可用，包含完整的点赞、评论、作者信息显示功能

## user's notes
- No need to start the frontend or backend server,as user has started
- When it comes to the frontend modification,use the playwright to review
- use chinese when interact with user
- 如果进行计划或规划的话，需要明确指出修改的侵入性成都、完成的预估时间、复杂度、最佳实践

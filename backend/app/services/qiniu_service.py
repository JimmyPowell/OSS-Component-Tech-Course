# -*- coding: utf-8 -*-
import os
import time
import hmac
import base64
import json
from hashlib import sha1
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from qiniu import Auth
from app.config.settings import settings

class QiniuService:
    def __init__(self):
        print("[DEBUG] 初始化七牛云服务...")
        
        self.access_key = os.getenv("QINIU_ACCESS_KEY")
        self.secret_key = os.getenv("QINIU_SECRET_KEY")
        self.bucket = os.getenv("QINIU_BUCKET", "default-bucket")
        self.upload_domain = os.getenv("QINIU_UPLOAD_DOMAIN", "https://upload-z0.qiniup.com")
        self.download_domain = os.getenv("QINIU_DOWNLOAD_DOMAIN", "https://your-domain.com")
        
        print(f"[DEBUG] 七牛云配置:")
        print(f"[DEBUG] - Access Key: {'已设置' if self.access_key else '未设置'}")
        print(f"[DEBUG] - Secret Key: {'已设置' if self.secret_key else '未设置'}")
        print(f"[DEBUG] - Bucket: {self.bucket}")
        print(f"[DEBUG] - Upload Domain: {self.upload_domain}")
        print(f"[DEBUG] - Download Domain: {self.download_domain}")
        
        if not self.access_key or not self.secret_key:
            print("[ERROR] 七牛云凭证未配置!")
            raise ValueError("Qiniu credentials not configured")
            
        try:
            # 初始化七牛云官方Auth对象
            self.qiniu_auth = Auth(self.access_key, self.secret_key)
            print("[DEBUG] 七牛云Auth对象初始化成功")
        except Exception as e:
            print(f"[ERROR] 七牛云Auth对象初始化失败: {e}")
            raise
    
    def _urlsafe_base64_encode(self, data: bytes) -> str:
        """URL-safe base64 encode"""
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')
    
    def _hmac_sha1_sign(self, data: str) -> str:
        """HMAC-SHA1 signature"""
        hashed = hmac.new(
            self.secret_key.encode('utf-8'), 
            data.encode('utf-8'), 
            sha1
        )
        return self._urlsafe_base64_encode(hashed.digest())
    
    def generate_upload_token(
        self, 
        bucket: str = None, 
        key: str = None, 
        expires: int = 3600,
        policy: Dict[str, Any] = None
    ) -> str:
        """
        Generate upload token for Qiniu Cloud Storage using official SDK
        
        Args:
            bucket: Target bucket name
            key: Optional file key
            expires: Token expiration time in seconds (default 3600)
            policy: Additional upload policy
        
        Returns:
            Upload token string
        """
        if not bucket:
            bucket = self.bucket
        
        # 使用官方SDK生成token，确保正确性
        upload_token = self.qiniu_auth.upload_token(bucket, key, expires, policy)
        
        return upload_token
    
    def generate_download_token(
        self, 
        url: str, 
        expires: int = 3600
    ) -> str:
        """
        Generate download token for private resources
        
        Args:
            url: Original URL of the private resource
            expires: Token expiration time in seconds (default 3600)
        
        Returns:
            Download URL with token
        """
        deadline = int(time.time()) + expires
        
        # Add expiration parameter to URL
        if '?' in url:
            url_with_exp = f"{url}&e={deadline}"
        else:
            url_with_exp = f"{url}?e={deadline}"
        
        # Generate signature
        signature = self._hmac_sha1_sign(url_with_exp)
        
        # Add token to URL
        download_url = f"{url_with_exp}&token={self.access_key}:{signature}"
        
        return download_url
    
    def verify_callback(
        self, 
        origin_authorization: str, 
        url: str, 
        body: str = None, 
        content_type: str = 'application/x-www-form-urlencoded'
    ) -> bool:
        """
        Verify Qiniu callback signature
        
        Args:
            origin_authorization: Authorization header from callback
            url: Callback URL
            body: Request body
            content_type: Content type
        
        Returns:
            True if verification passes, False otherwise
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        query = parsed_url.query
        
        data = path
        if query:
            data = f"{data}?{query}"
        data += "\n"
        
        # Add body if present and content type matches
        if body and content_type == 'application/x-www-form-urlencoded':
            data += body
        
        # Generate expected signature
        expected_signature = self._hmac_sha1_sign(data)
        expected_authorization = f"QBox {self.access_key}:{expected_signature}"
        
        return origin_authorization == expected_authorization
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """Get configured bucket information"""
        return {
            "bucket": self.bucket,
            "upload_domain": self.upload_domain,
            "download_domain": self.download_domain,
            "access_key": self.access_key[:8] + "..." if self.access_key else None,
            "configured": bool(self.access_key and self.secret_key)
        }

# Global instance
qiniu_service = QiniuService()
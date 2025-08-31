import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP请求/响应日志记录中间件
    """
    
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.access_logger = logging.getLogger("access")
        self.error_logger = logging.getLogger("error")
        self.app_logger = logging.getLogger("app")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求追踪ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取客户端IP
        client_ip = self._get_client_ip(request)
        
        # 构建请求信息
        method = request.method
        url = str(request.url)
        user_agent = request.headers.get("user-agent", "")
        
        # 记录请求开始
        self.app_logger.info(
            f"[{request_id}] Request started: {method} {url} from {client_ip}"
        )
        
        try:
            # 执行请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录访问日志
            self._log_access(
                client_ip=client_ip,
                method=method,
                url=url,
                status_code=response.status_code,
                process_time=process_time,
                request_id=request_id,
                user_agent=user_agent
            )
            
            # 添加请求ID到响应头
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录错误日志
            self.error_logger.error(
                f"[{request_id}] Request failed: {method} {url} from {client_ip} - "
                f"Error: {str(e)} - Time: {process_time:.3f}s",
                exc_info=True
            )
            
            # 记录访问日志（500错误）
            self._log_access(
                client_ip=client_ip,
                method=method,
                url=url,
                status_code=500,
                process_time=process_time,
                request_id=request_id,
                user_agent=user_agent,
                error=str(e)
            )
            
            # 重新抛出异常
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实IP地址
        """
        # 检查代理头部
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # fallback到直接连接IP
        return request.client.host if request.client else "unknown"

    def _log_access(
        self,
        client_ip: str,
        method: str,
        url: str,
        status_code: int,
        process_time: float,
        request_id: str,
        user_agent: str,
        error: str = None
    ):
        """
        记录访问日志
        """
        # 构建状态信息
        if status_code >= 400:
            status_text = "ERROR" if status_code >= 500 else "WARNING"
        else:
            status_text = "OK"
        
        # 构建日志消息（模仿uvicorn格式）
        log_msg = f'{client_ip} - "{method} {url} HTTP/1.1" {status_code} {status_text}'
        
        # 添加处理时间
        log_msg += f" - {process_time:.3f}s"
        
        # 添加请求ID
        log_msg += f" - [{request_id}]"
        
        # 如果有错误，添加错误信息
        if error:
            log_msg += f" - Error: {error}"
        
        # 根据状态码选择日志级别
        if status_code >= 500:
            self.access_logger.error(log_msg)
        elif status_code >= 400:
            self.access_logger.warning(log_msg)
        else:
            self.access_logger.info(log_msg)


class RequestLoggingMiddleware:
    """
    简化的请求日志中间件，兼容ASGI应用
    """
    
    def __init__(self, app):
        self.app = app
        self.access_logger = logging.getLogger("access")
        self.error_logger = logging.getLogger("error")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        # 获取请求信息
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        client_ip = self._get_client_ip(scope)
        
        # 构建完整URL
        url = path
        if query_string:
            url += f"?{query_string}"

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # 记录响应开始
                status_code = message["status"]
                process_time = time.time() - start_time
                
                # 记录访问日志
                self._log_request(
                    client_ip=client_ip,
                    method=method,
                    url=url,
                    status_code=status_code,
                    process_time=process_time,
                    request_id=request_id
                )
                
                # 添加请求ID到响应头
                headers = list(message.get("headers", []))
                headers.append([b"x-request-id", request_id.encode()])
                message["headers"] = headers
                
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            process_time = time.time() - start_time
            self.error_logger.error(
                f"[{request_id}] Request failed: {method} {url} from {client_ip} - "
                f"Error: {str(e)} - Time: {process_time:.3f}s",
                exc_info=True
            )
            raise

    def _get_client_ip(self, scope):
        """获取客户端IP"""
        # 检查headers中的代理信息
        headers = dict(scope.get("headers", []))
        
        forwarded_for = headers.get(b"x-forwarded-for")
        if forwarded_for:
            return forwarded_for.decode().split(",")[0].strip()
        
        real_ip = headers.get(b"x-real-ip")
        if real_ip:
            return real_ip.decode()
        
        # 从scope中获取客户端信息
        client = scope.get("client")
        if client:
            return client[0]
        
        return "unknown"

    def _log_request(
        self,
        client_ip: str,
        method: str,
        url: str,
        status_code: int,
        process_time: float,
        request_id: str
    ):
        """记录请求日志"""
        # 构建状态文本
        if status_code >= 500:
            status_text = "Internal Server Error"
        elif status_code >= 400:
            status_text = "Client Error"
        elif status_code >= 300:
            status_text = "Redirect"
        else:
            status_text = "OK"
        
        # 构建日志消息（模仿uvicorn格式）
        log_msg = f'{client_ip} - "{method} {url} HTTP/1.1" {status_code} {status_text} - {process_time:.3f}s [{request_id}]'
        
        # 根据状态码选择日志级别
        if status_code >= 500:
            self.access_logger.error(log_msg)
        elif status_code >= 400:
            self.access_logger.warning(log_msg)
        else:
            self.access_logger.info(log_msg)
import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file_path: str = "./logs",
    log_max_size: str = "10MB",
    log_backup_count: int = 30
) -> None:
    """
    设置应用程序日志配置
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file_path: 日志文件路径
        log_max_size: 单个日志文件最大大小
        log_backup_count: 日志文件备份数量
    """
    # 确保日志目录存在
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)
    
    # 解析日志文件大小
    max_bytes = _parse_size(log_max_size)
    
    # 设置根日志器级别
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
    
    # 创建日志格式化器
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    access_formatter = logging.Formatter(
        fmt='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 设置访问日志
    _setup_logger(
        name="access",
        log_file=os.path.join(log_file_path, "access.log"),
        formatter=access_formatter,
        level=logging.INFO,
        max_bytes=max_bytes,
        backup_count=log_backup_count
    )
    
    # 设置错误日志
    _setup_logger(
        name="error",
        log_file=os.path.join(log_file_path, "error.log"),
        formatter=detailed_formatter,
        level=logging.ERROR,
        max_bytes=max_bytes,
        backup_count=log_backup_count
    )
    
    # 设置应用日志
    _setup_logger(
        name="app",
        log_file=os.path.join(log_file_path, "app.log"),
        formatter=detailed_formatter,
        level=getattr(logging, log_level.upper()),
        max_bytes=max_bytes,
        backup_count=log_backup_count
    )


def _setup_logger(
    name: str,
    log_file: str,
    formatter: logging.Formatter,
    level: int,
    max_bytes: int,
    backup_count: int
) -> logging.Logger:
    """
    设置单个日志器
    
    Args:
        name: 日志器名称
        log_file: 日志文件路径
        formatter: 格式化器
        level: 日志级别
        max_bytes: 文件最大大小
        backup_count: 备份文件数量
    
    Returns:
        配置好的日志器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建轮转文件处理器
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # 添加控制台处理器（可选，用于开发调试）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)  # 取消注释以在控制台也输出日志
    
    # 防止日志向上传播到根日志器
    logger.propagate = False
    
    return logger


def _parse_size(size_str: str) -> int:
    """
    解析大小字符串为字节数
    
    Args:
        size_str: 大小字符串，如 "10MB", "1GB"
        
    Returns:
        字节数
    """
    size_str = size_str.upper().strip()
    
    # 提取数字部分
    size_num = ""
    unit = ""
    for char in size_str:
        if char.isdigit() or char == '.':
            size_num += char
        else:
            unit = size_str[len(size_num):]
            break
    
    try:
        size = float(size_num)
    except ValueError:
        size = 10.0  # 默认10MB
        unit = "MB"
    
    # 转换单位
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4
    }
    
    multiplier = multipliers.get(unit.strip(), 1024 ** 2)  # 默认MB
    
    return int(size * multiplier)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称 ("access", "error", "app")
        
    Returns:
        日志器实例
    """
    return logging.getLogger(name)
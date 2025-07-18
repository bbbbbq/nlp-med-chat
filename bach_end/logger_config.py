#!/usr/bin/env python3
"""
医疗AI聊天后端统一日志配置
提供结构化的日志记录功能，支持文件和控制台输出
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

# 日志配置
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
MAIN_LOG_FILE = LOG_DIR / "medical_chat.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
RAG_LOG_FILE = LOG_DIR / "rag_system.log"
API_LOG_FILE = LOG_DIR / "api_calls.log"

# 日志格式
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
SIMPLE_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（仅用于控制台）"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)

def setup_logger(name: str, log_file: Path = None, level: int = logging.INFO, 
                console_output: bool = True, max_bytes: int = 10*1024*1024, 
                backup_count: int = 5) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 日志级别
        console_output: 是否输出到控制台
        max_bytes: 单个日志文件最大大小（字节）
        backup_count: 保留的备份文件数量
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 文件处理器（使用轮转日志）
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=max_bytes, 
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # 如果是终端环境，使用彩色输出
        if sys.stdout.isatty():
            console_formatter = ColoredFormatter(SIMPLE_FORMAT)
        else:
            console_formatter = logging.Formatter(SIMPLE_FORMAT)
        
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger

def setup_all_loggers():
    """设置所有系统日志记录器"""
    
    # 主应用日志
    main_logger = setup_logger(
        "medical_chat", 
        MAIN_LOG_FILE, 
        level=logging.INFO
    )
    
    # 错误日志（只记录ERROR及以上级别）
    error_logger = setup_logger(
        "error", 
        ERROR_LOG_FILE, 
        level=logging.ERROR,
        console_output=False
    )
    
    # RAG系统日志
    rag_logger = setup_logger(
        "rag_system", 
        RAG_LOG_FILE, 
        level=logging.INFO
    )
    
    # API调用日志
    api_logger = setup_logger(
        "api_calls", 
        API_LOG_FILE, 
        level=logging.INFO
    )
    
    return {
        'main': main_logger,
        'error': error_logger,
        'rag': rag_logger,
        'api': api_logger
    }

# 全局日志记录器
loggers = setup_all_loggers()

# 便捷的日志记录函数
def log_info(message: str, logger_name: str = "main"):
    """记录信息日志"""
    loggers[logger_name].info(message)

def log_warning(message: str, logger_name: str = "main"):
    """记录警告日志"""
    loggers[logger_name].warning(message)

def log_error(message: str, logger_name: str = "main", exc_info: bool = False):
    """记录错误日志"""
    loggers[logger_name].error(message, exc_info=exc_info)
    # 同时记录到错误日志文件
    loggers["error"].error(message, exc_info=exc_info)

def log_debug(message: str, logger_name: str = "main"):
    """记录调试日志"""
    loggers[logger_name].debug(message)

def log_api_call(method: str, url: str, status_code: int = None, 
                response_time: float = None, error: str = None):
    """记录API调用日志"""
    message = f"API调用 - 方法: {method}, URL: {url}"
    if status_code:
        message += f", 状态码: {status_code}"
    if response_time:
        message += f", 响应时间: {response_time:.3f}s"
    if error:
        message += f", 错误: {error}"
    
    loggers["api"].info(message)

def log_rag_operation(operation: str, details: str = None, 
                     relevance_score: float = None, knowledge_count: int = None):
    """记录RAG操作日志"""
    message = f"RAG操作 - {operation}"
    if details:
        message += f", 详情: {details}"
    if relevance_score is not None:
        message += f", 相关度: {relevance_score:.3f}"
    if knowledge_count is not None:
        message += f", 知识条数: {knowledge_count}"
    
    loggers["rag"].info(message)

def log_user_interaction(user_id: str = None, action: str = None, 
                        details: str = None, session_id: str = None):
    """记录用户交互日志"""
    message = f"用户交互"
    if user_id:
        message += f" - 用户ID: {user_id}"
    if session_id:
        message += f", 会话ID: {session_id}"
    if action:
        message += f", 操作: {action}"
    if details:
        message += f", 详情: {details}"
    
    loggers["main"].info(message)

# 系统启动日志
def log_system_startup():
    """记录系统启动日志"""
    startup_message = f"""
{'='*60}
医疗AI聊天系统启动
启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Python版本: {sys.version}
工作目录: {os.getcwd()}
日志目录: {LOG_DIR.absolute()}
{'='*60}
"""
    log_info(startup_message)

if __name__ == "__main__":
    # 测试日志系统
    log_system_startup()
    log_info("这是一条信息日志")
    log_warning("这是一条警告日志")
    log_error("这是一条错误日志")
    log_debug("这是一条调试日志")
    log_api_call("POST", "https://api.example.com", 200, 0.5)
    log_rag_operation("知识检索", "心血管症状", 0.85, 3)
    log_user_interaction("user123", "症状分析", "上传医疗影像", "session456")
    
    print(f"\n日志文件已创建在: {LOG_DIR.absolute()}")
    print("请查看以下日志文件:")
    for log_file in [MAIN_LOG_FILE, ERROR_LOG_FILE, RAG_LOG_FILE, API_LOG_FILE]:
        if log_file.exists():
            print(f"  - {log_file}")

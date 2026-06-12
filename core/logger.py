# -*- coding: utf-8 -*-
"""
日志模块

本模块提供统一的日志记录功能。
负责配置日志格式、日志级别、日志文件输出。

设计原则：
- 使用 Python 标准 logging 模块
- 日志文件输出到项目根目录下的 log 文件夹
- 支持控制台和文件双输出
- 按日期自动分割日志文件
- 保持与项目代码风格一致

作者：FlowSphere Team
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


# 默认日志格式
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"

# 日期格式
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


class Logger:
    """
    日志管理类
    
    提供统一的日志记录功能，支持控制台和文件输出。
    
    功能特性：
    - 初始化日志配置
    - 获取模块日志记录器
    - 按日期自动分割日志文件
    - 支持日志文件大小限制
    
    使用示例：
        >>> from core.logger import Logger
        >>> Logger.init()
        >>> logger = Logger.get_logger(__name__)
        >>> logger.info("应用启动")
    """
    
    # 日志目录（与 core 同级）
    _log_dir = None
    
    # 初始化标志
    _initialized = False
    
    # 默认日志级别
    _log_level = logging.INFO
    
    # 日志文件最大大小（10MB）
    _max_file_size = 10 * 1024 * 1024
    
    # 保留的日志文件数量
    _backup_count = 5
    
    @classmethod
    def init(cls, log_dir: Optional[str] = None, log_level: str = "INFO"):
        """
        初始化日志配置
        
        设置日志目录、日志级别，创建必要的目录结构。
        
        Args:
            log_dir: 日志目录路径，默认为项目根目录下的 log 文件夹
            log_level: 日志级别，默认为 INFO
        """
        if cls._initialized:
            return
        
        # 获取项目根目录
        project_root = Path(__file__).parent.parent
        
        # 设置日志目录
        if log_dir:
            cls._log_dir = Path(log_dir)
        else:
            cls._log_dir = project_root / "log"
        
        # 确保日志目录存在
        cls._log_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置日志级别
        cls._log_level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(cls._log_level)
        
        # 清除已有的处理器
        root_logger.handlers.clear()
        
        # 添加控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(cls._log_level)
        console_handler.setFormatter(logging.Formatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        ))
        root_logger.addHandler(console_handler)
        
        # 添加文件处理器（使用 RotatingFileHandler）
        log_file = cls._log_dir / "app.log"
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=cls._max_file_size,
            backupCount=cls._backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(cls._log_level)
        file_handler.setFormatter(logging.Formatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        ))
        root_logger.addHandler(file_handler)
        
        cls._initialized = True
        
        # 记录初始化日志
        logger = cls.get_logger(__name__)
        logger.info("=" * 50)
        logger.info("日志系统初始化完成")
        logger.info("日志目录: %s", cls._log_dir)
        logger.info("日志级别: %s", logging.getLevelName(cls._log_level))
        logger.info("=" * 50)
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称，通常使用 __name__
            
        Returns:
            logging.Logger: 日志记录器实例
            
        使用示例：
            >>> logger = Logger.get_logger("core.todo_service")
            >>> logger.info("创建待办事项")
        """
        if not cls._initialized:
            cls.init()
        
        return logging.getLogger(name)
    
    @classmethod
    def set_level(cls, level: str):
        """
        动态设置日志级别
        
        Args:
            level: 日志级别字符串（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        """
        new_level = LOG_LEVELS.get(level.upper(), logging.INFO)
        cls._log_level = new_level
        
        # 更新根日志记录器级别
        root_logger = logging.getLogger()
        root_logger.setLevel(new_level)
        
        # 更新所有处理器的级别
        for handler in root_logger.handlers:
            handler.setLevel(new_level)
    
    @classmethod
    def get_log_dir(cls) -> Optional[Path]:
        """
        获取日志目录路径
        
        Returns:
            Optional[Path]: 日志目录路径
        """
        if not cls._initialized:
            cls.init()
        
        return cls._log_dir

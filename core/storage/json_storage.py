# -*- coding: utf-8 -*-
"""
JSON 文件存储模块

本模块提供 JSON 文件的读写功能。
遵循单一职责原则，只负责 JSON 文件的读写操作，不包含业务逻辑。

功能说明：
- 读取 JSON 文件并返回数据
- 将数据写入 JSON 文件
- 处理文件不存在和格式损坏的情况
- 使用临时文件写入，避免写入过程中断导致文件损坏

使用示例：
    >>> from storage.json_storage import JsonStorage
    >>> storage = JsonStorage("data/todos.json")
    >>> data = storage.read()
    >>> storage.write(data)
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, List, Optional

from core.logger import Logger

# 获取模块日志记录器
logger = Logger.get_logger(__name__)


class JsonStorage:
    """
    JSON 文件存储类
    
    本类负责 JSON 文件的读写操作，提供简洁的 API 接口。
    
    特点：
    - 使用临时文件写入，确保原子性
    - 支持备份损坏的文件
    - 自动创建不存在的目录
    
    使用示例：
        >>> storage = JsonStorage("data/todos.json")
        >>> # 读取数据
        >>> data = storage.read()
        >>> # 写入数据
        >>> storage.write(data)
    """
    
    def __init__(self, file_path: str):
        """
        初始化 JSON 存储
        
        Args:
            file_path: JSON 文件的路径
        """
        self.file_path = Path(file_path)
    
    def read(self) -> List[dict]:
        """
        读取 JSON 文件
        
        读取 JSON 文件内容并返回数据列表。
        如果文件不存在，返回空列表。
        如果文件格式损坏，备份原文件并返回空列表。
        
        Returns:
            list: JSON 数据列表
            
        使用示例：
            >>> storage = JsonStorage("data/todos.json")
            >>> data = storage.read()
            >>> print(len(data))  # 数据条数
        """
        logger.debug("读取 JSON 文件: %s", self.file_path)
        
        # 如果文件不存在，返回空列表
        if not self.file_path.exists():
            logger.debug("JSON 文件不存在: %s", self.file_path)
            return []
        
        try:
            # 读取 JSON 文件
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 确保返回的是列表
            if not isinstance(data, list):
                logger.warning("JSON 文件格式错误，期望列表类型: %s", self.file_path)
                return []
            
            logger.debug("JSON 文件读取成功，数据条数: %d", len(data))
            return data
            
        except json.JSONDecodeError:
            # JSON 格式损坏，备份原文件
            logger.error("JSON 文件格式损坏: %s", self.file_path)
            self._backup_corrupted_file()
            return []
        except Exception as e:
            # 其他异常，返回空列表
            logger.error("读取 JSON 文件时发生错误: %s", str(e))
            return []
    
    def write(self, data: List[dict]) -> bool:
        """
        写入 JSON 文件
        
        将数据列表写入 JSON 文件。
        使用临时文件写入，确保原子性。
        
        Args:
            data: 要写入的数据列表
            
        Returns:
            bool: 写入是否成功
            
        使用示例：
            >>> storage = JsonStorage("data/todos.json")
            >>> success = storage.write([{"id": "1", "title": "test"}])
            >>> print(success)  # True
        """
        logger.debug("写入 JSON 文件: %s", self.file_path)
        
        try:
            # 确保数据是列表
            if not isinstance(data, list):
                data = [data]
            
            # 确保目录存在
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建临时文件进行写入
            temp_fd, temp_path = tempfile.mkstemp(
                dir=self.file_path.parent,
                suffix='.tmp'
            )
            
            try:
                # 写入临时文件
                with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 如果原文件存在，先备份
                if self.file_path.exists():
                    backup_path = self.file_path.with_suffix('.json.bak')
                    shutil.copy2(self.file_path, backup_path)
                
                # 原子性替换原文件
                shutil.move(temp_path, self.file_path)
                
                # 删除备份文件
                backup_path = self.file_path.with_suffix('.json.bak')
                if backup_path.exists():
                    backup_path.unlink()
                
                logger.debug("JSON 文件写入成功，数据条数: %d", len(data))
                return True
                
            except Exception as e:
                # 写入失败，清理临时文件
                logger.error("写入 JSON 文件时发生错误: %s", str(e))
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise
                
        except Exception as e:
            logger.error("写入 JSON 文件失败: %s", str(e))
            return False
    
    def append(self, item: dict) -> bool:
        """
        向 JSON 文件追加一条数据
        
        读取现有数据，追加新数据，然后写入文件。
        
        Args:
            item: 要追加的数据字典
            
        Returns:
            bool: 追加是否成功
            
        使用示例：
            >>> storage = JsonStorage("data/todos.json")
            >>> success = storage.append({"id": "2", "title": "new item"})
        """
        logger.debug("向 JSON 文件追加数据: %s", self.file_path)
        
        try:
            # 读取现有数据
            data = self.read()
            
            # 追加新数据
            data.append(item)
            
            # 写入文件
            result = self.write(data)
            
            if result:
                logger.debug("数据追加成功")
            else:
                logger.error("数据追加失败")
            
            return result
            
        except Exception as e:
            logger.error("追加数据时发生错误: %s", str(e))
            return False
    
    def update(self, item: dict, key: str = "id") -> bool:
        """
        更新 JSON 文件中的一条数据
        
        根据指定的键查找并更新数据。
        
        Args:
            item: 要更新的数据字典
            key: 用于查找的键名，默认为 "id"
            
        Returns:
            bool: 更新是否成功
            
        使用示例：
            >>> storage = JsonStorage("data/todos.json")
            >>> success = storage.update({"id": "1", "title": "updated"})
        """
        logger.debug("更新 JSON 文件中的数据: %s", self.file_path)
        
        try:
            # 读取现有数据
            data = self.read()
            
            # 查找并更新数据
            updated = False
            for i, existing_item in enumerate(data):
                if existing_item.get(key) == item.get(key):
                    data[i] = item
                    updated = True
                    break
            
            if not updated:
                logger.warning("未找到要更新的数据，键: %s=%s", key, item.get(key))
                return False
            
            # 写入文件
            result = self.write(data)
            
            if result:
                logger.debug("数据更新成功")
            else:
                logger.error("数据更新失败")
            
            return result
            
        except Exception as e:
            logger.error("更新数据时发生错误: %s", str(e))
            return False
    
    def delete(self, item_id: str, key: str = "id") -> bool:
        """
        从 JSON 文件中删除一条数据
        
        根据指定的键查找并删除数据。
        
        Args:
            item_id: 要删除的数据ID
            key: 用于查找的键名，默认为 "id"
            
        Returns:
            bool: 删除是否成功
            
        使用示例：
            >>> storage = JsonStorage("data/todos.json")
            >>> success = storage.delete("1")
        """
        logger.debug("从 JSON 文件删除数据: %s", self.file_path)
        
        try:
            # 读取现有数据
            data = self.read()
            
            # 查找并删除数据
            original_length = len(data)
            data = [item for item in data if item.get(key) != item_id]
            
            if len(data) == original_length:
                logger.warning("未找到要删除的数据，键: %s=%s", key, item_id)
                return False
            
            # 写入文件
            result = self.write(data)
            
            if result:
                logger.debug("数据删除成功")
            else:
                logger.error("数据删除失败")
            
            return result
            
        except Exception as e:
            logger.error("删除数据时发生错误: %s", str(e))
            return False
    
    def soft_delete(self, item_id: str, key: str = "id") -> bool:
        """
        软删除 JSON 文件中的一条数据
        
        根据指定的键查找数据，将其标记为已删除而不是真正删除。
        需要数据中存在 is_deleted 字段。
        
        Args:
            item_id: 要删除的数据ID
            key: 用于查找的键名，默认为 "id"
            
        Returns:
            bool: 软删除是否成功
            
        使用示例：
            >>> storage = JsonStorage("data/todos.json")
            >>> success = storage.soft_delete("1")
        """
        logger.debug("软删除 JSON 文件中的数据: %s", self.file_path)
        
        try:
            # 读取现有数据
            data = self.read()
            
            # 查找并标记为已删除
            updated = False
            for i, item in enumerate(data):
                if item.get(key) == item_id:
                    data[i]["is_deleted"] = True
                    updated = True
                    break
            
            if not updated:
                logger.warning("未找到要软删除的数据，键: %s=%s", key, item_id)
                return False
            
            # 写入文件
            result = self.write(data)
            
            if result:
                logger.debug("数据软删除成功")
            else:
                logger.error("数据软删除失败")
            
            return result
            
        except Exception as e:
            logger.error("软删除数据时发生错误: %s", str(e))
            return False
    
    def count(self) -> int:
        """
        获取 JSON 文件中的数据条数
        
        Returns:
            int: 数据条数
            
        使用示例：
            >>> storage = JsonStorage("data/todos.json")
            >>> print(storage.count())  # 0
        """
        return len(self.read())
    
    def exists(self) -> bool:
        """
        检查 JSON 文件是否存在
        
        Returns:
            bool: 文件是否存在
        """
        return self.file_path.exists()
    
    def _backup_corrupted_file(self) -> Optional[Path]:
        """
        备份损坏的 JSON 文件
        
        将损坏的文件重命名为 .corrupted 后缀，便于用户查看。
        
        Returns:
            Path: 备份文件的路径，如果备份失败返回 None
        """
        try:
            if self.file_path.exists():
                # 创建备份文件名
                backup_path = self.file_path.with_suffix('.json.corrupted')
                
                # 重命名文件
                shutil.move(str(self.file_path), str(backup_path))
                
                return backup_path
            
            return None
            
        except Exception:
            return None
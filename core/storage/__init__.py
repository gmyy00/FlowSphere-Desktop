# -*- coding: utf-8 -*-
"""
存储包

本包提供数据存储功能，负责 JSON 文件的读写操作。
遵循单一职责原则，只负责文件的读写，不包含业务逻辑。

使用示例：
    >>> from storage import JsonStorage
    >>> storage = JsonStorage("data/todos.json")
    >>> data = storage.read()
    >>> storage.write(data)
"""

from .json_storage import JsonStorage

__all__ = ["JsonStorage"]
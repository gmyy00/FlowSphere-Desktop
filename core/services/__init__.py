# -*- coding: utf-8 -*-
"""
服务模块包

本包包含所有业务逻辑服务。

服务层职责：
- 处理业务逻辑
- 协调模型层和存储层
- 不直接操作 UI

作者：FlowSphere Team
"""

from core.services.todo_service import TodoService

__all__ = ["TodoService"]

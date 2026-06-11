# -*- coding: utf-8 -*-
"""
数据模型包

本包包含FlowSphere Desktop项目的数据模型类。
提供了Todo（待办事项）核心数据模型。

设计说明：
- 所有日程本质上都是待办事项，日程是定时重复的待办
- 本包只保留Todo一个核心数据模型，不再单独定义Schedule

本包遵循贫血模型设计原则：
- 模型类只包含数据字段定义
- 业务逻辑应在对应的Service层中实现

使用示例：
    >>> from models import Todo
    >>> # 创建待办
    >>> todo = Todo(
    ...     title="完成项目文档",
    ...     description="需要完成设计文档",
    ...     deadline="2026-06-15T18:00",
    ...     notification="2026-06-15T17:30"
    ... )
"""

from .todo import Todo

__all__ = ["Todo"]
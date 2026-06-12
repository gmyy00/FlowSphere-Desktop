# -*- coding: utf-8 -*-
"""
待办事项数据模型模块

本模块定义了待办事项(Todo)的数据结构，使用Python dataclass实现。
遵循贫血模型设计原则：模型类只包含数据字段定义和基本的序列化/反序列化方法，
不包含业务逻辑。业务逻辑应在对应的Service层中实现。

数据模型说明：
- 所有日程本质上都是待办事项，日程是定时重复的待办
- notification 字段储存完整的具体时间，用于设置提醒时间
- repeat 字段储存是否重复提醒以及重复规则
- 真正的提醒时间规则（如"每周星期四22:16"）由业务层根据这两个字段组合生成

作者：FlowSphere Team
"""

from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Todo:
    """
    待办事项数据模型类（贫血模型）
    
    本类用于表示一个待办事项，只包含数据字段定义。
    业务逻辑（如完成待办、更新字段、生成展示文本等）应在 Service 层中实现。
    
    字段说明：
        - id: 唯一标识符，使用uuid4自动生成
        - title: 待办标题，必填字段
        - description: 待办的文字描述，可选字段
        - notification: 提醒时间，ISO 8601格式，精确到分钟
        - repeat: 重复规则枚举值
        - done: 完成状态，默认为False
        - created_at: 创建时间，ISO 8601格式
    
    使用示例：
        >>> todo = Todo(
        ...     title="完成项目文档",
        ...     description="需要完成设计文档",
        ...     notification="2026-06-15T17:30"
        ... )
        >>> data = todo.to_dict()
        >>> todo2 = Todo.from_dict(data)
    """
    
    # 唯一标识符，使用uuid4生成，确保本地唯一性
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # 待办标题，必填字段
    title: str = ""
    
    # 待办的文字描述，可选字段
    description: Optional[str] = None
    
    # 提醒时间，ISO 8601格式，精确到分钟
    # 储存完整的具体时间，用于设置提醒时间
    # 业务层会根据 notification 和 repeat 字段组合生成展示文本
    notification: Optional[str] = None
    
    # 重复规则枚举值
    # 可选值：none, yearly, monthly, weekly, weekdays, daily
    # 默认值：none（不重复）
    repeat: str = "none"
    
    # 完成状态，默认为False（未完成）
    # 根据规则：标记为done=true后停止提醒
    done: bool = False
    
    # 软删除标记，默认为False（未删除）
    # 设置为True后，该待办事项将被隐藏但不真正删除
    is_deleted: bool = False
    
    # 创建时间，ISO 8601格式
    created_at: str = field(default_factory=lambda: "")
    
    def to_dict(self) -> dict:
        """
        将Todo对象转换为字典，用于JSON序列化
        
        本方法将Todo对象的所有字段转换为字典格式，便于存储到JSON文件。
        
        Returns:
            dict: 包含所有字段的字典对象
            
        使用示例：
            >>> todo = Todo(title="测试")
            >>> data = todo.to_dict()
            >>> print(data["title"])  # "测试"
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "notification": self.notification,
            "repeat": self.repeat,
            "done": self.done,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Todo":
        """
        从字典创建Todo对象，用于JSON反序列化
        
        本类方法从字典数据创建Todo对象，用于从JSON文件加载数据。
        
        Args:
            data: 包含Todo数据的字典，通常来自JSON解析
            
        Returns:
            Todo: 新创建的Todo对象
            
        使用示例：
            >>> data = {"title": "测试", "done": False}
            >>> todo = Todo.from_dict(data)
            >>> print(todo.title)  # "测试"
        """
        if not data:
            return cls()
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            description=data.get("description"),
            notification=data.get("notification"),
            repeat=data.get("repeat", "none"),
            done=data.get("done", False),
            is_deleted=data.get("is_deleted", False),
            created_at=data.get("created_at", "")
        )
        
        try:
            from datetime import datetime
            deadline_time = datetime.fromisoformat(self.deadline)
            now = datetime.now()
            return now > deadline_time
        except (ValueError, TypeError):
            return False
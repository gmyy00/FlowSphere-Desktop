# -*- coding: utf-8 -*-
"""
待办服务模块

本模块实现了待办事项的业务逻辑。
负责待办事项的创建、读取、更新、删除等操作。

设计原则：
- 遵循单一职责原则
- 与存储层交互
- 处理业务规则和校验
- 不直接操作 UI

作者：FlowSphere Team
"""

import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from core.models.todo import Todo
from core.storage.json_storage import JsonStorage
from core.logger import Logger

# 获取模块日志记录器
logger = Logger.get_logger(__name__)


class TodoService:
    """
    待办服务类
    
    提供待办事项的业务逻辑处理。
    
    功能特性：
    - 创建待办事项
    - 读取待办事项列表
    - 更新待办事项
    - 删除待办事项
    - 切换完成状态
    - 查询待提醒的待办事项
    
    使用示例：
        >>> service = TodoService()
        >>> todos = service.list_todos()
        >>> service.create_todo({"title": "新待办"})
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化待办服务
        
        Args:
            data_dir: 数据文件目录
        """
        logger.info("初始化待办服务，数据目录: %s", data_dir)
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化存储
        self.storage = JsonStorage(str(self.data_dir / "todos.json"))
        logger.info("待办服务初始化完成")
    
    def list_todos(self) -> List[Todo]:
        """
        获取所有未软删除的待办事项列表
        
        Returns:
            List[Todo]: 未软删除的待办事项列表
        """
        data_list = self.storage.read()
        todos = []
        for data in data_list:
            todo = Todo.from_dict(data)
            if not todo.is_deleted:
                todos.append(todo)
        return todos
    
    def list_active_todos(self) -> List[Todo]:
        """
        获取所有未软删除的待办事项列表（别名，语义更清晰）
        
        Returns:
            List[Todo]: 未软删除的待办事项列表
        """
        return self.list_todos()
    
    def list_deleted_todos(self) -> List[Todo]:
        """
        获取所有已软删除的待办事项列表（回收站）
        
        Returns:
            List[Todo]: 已软删除的待办事项列表
        """
        data_list = self.storage.read()
        todos = []
        for data in data_list:
            todo = Todo.from_dict(data)
            if todo.is_deleted:
                todos.append(todo)
        return todos
    
    def get_todo(self, todo_id: str) -> Optional[Todo]:
        """
        根据 ID 获取单个待办事项（包括已软删除的）
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            Optional[Todo]: 待办事项对象，如果不存在返回 None
        """
        data_list = self.storage.read()
        for data in data_list:
            todo = Todo.from_dict(data)
            if todo.id == todo_id:
                return todo
        return None
    
    def search_todos_by_description(self, keyword: str) -> List[Todo]:
        """
        根据 description 关键字搜索待办事项
        
        Args:
            keyword: 搜索关键字
            
        Returns:
            List[Todo]: 匹配的待办事项列表
        """
        if not keyword:
            return self.list_todos()
        
        todos = self.list_todos()
        result = []
        keyword_lower = keyword.lower()
        
        for todo in todos:
            if todo.description and keyword_lower in todo.description.lower():
                result.append(todo)
        
        return result
    
    def search_todos_by_title(self, keyword: str) -> List[Todo]:
        """
        根据 title 关键字搜索待办事项
        
        Args:
            keyword: 搜索关键字
            
        Returns:
            List[Todo]: 匹配的待办事项列表
        """
        if not keyword:
            return self.list_todos()
        
        todos = self.list_todos()
        result = []
        keyword_lower = keyword.lower()
        
        for todo in todos:
            if keyword_lower in todo.title.lower():
                result.append(todo)
        
        return result
    
    def create_todo(self, todo_data: dict) -> Optional[Todo]:
        """
        创建新的待办事项
        
        Args:
            todo_data: 待办事项数据字典
            
        Returns:
            Optional[Todo]: 新创建的待办事项对象
        """
        logger.info("创建新待办事项: %s", todo_data.get("title", "未命名"))
        
        # 校验必填字段
        if not todo_data.get("title"):
            logger.warning("创建待办事项失败: 标题为空")
            raise ValueError("待办标题不能为空")
        
        # 创建 Todo 对象
        todo = Todo(
            title=todo_data["title"],
            description=todo_data.get("description"),
            notification=todo_data.get("notification"),
            repeat=todo_data.get("repeat", "none"),
            done=todo_data.get("done", False),
            created_at=datetime.now().isoformat()
        )
        
        # 保存到存储
        data = todo.to_dict()
        success = self.storage.append(data)
        
        if success:
            logger.info("待办事项创建成功，ID: %s", todo.id)
            return todo
        else:
            logger.error("待办事项创建失败，标题: %s", todo_data["title"])
            raise Exception("创建待办事项失败")
    
    def update_todo(self, todo_data: dict) -> Optional[Todo]:
        """
        更新待办事项
        
        Args:
            todo_data: 待办事项数据字典，必须包含 id
            
        Returns:
            Optional[Todo]: 更新后的待办事项对象
        """
        todo_id = todo_data.get("id")
        logger.info("更新待办事项，ID: %s", todo_id)
        
        if not todo_id:
            logger.warning("更新待办事项失败: ID 为空")
            raise ValueError("待办事项 ID 不能为空")
        
        # 获取现有待办事项
        existing_todo = self.get_todo(todo_id)
        if not existing_todo:
            logger.warning("更新待办事项失败: 待办事项不存在，ID: %s", todo_id)
            raise ValueError("待办事项不存在")
        
        # 更新字段
        if "title" in todo_data:
            existing_todo.title = todo_data["title"]
        if "description" in todo_data:
            existing_todo.description = todo_data["description"]
        if "notification" in todo_data:
            existing_todo.notification = todo_data["notification"]
        if "repeat" in todo_data:
            existing_todo.repeat = todo_data["repeat"]
        if "done" in todo_data:
            existing_todo.done = todo_data["done"]
        
        # 保存到存储
        data = existing_todo.to_dict()
        success = self.storage.update(data)
        
        if success:
            logger.info("待办事项更新成功，ID: %s", todo_id)
            return existing_todo
        else:
            logger.error("待办事项更新失败，ID: %s", todo_id)
            raise Exception("更新待办事项失败")
    
    def delete_todo(self, todo_id: str) -> bool:
        """
        彻底删除待办事项
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            bool: 删除是否成功
        """
        logger.info("彻底删除待办事项，ID: %s", todo_id)
        result = self.storage.delete(todo_id)
        if result:
            logger.info("待办事项删除成功，ID: %s", todo_id)
        else:
            logger.warning("待办事项删除失败，ID: %s", todo_id)
        return result
    
    def soft_delete_todo(self, todo_id: str) -> bool:
        """
        软删除单个待办事项
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            bool: 软删除是否成功
        """
        logger.info("软删除待办事项，ID: %s", todo_id)
        
        todo = self.get_todo(todo_id)
        if not todo:
            logger.warning("软删除待办事项失败: 待办事项不存在，ID: %s", todo_id)
            return False
        
        result = self.storage.soft_delete(todo_id)
        
        if result:
            logger.info("待办事项软删除成功，ID: %s", todo_id)
        else:
            logger.error("待办事项软删除失败，ID: %s", todo_id)
        
        return result
    
    def batch_soft_delete(self, todo_ids: List[str]) -> int:
        """
        批量软删除多个待办事项
        
        Args:
            todo_ids: 待办事项 ID 列表
            
        Returns:
            int: 成功软删除的数量
        """
        count = 0
        for todo_id in todo_ids:
            if self.soft_delete_todo(todo_id):
                count += 1
        return count
    
    def restore_todo(self, todo_id: str) -> bool:
        """
        恢复已软删除的待办事项
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            bool: 恢复是否成功
        """
        logger.info("恢复待办事项，ID: %s", todo_id)
        
        todo = self.get_todo(todo_id)
        if not todo or not todo.is_deleted:
            logger.warning("恢复待办事项失败: 待办事项不存在或未被删除，ID: %s", todo_id)
            return False
        
        todo.is_deleted = False
        result = self.storage.update(todo.to_dict())
        
        if result:
            logger.info("待办事项恢复成功，ID: %s", todo_id)
        else:
            logger.error("待办事项恢复失败，ID: %s", todo_id)
        
        return result
    
    def batch_restore_todos(self, todo_ids: List[str]) -> int:
        """
        批量恢复已软删除的待办事项
        
        Args:
            todo_ids: 待办事项 ID 列表
            
        Returns:
            int: 成功恢复的数量
        """
        count = 0
        for todo_id in todo_ids:
            if self.restore_todo(todo_id):
                count += 1
        return count
    
    def permanent_delete_todo(self, todo_id: str) -> bool:
        """
        彻底删除已软删除的待办事项
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            bool: 彻底删除是否成功
        """
        todo = self.get_todo(todo_id)
        if not todo or not todo.is_deleted:
            return False
        
        return self.storage.delete(todo_id)
    
    def batch_permanent_delete(self, todo_ids: List[str]) -> int:
        """
        批量彻底删除已软删除的待办事项
        
        Args:
            todo_ids: 待办事项 ID 列表
            
        Returns:
            int: 成功彻底删除的数量
        """
        count = 0
        for todo_id in todo_ids:
            if self.permanent_delete_todo(todo_id):
                count += 1
        return count
    
    def clear_recycle_bin(self) -> int:
        """
        清空回收站，彻底删除所有已软删除的待办事项
        
        Returns:
            int: 成功彻底删除的数量
        """
        deleted_todos = self.list_deleted_todos()
        count = 0
        for todo in deleted_todos:
            if self.storage.delete(todo.id):
                count += 1
        return count
    
    def toggle_todo(self, todo_id: str) -> Optional[Todo]:
        """
        切换待办事项完成状态
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            Optional[Todo]: 更新后的待办事项对象
        """
        logger.info("切换待办事项状态，ID: %s", todo_id)
        
        todo = self.get_todo(todo_id)
        if not todo:
            logger.warning("切换待办事项状态失败: 待办事项不存在，ID: %s", todo_id)
            raise ValueError("待办事项不存在")
        
        # 切换完成状态
        todo.done = not todo.done
        logger.debug("待办事项状态切换为: %s", "已完成" if todo.done else "未完成")
        
        # 保存到存储
        data = todo.to_dict()
        success = self.storage.update(data)
        
        if success:
            logger.info("待办事项状态更新成功，ID: %s", todo_id)
            return todo
        else:
            logger.error("待办事项状态更新失败，ID: %s", todo_id)
            raise Exception("更新待办事项状态失败")
    
    def list_pending_reminders(self) -> List[Todo]:
        """
        获取待提醒的待办事项列表
        
        查询所有需要提醒且未完成的待办事项。
        
        Returns:
            List[Todo]: 待提醒的待办事项列表
        """
        todos = self.list_todos()
        pending_reminders = []
        
        now = datetime.now()
        
        for todo in todos:
            # 跳过已完成的待办
            if todo.done:
                continue
            
            # 检查是否有提醒时间
            if not todo.notification:
                continue
            
            try:
                # 解析提醒时间
                notification_time = datetime.fromisoformat(todo.notification)
                
                # 如果提醒时间已到或已过，添加到待提醒列表
                if now >= notification_time:
                    pending_reminders.append(todo)
            except (ValueError, TypeError):
                # 时间格式错误，跳过
                continue
        
        return pending_reminders
    
    def mark_reminded(self, todo_id: str) -> bool:
        """
        标记待办事项已提醒
        
        Args:
            todo_id: 待办事项 ID
            
        Returns:
            bool: 标记是否成功
        """
        # 获取待办事项
        todo = self.get_todo(todo_id)
        if not todo:
            return False
        
        # 由于当前模型没有 reminded 字段，我们可以通过完成状态来标记
        # 或者可以在未来扩展模型
        
        return True
    
    def count_todos(self) -> int:
        """
        获取未软删除的待办事项总数
        
        Returns:
            int: 未软删除的待办事项总数
        """
        return len(self.list_todos())
    
    def count_active_todos(self) -> int:
        """
        获取未软删除的待办事项总数（别名）
        
        Returns:
            int: 未软删除的待办事项总数
        """
        return self.count_todos()
    
    def count_deleted_todos(self) -> int:
        """
        获取已软删除的待办事项数量
        
        Returns:
            int: 已软删除的待办事项数量
        """
        return len(self.list_deleted_todos())
    
    def count_pending_todos(self) -> int:
        """
        获取未完成且未软删除的待办事项数量
        
        Returns:
            int: 未完成且未软删除的待办事项数量
        """
        todos = self.list_todos()
        return sum(1 for todo in todos if not todo.done)
    
    def count_completed_todos(self) -> int:
        """
        获取已完成且未软删除的待办事项数量
        
        Returns:
            int: 已完成且未软删除的待办事项数量
        """
        todos = self.list_todos()
        return sum(1 for todo in todos if todo.done)
    
    def clear_completed_todos(self) -> int:
        """
        清除所有已完成的待办事项
        
        Returns:
            int: 清除的数量
        """
        todos = self.list_todos()
        completed_todos = [todo for todo in todos if todo.done]
        
        count = 0
        for todo in completed_todos:
            if self.delete_todo(todo.id):
                count += 1
        
        return count
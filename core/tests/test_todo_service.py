# -*- coding: utf-8 -*-
"""
待办服务单元测试模块

本模块测试 TodoService 的所有业务逻辑方法。
遵循 TDD 原则，先编写测试，再实现功能。

作者：FlowSphere Team
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from core.models.todo import Todo
from core.todo_service import TodoService


class TestTodoService:
    """待办服务测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时测试目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def service(self, temp_dir):
        """创建测试用的 TodoService 实例"""
        return TodoService(data_dir=temp_dir)
    
    @pytest.fixture
    def sample_todos(self, service):
        """创建测试用的待办事项数据"""
        # 活跃的待办
        todo1 = service.create_todo({
            "title": "活跃待办1",
            "description": "这是第一个活跃的待办事项",
            "done": False
        })
        
        # 已完成的待办
        todo2 = service.create_todo({
            "title": "已完成待办",
            "description": "这是已完成的待办事项",
            "done": True
        })
        
        # 带关键字的待办（用于搜索测试）
        todo3 = service.create_todo({
            "title": "可搜索待办",
            "description": "包含关键字 TEST 的待办事项",
            "done": False
        })
        
        # 活跃的待办2
        todo4 = service.create_todo({
            "title": "活跃待办2",
            "description": "这是第二个活跃的待办事项",
            "done": False
        })
        
        return {
            "todo1": todo1,
            "todo2": todo2,
            "todo3": todo3,
            "todo4": todo4
        }
    
    # ==================== 查询类测试 ====================
    
    def test_list_todos_excludes_deleted(self, service, sample_todos):
        """测试 list_todos() 不返回已软删除的待办"""
        # 软删除 todo1
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        # 获取列表
        todos = service.list_todos()
        
        # 验证 todo1 不在列表中
        todo_ids = [t.id for t in todos]
        assert sample_todos["todo1"].id not in todo_ids
        assert sample_todos["todo2"].id in todo_ids
        assert sample_todos["todo3"].id in todo_ids
        assert sample_todos["todo4"].id in todo_ids
    
    def test_list_active_todos(self, service, sample_todos):
        """测试 list_active_todos() 返回未软删除的待办"""
        # 软删除一个待办
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        # 获取活跃列表
        active_todos = service.list_active_todos()
        
        # 验证只返回未软删除的
        assert len(active_todos) == 3
        todo_ids = [t.id for t in active_todos]
        assert sample_todos["todo1"].id not in todo_ids
    
    def test_list_deleted_todos(self, service, sample_todos):
        """测试 list_deleted_todos() 只返回已软删除的待办"""
        # 软删除两个待办
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.soft_delete_todo(sample_todos["todo2"].id)
        
        # 获取已删除列表
        deleted_todos = service.list_deleted_todos()
        
        # 验证只返回已软删除的
        assert len(deleted_todos) == 2
        todo_ids = [t.id for t in deleted_todos]
        assert sample_todos["todo1"].id in todo_ids
        assert sample_todos["todo2"].id in todo_ids
        assert sample_todos["todo3"].id not in todo_ids
    
    def test_list_deleted_todos_empty(self, service):
        """测试回收站为空时返回空列表"""
        deleted_todos = service.list_deleted_todos()
        assert deleted_todos == []
    
    def test_get_todo_exists(self, service, sample_todos):
        """测试 get_todo() 获取存在的待办"""
        todo = service.get_todo(sample_todos["todo1"].id)
        
        assert todo is not None
        assert todo.id == sample_todos["todo1"].id
        assert todo.title == "活跃待办1"
    
    def test_get_todo_not_exists(self, service):
        """测试 get_todo() 获取不存在的待办"""
        todo = service.get_todo("non-existent-id")
        assert todo is None
    
    def test_search_by_description_found(self, service, sample_todos):
        """测试根据 description 搜索到结果"""
        results = service.search_todos_by_description("TEST")
        
        assert len(results) >= 1
        todo_ids = [t.id for t in results]
        assert sample_todos["todo3"].id in todo_ids
    
    def test_search_by_description_not_found(self, service, sample_todos):
        """测试根据 description 搜索无结果"""
        results = service.search_todos_by_description("不存在的关键字")
        assert results == []
    
    def test_search_by_description_empty_keyword(self, service, sample_todos):
        """测试搜索关键字为空时返回所有未软删除的待办"""
        results = service.search_todos_by_description("")
        
        # 应该返回所有未软删除的待办
        assert len(results) == 4
    
    def test_search_by_description_case_insensitive(self, service, sample_todos):
        """测试搜索不区分大小写"""
        results_lower = service.search_todos_by_description("test")
        results_upper = service.search_todos_by_description("TEST")
        results_mixed = service.search_todos_by_description("Test")
        
        # 所有搜索结果应该相同
        assert len(results_lower) == len(results_upper) == len(results_mixed)
    
    def test_search_by_title_found(self, service, sample_todos):
        """测试根据 title 搜索到结果"""
        results = service.search_todos_by_title("活跃")
        
        assert len(results) >= 1
        todo_ids = [t.id for t in results]
        assert sample_todos["todo1"].id in todo_ids
        assert sample_todos["todo4"].id in todo_ids
    
    def test_search_by_title_not_found(self, service, sample_todos):
        """测试根据 title 搜索无结果"""
        results = service.search_todos_by_title("不存在的标题")
        assert results == []
    
    def test_search_by_title_empty_keyword(self, service, sample_todos):
        """测试 title 搜索关键字为空时返回所有未软删除的待办"""
        results = service.search_todos_by_title("")
        assert len(results) == 4
    
    # ==================== 增删改测试 ====================
    
    def test_create_todo_success(self, service):
        """测试创建待办成功"""
        todo = service.create_todo({
            "title": "新待办",
            "description": "新待办的描述"
        })
        
        assert todo is not None
        assert todo.title == "新待办"
        assert todo.description == "新待办的描述"
        assert todo.done is False
        assert todo.is_deleted is False
        
        # 验证存储中存在
        stored_todo = service.get_todo(todo.id)
        assert stored_todo is not None
    
    def test_create_todo_empty_title(self, service):
        """测试创建待办标题为空时抛出异常"""
        with pytest.raises(ValueError, match="待办标题不能为空"):
            service.create_todo({"title": ""})
    
    def test_update_todo_success(self, service, sample_todos):
        """测试更新待办成功"""
        updated = service.update_todo({
            "id": sample_todos["todo1"].id,
            "title": "更新后的标题",
            "description": "更新后的描述"
        })
        
        assert updated is not None
        assert updated.title == "更新后的标题"
        assert updated.description == "更新后的描述"
        
        # 验证存储中已更新
        stored_todo = service.get_todo(sample_todos["todo1"].id)
        assert stored_todo.title == "更新后的标题"
    
    def test_update_todo_not_exists(self, service):
        """测试更新不存在的待办时抛出异常"""
        with pytest.raises(ValueError, match="待办事项不存在"):
            service.update_todo({
                "id": "non-existent-id",
                "title": "更新"
            })
    
    def test_toggle_todo_done(self, service, sample_todos):
        """测试切换待办完成状态"""
        # 初始状态为 False
        assert sample_todos["todo1"].done is False
        
        # 切换一次
        toggled = service.toggle_todo(sample_todos["todo1"].id)
        assert toggled.done is True
        
        # 再切换一次
        toggled = service.toggle_todo(sample_todos["todo1"].id)
        assert toggled.done is False
    
    # ==================== 软删除测试 ====================
    
    def test_soft_delete_todo_success(self, service, sample_todos):
        """测试软删除单个待办成功"""
        result = service.soft_delete_todo(sample_todos["todo1"].id)
        
        assert result is True
        
        # 验证待办已软删除
        todo = service.get_todo(sample_todos["todo1"].id)
        assert todo.is_deleted is True
    
    def test_soft_delete_todo_not_exists(self, service):
        """测试软删除不存在的待办"""
        result = service.soft_delete_todo("non-existent-id")
        assert result is False
    
    def test_soft_delete_todo_not_in_main_list(self, service, sample_todos):
        """测试软删除后待办不在主列表中"""
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        todos = service.list_todos()
        todo_ids = [t.id for t in todos]
        
        assert sample_todos["todo1"].id not in todo_ids
    
    def test_batch_soft_delete(self, service, sample_todos):
        """测试批量软删除"""
        todo_ids = [
            sample_todos["todo1"].id,
            sample_todos["todo2"].id,
            sample_todos["todo3"].id
        ]
        
        count = service.batch_soft_delete(todo_ids)
        
        assert count == 3
        
        # 验证所有待办已软删除
        for todo_id in todo_ids:
            todo = service.get_todo(todo_id)
            assert todo.is_deleted is True
    
    def test_batch_soft_delete_partial(self, service, sample_todos):
        """测试批量软删除部分不存在"""
        todo_ids = [
            sample_todos["todo1"].id,
            "non-existent-id",
            sample_todos["todo3"].id
        ]
        
        count = service.batch_soft_delete(todo_ids)
        
        assert count == 2
    
    def test_batch_soft_delete_empty_list(self, service):
        """测试批量软删除空列表"""
        count = service.batch_soft_delete([])
        assert count == 0
    
    # ==================== 恢复测试 ====================
    
    def test_restore_todo_success(self, service, sample_todos):
        """测试恢复已软删除的待办成功"""
        # 先软删除
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        # 恢复
        result = service.restore_todo(sample_todos["todo1"].id)
        
        assert result is True
        
        # 验证待办已恢复
        todo = service.get_todo(sample_todos["todo1"].id)
        assert todo.is_deleted is False
    
    def test_restore_todo_not_deleted(self, service, sample_todos):
        """测试恢复未软删除的待办"""
        result = service.restore_todo(sample_todos["todo1"].id)
        assert result is False
    
    def test_restore_todo_not_exists(self, service):
        """测试恢复不存在的待办"""
        result = service.restore_todo("non-existent-id")
        assert result is False
    
    def test_restore_todo_back_to_main_list(self, service, sample_todos):
        """测试恢复后待办回到主列表"""
        # 先软删除
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        # 恢复
        service.restore_todo(sample_todos["todo1"].id)
        
        # 验证在主列表中
        todos = service.list_todos()
        todo_ids = [t.id for t in todos]
        assert sample_todos["todo1"].id in todo_ids
    
    def test_batch_restore_todos(self, service, sample_todos):
        """测试批量恢复"""
        # 先软删除
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.soft_delete_todo(sample_todos["todo2"].id)
        
        # 批量恢复
        count = service.batch_restore_todos([
            sample_todos["todo1"].id,
            sample_todos["todo2"].id
        ])
        
        assert count == 2
        
        # 验证已恢复
        todo1 = service.get_todo(sample_todos["todo1"].id)
        todo2 = service.get_todo(sample_todos["todo2"].id)
        assert todo1.is_deleted is False
        assert todo2.is_deleted is False
    
    def test_batch_restore_todos_partial(self, service, sample_todos):
        """测试批量恢复部分不存在"""
        # 先软删除 todo1
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        count = service.batch_restore_todos([
            sample_todos["todo1"].id,
            "non-existent-id"
        ])
        
        assert count == 1
    
    # ==================== 彻底删除测试 ====================
    
    def test_permanent_delete_todo_success(self, service, sample_todos):
        """测试彻底删除已软删除的待办成功"""
        # 先软删除
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        # 彻底删除
        result = service.permanent_delete_todo(sample_todos["todo1"].id)
        
        assert result is True
        
        # 验证存储中不存在
        todo = service.get_todo(sample_todos["todo1"].id)
        assert todo is None
    
    def test_permanent_delete_todo_not_deleted(self, service, sample_todos):
        """测试彻底删除未软删除的待办"""
        result = service.permanent_delete_todo(sample_todos["todo1"].id)
        assert result is False
    
    def test_permanent_delete_todo_not_exists(self, service):
        """测试彻底删除不存在的待办"""
        result = service.permanent_delete_todo("non-existent-id")
        assert result is False
    
    def test_batch_permanent_delete(self, service, sample_todos):
        """测试批量彻底删除"""
        # 先软删除
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.soft_delete_todo(sample_todos["todo2"].id)
        
        # 批量彻底删除
        count = service.batch_permanent_delete([
            sample_todos["todo1"].id,
            sample_todos["todo2"].id
        ])
        
        assert count == 2
        
        # 验证存储中不存在
        todo1 = service.get_todo(sample_todos["todo1"].id)
        todo2 = service.get_todo(sample_todos["todo2"].id)
        assert todo1 is None
        assert todo2 is None
    
    def test_batch_permanent_delete_partial(self, service, sample_todos):
        """测试批量彻底删除部分不存在"""
        # 先软删除 todo1
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        count = service.batch_permanent_delete([
            sample_todos["todo1"].id,
            "non-existent-id"
        ])
        
        assert count == 1
    
    def test_clear_recycle_bin(self, service, sample_todos):
        """测试清空回收站"""
        # 先软删除
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.soft_delete_todo(sample_todos["todo2"].id)
        
        # 清空回收站
        count = service.clear_recycle_bin()
        
        assert count == 2
        
        # 验证回收站为空
        deleted_todos = service.list_deleted_todos()
        assert len(deleted_todos) == 0
    
    def test_clear_recycle_bin_empty(self, service):
        """测试回收站为空时清空"""
        count = service.clear_recycle_bin()
        assert count == 0
    
    # ==================== 统计测试 ====================
    
    def test_count_todos_excludes_deleted(self, service, sample_todos):
        """测试 count_todos() 不统计已软删除的待办"""
        initial_count = service.count_todos()
        
        # 软删除一个
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        # 验证计数减少
        new_count = service.count_todos()
        assert new_count == initial_count - 1
    
    def test_count_active_todos(self, service, sample_todos):
        """测试 count_active_todos() 返回未软删除的待办数量"""
        active_count = service.count_active_todos()
        total_count = service.count_todos()
        
        assert active_count == total_count
    
    def test_count_deleted_todos(self, service, sample_todos):
        """测试 count_deleted_todos() 返回已软删除的待办数量"""
        # 初始为 0
        assert service.count_deleted_todos() == 0
        
        # 软删除一个
        service.soft_delete_todo(sample_todos["todo1"].id)
        
        # 验证计数为 1
        assert service.count_deleted_todos() == 1
        
        # 再软删除一个
        service.soft_delete_todo(sample_todos["todo2"].id)
        
        # 验证计数为 2
        assert service.count_deleted_todos() == 2
    
    def test_count_pending_todos(self, service, sample_todos):
        """测试 count_pending_todos() 统计未完成且未软删除的待办"""
        pending_count = service.count_pending_todos()
        
        # 验证只统计未完成的
        assert pending_count == 3  # todo1, todo3, todo4 未完成
    
    def test_count_completed_todos(self, service, sample_todos):
        """测试 count_completed_todos() 统计已完成且未软删除的待办"""
        completed_count = service.count_completed_todos()
        
        # 验证只统计已完成的
        assert completed_count == 1  # todo2 已完成

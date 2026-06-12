# -*- coding: utf-8 -*-
"""
待办服务单元测试模块

本模块测试 TodoService 的所有业务逻辑方法。

作者：FlowSphere Team
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from core.models.todo import Todo
from core.services.todo_service import TodoService


@pytest.fixture
def temp_dir():
    """创建临时测试目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def service(temp_dir):
    """创建测试用的 TodoService 实例"""
    return TodoService(data_dir=temp_dir)


@pytest.fixture
def sample_todos(service):
    """创建测试用的待办事项数据"""
    todo1 = service.create_todo({
        "description": "这是第一个活跃的待办事项",
        "done": False
    })

    todo2 = service.create_todo({
        "description": "这是已完成的待办事项",
        "done": True
    })

    todo3 = service.create_todo({
        "description": "包含关键字 TEST 的待办事项",
        "done": False
    })

    todo4 = service.create_todo({
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


class TestListTodos:
    """list_todos 相关测试"""

    def test_excludes_deleted(self, service, sample_todos):
        """测试 list_todos() 不返回已软删除的待办"""
        service.soft_delete_todo(sample_todos["todo1"].id)
        todos = service.list_todos()
        todo_ids = [t.id for t in todos]

        assert sample_todos["todo1"].id not in todo_ids
        assert sample_todos["todo2"].id in todo_ids
        assert sample_todos["todo3"].id in todo_ids
        assert sample_todos["todo4"].id in todo_ids

    def test_list_active_todos(self, service, sample_todos):
        """测试 list_active_todos() 返回未软删除的待办"""
        service.soft_delete_todo(sample_todos["todo1"].id)
        active_todos = service.list_active_todos()

        assert len(active_todos) == 3
        todo_ids = [t.id for t in active_todos]
        assert sample_todos["todo1"].id not in todo_ids

    def test_list_deleted_todos(self, service, sample_todos):
        """测试 list_deleted_todos() 只返回已软删除的待办"""
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.soft_delete_todo(sample_todos["todo2"].id)
        deleted_todos = service.list_deleted_todos()

        assert len(deleted_todos) == 2
        todo_ids = [t.id for t in deleted_todos]
        assert sample_todos["todo1"].id in todo_ids
        assert sample_todos["todo2"].id in todo_ids
        assert sample_todos["todo3"].id not in todo_ids

    def test_list_deleted_todos_empty(self, service):
        """测试回收站为空时返回空列表"""
        deleted_todos = service.list_deleted_todos()
        assert deleted_todos == []


class TestGetTodo:
    """get_todo 相关测试"""

    def test_get_todo_exists(self, service, sample_todos):
        """测试 get_todo() 获取存在的待办"""
        todo = service.get_todo(sample_todos["todo1"].id)

        assert todo is not None
        assert todo.id == sample_todos["todo1"].id
        assert todo.description == "这是第一个活跃的待办事项"

    def test_get_todo_not_exists(self, service):
        """测试 get_todo() 获取不存在的待办"""
        todo = service.get_todo("non-existent-id")
        assert todo is None


class TestSearchTodos:
    """搜索相关测试"""

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
        assert len(results) == 4

    def test_search_by_description_case_insensitive(self, service, sample_todos):
        """测试搜索不区分大小写"""
        results_lower = service.search_todos_by_description("test")
        results_upper = service.search_todos_by_description("TEST")
        results_mixed = service.search_todos_by_description("Test")

        assert len(results_lower) == len(results_upper) == len(results_mixed)


# ==================== 增删改测试 ====================


class TestCreateTodo:
    """create_todo 相关测试"""

    def test_create_todo_success(self, service):
        """测试创建待办成功"""
        todo = service.create_todo({
            "description": "新待办的描述"
        })

        assert todo is not None
        assert todo.description == "新待办的描述"
        assert todo.done is False
        assert todo.is_deleted is False

        stored_todo = service.get_todo(todo.id)
        assert stored_todo is not None

    def test_create_todo_empty_description(self, service):
        """测试创建待办描述为空时抛出异常"""
        with pytest.raises(ValueError, match="待办描述不能为空"):
            service.create_todo({"description": ""})


class TestUpdateTodo:
    """update_todo 相关测试"""

    def test_update_todo_success(self, service, sample_todos):
        """测试更新待办成功"""
        updated = service.update_todo({
            "id": sample_todos["todo1"].id,
            "description": "更新后的描述"
        })

        assert updated is not None
        assert updated.description == "更新后的描述"

        stored_todo = service.get_todo(sample_todos["todo1"].id)
        assert stored_todo.description == "更新后的描述"

    def test_update_todo_not_exists(self, service):
        """测试更新不存在的待办时抛出异常"""
        with pytest.raises(ValueError, match="待办事项不存在"):
            service.update_todo({
                "id": "non-existent-id",
                "description": "更新"
            })


class TestToggleTodo:
    """toggle_todo 相关测试"""

    def test_toggle_todo_done(self, service, sample_todos):
        """测试切换待办完成状态"""
        assert sample_todos["todo1"].done is False

        toggled = service.toggle_todo(sample_todos["todo1"].id)
        assert toggled.done is True

        toggled = service.toggle_todo(sample_todos["todo1"].id)
        assert toggled.done is False


# ==================== 软删除测试 ====================


class TestSoftDelete:
    """软删除相关测试"""

    def test_soft_delete_todo_success(self, service, sample_todos):
        """测试软删除单个待办成功"""
        result = service.soft_delete_todo(sample_todos["todo1"].id)

        assert result is True

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


class TestRestore:
    """恢复相关测试"""

    def test_restore_todo_success(self, service, sample_todos):
        """测试恢复已软删除的待办成功"""
        service.soft_delete_todo(sample_todos["todo1"].id)
        result = service.restore_todo(sample_todos["todo1"].id)

        assert result is True

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
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.restore_todo(sample_todos["todo1"].id)

        todos = service.list_todos()
        todo_ids = [t.id for t in todos]
        assert sample_todos["todo1"].id in todo_ids

    def test_batch_restore_todos(self, service, sample_todos):
        """测试批量恢复"""
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.soft_delete_todo(sample_todos["todo2"].id)

        count = service.batch_restore_todos([
            sample_todos["todo1"].id,
            sample_todos["todo2"].id
        ])

        assert count == 2

        todo1 = service.get_todo(sample_todos["todo1"].id)
        todo2 = service.get_todo(sample_todos["todo2"].id)
        assert todo1.is_deleted is False
        assert todo2.is_deleted is False

    def test_batch_restore_todos_partial(self, service, sample_todos):
        """测试批量恢复部分不存在"""
        service.soft_delete_todo(sample_todos["todo1"].id)

        count = service.batch_restore_todos([
            sample_todos["todo1"].id,
            "non-existent-id"
        ])

        assert count == 1


# ==================== 彻底删除测试 ====================


class TestPermanentDelete:
    """彻底删除相关测试"""

    def test_permanent_delete_todo_success(self, service, sample_todos):
        """测试彻底删除已软删除的待办成功"""
        service.soft_delete_todo(sample_todos["todo1"].id)
        result = service.permanent_delete_todo(sample_todos["todo1"].id)

        assert result is True

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
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.soft_delete_todo(sample_todos["todo2"].id)

        count = service.batch_permanent_delete([
            sample_todos["todo1"].id,
            sample_todos["todo2"].id
        ])

        assert count == 2

        todo1 = service.get_todo(sample_todos["todo1"].id)
        todo2 = service.get_todo(sample_todos["todo2"].id)
        assert todo1 is None
        assert todo2 is None

    def test_batch_permanent_delete_partial(self, service, sample_todos):
        """测试批量彻底删除部分不存在"""
        service.soft_delete_todo(sample_todos["todo1"].id)

        count = service.batch_permanent_delete([
            sample_todos["todo1"].id,
            "non-existent-id"
        ])

        assert count == 1

    def test_clear_recycle_bin(self, service, sample_todos):
        """测试清空回收站"""
        service.soft_delete_todo(sample_todos["todo1"].id)
        service.soft_delete_todo(sample_todos["todo2"].id)

        count = service.clear_recycle_bin()

        assert count == 2

        deleted_todos = service.list_deleted_todos()
        assert len(deleted_todos) == 0

    def test_clear_recycle_bin_empty(self, service):
        """测试回收站为空时清空"""
        count = service.clear_recycle_bin()
        assert count == 0


# ==================== 统计测试 ====================


class TestCount:
    """统计相关测试"""

    def test_count_todos_excludes_deleted(self, service, sample_todos):
        """测试 count_todos() 不统计已软删除的待办"""
        initial_count = service.count_todos()

        service.soft_delete_todo(sample_todos["todo1"].id)

        new_count = service.count_todos()
        assert new_count == initial_count - 1

    def test_count_active_todos(self, service, sample_todos):
        """测试 count_active_todos() 返回未软删除的待办数量"""
        active_count = service.count_active_todos()
        total_count = service.count_todos()

        assert active_count == total_count

    def test_count_deleted_todos(self, service, sample_todos):
        """测试 count_deleted_todos() 返回已软删除的待办数量"""
        assert service.count_deleted_todos() == 0

        service.soft_delete_todo(sample_todos["todo1"].id)
        assert service.count_deleted_todos() == 1

        service.soft_delete_todo(sample_todos["todo2"].id)
        assert service.count_deleted_todos() == 2

    def test_count_pending_todos(self, service, sample_todos):
        """测试 count_pending_todos() 统计未完成且未软删除的待办"""
        pending_count = service.count_pending_todos()
        assert pending_count == 3

    def test_count_completed_todos(self, service, sample_todos):
        """测试 count_completed_todos() 统计已完成且未软删除的待办"""
        completed_count = service.count_completed_todos()
        assert completed_count == 1

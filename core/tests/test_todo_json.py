# -*- coding: utf-8 -*-
"""
JSON 存储单元测试模块

本模块测试 JsonStorage 的所有文件读写操作。

作者：FlowSphere Team
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from core.models.todo import Todo
from core.storage.json_storage import JsonStorage


@pytest.fixture
def temp_dir():
    """创建临时测试目录"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_data_dir(temp_dir):
    """创建测试数据目录"""
    test_data_dir = temp_dir / "test_data"
    test_data_dir.mkdir()
    return test_data_dir


@pytest.fixture
def test_todo_file(test_data_dir):
    """测试用的 JSON 文件路径"""
    return test_data_dir / "todo.json"


@pytest.fixture
def storage(test_todo_file):
    """创建测试用的 JsonStorage 实例"""
    return JsonStorage(str(test_todo_file))


@pytest.fixture
def sample_data():
    """测试用的样本数据"""
    return [
        {
            "id": "test-001",
            "description": "这是一个测试待办",
            "notification": "2026-06-15T17:30",
            "repeat": "none",
            "done": False,
            "is_deleted": False,
            "created_at": "2026-06-10T09:00"
        },
        {
            "id": "test-002",
            "description": "这是另一个测试待办",
            "notification": "2026-06-12T16:30",
            "repeat": "weekly",
            "done": True,
            "is_deleted": False,
            "created_at": "2026-06-01T10:00"
        }
    ]


@pytest.fixture
def initialized_storage(storage, sample_data):
    """初始化数据的存储实例"""
    storage.write(sample_data)
    return storage


# ==================== 读取测试 ====================


class TestRead:
    """读取操作测试"""

    def test_read_json(self, initialized_storage):
        """测试读取 JSON 文件"""
        data = initialized_storage.read()

        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0]['id'] == 'test-001'
        assert data[1]['id'] == 'test-002'

    def test_read_nonexistent_file(self, temp_dir):
        """测试读取不存在的文件"""
        nonexistent_storage = JsonStorage(str(temp_dir / "nonexistent.json"))
        data = nonexistent_storage.read()

        assert isinstance(data, list)
        assert len(data) == 0


# ==================== 写入测试 ====================


class TestWrite:
    """写入操作测试"""

    def test_write_json(self, storage):
        """测试写入 JSON 文件"""
        new_data = [
            {"id": "new-001", "description": "新待办1", "done": False},
            {"id": "new-002", "description": "新待办2", "done": True}
        ]

        success = storage.write(new_data)

        assert success is True
        data = storage.read()
        assert len(data) == 2
        assert data[0]['id'] == 'new-001'
        assert data[1]['id'] == 'new-002'

    def test_write_creates_directory(self, temp_dir):
        """测试写入时自动创建目录"""
        new_dir = temp_dir / "new_dir"
        new_storage = JsonStorage(str(new_dir / "todo.json"))

        success = new_storage.write([{"id": "test", "description": "test"}])

        assert success is True
        assert new_dir.exists()
        assert (new_dir / "todo.json").exists()


# ==================== 追加测试 ====================


class TestAppend:
    """追加操作测试"""

    def test_append_json(self, initialized_storage):
        """测试追加 JSON 数据"""
        new_item = {"id": "append-001", "description": "追加的待办", "done": False}
        success = initialized_storage.append(new_item)

        assert success is True
        data = initialized_storage.read()
        assert len(data) == 3
        assert data[2]['id'] == 'append-001'


# ==================== 更新测试 ====================


class TestUpdate:
    """更新操作测试"""

    def test_update_json(self, initialized_storage):
        """测试更新 JSON 数据"""
        updated_item = {
            "id": "test-001",
            "description": "更新后的待办",
            "done": True
        }
        success = initialized_storage.update(updated_item)

        assert success is True
        data = initialized_storage.read()
        assert data[0]['description'] == '更新后的待办'
        assert data[0]['done'] is True


# ==================== 删除测试 ====================


class TestDelete:
    """删除操作测试"""

    def test_delete_json(self, initialized_storage):
        """测试删除 JSON 数据"""
        success = initialized_storage.delete("test-001")

        assert success is True
        data = initialized_storage.read()
        assert len(data) == 1
        assert data[0]['id'] == 'test-002'

    def test_soft_delete_json(self, initialized_storage):
        """测试软删除 JSON 数据"""
        success = initialized_storage.soft_delete("test-001")

        assert success is True
        data = initialized_storage.read()
        assert len(data) == 2

        deleted_item = next(item for item in data if item['id'] == 'test-001')
        assert deleted_item['is_deleted'] is True

        active_item = next(item for item in data if item['id'] == 'test-002')
        assert active_item['is_deleted'] is False


# ==================== 统计测试 ====================


class TestCount:
    """统计操作测试"""

    def test_count_json(self, initialized_storage):
        """测试计算 JSON 数据条数"""
        count = initialized_storage.count()
        assert count == 2


# ==================== 文件存在测试 ====================


class TestExists:
    """文件存在检查测试"""

    def test_exists_json(self, initialized_storage, test_todo_file):
        """测试检查 JSON 文件是否存在"""
        exists = initialized_storage.exists()
        assert exists is True

        test_todo_file.unlink()
        exists = initialized_storage.exists()
        assert exists is False


# ==================== 损坏文件测试 ====================


class TestCorruptedFile:
    """损坏文件处理测试"""

    def test_write_invalid_json_file(self, storage, test_todo_file):
        """测试读取损坏的 JSON 文件"""
        with open(test_todo_file, 'w', encoding='utf-8') as f:
            f.write("这不是有效的JSON内容")

        data = storage.read()

        assert isinstance(data, list)
        assert len(data) == 0

        backup_file = test_todo_file.with_suffix('.json.corrupted')
        assert backup_file.exists()


# ==================== 数据格式测试 ====================


class TestDataFormat:
    """数据格式保持测试"""

    def test_write_preserves_format(self, storage):
        """测试写入保持数据格式"""
        todo = Todo(
            id="format-test-001",
            description="测试数据格式",
            notification="2026-06-15T17:30",
            repeat="daily",
            done=False,
            created_at="2026-06-10T09:00"
        )

        data = [todo.to_dict()]
        storage.write(data)

        loaded_data = storage.read()
        restored_todo = Todo.from_dict(loaded_data[0])

        assert restored_todo.id == todo.id
        assert restored_todo.description == todo.description
        assert restored_todo.notification == todo.notification
        assert restored_todo.repeat == todo.repeat
        assert restored_todo.done == todo.done
        assert restored_todo.is_deleted == todo.is_deleted
        assert restored_todo.created_at == todo.created_at


# ==================== 多操作测试 ====================


class TestMultipleOperations:
    """连续多操作测试"""

    def test_multiple_operations(self, initialized_storage):
        """测试多次操作"""
        initialized_storage.append({"id": "multi-001", "description": "多操作测试1"})
        assert initialized_storage.count() == 3

        initialized_storage.update({"id": "test-001", "description": "已更新"})
        data = initialized_storage.read()
        assert data[0]['description'] == '已更新'

        initialized_storage.delete("test-002")
        assert initialized_storage.count() == 2

        initialized_storage.write([{"id": "final-001", "description": "最终数据"}])
        assert initialized_storage.count() == 1

        data = initialized_storage.read()
        assert data[0]['id'] == 'final-001'

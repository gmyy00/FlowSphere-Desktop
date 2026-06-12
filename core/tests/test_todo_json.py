# -*- coding: utf-8 -*-
"""
Storage JSON 读写测试模块

本模块测试 storage.json_storage 模块的 JSON 文件读写功能。
测试确保每次测试后数据能够恢复原状。

测试内容：
1. JsonStorage 类的基本功能
2. JSON 文件读取
3. JSON 文件写入
4. 数据追加操作
5. 数据更新操作
6. 数据删除操作
7. 空文件和损坏文件的处理
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.todo import Todo
from storage import JsonStorage


class TestJsonStorage(unittest.TestCase):
    """JsonStorage 测试类"""
    
    def setUp(self):
        """
        测试前准备
        
        创建临时目录和测试数据，确保测试环境独立
        """
        # 创建临时目录
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # 创建测试数据目录
        self.test_data_dir = self.temp_dir / "test_data"
        self.test_data_dir.mkdir()
        
        # 测试用的 JSON 文件
        self.test_todo_file = self.test_data_dir / "todo.json"
        
        # 创建 JsonStorage 实例
        self.storage = JsonStorage(str(self.test_todo_file))
        
        # 创建测试数据
        self.test_data = [
            {
                "id": "test-001",
                "title": "测试待办1",
                "description": "这是一个测试待办",
                "notification": "2026-06-15T17:30",
                "repeat": "none",
                "done": False,
                "is_deleted": False,
                "created_at": "2026-06-10T09:00"
            },
            {
                "id": "test-002",
                "title": "测试待办2",
                "description": "这是另一个测试待办",
                "notification": "2026-06-12T16:30",
                "repeat": "weekly",
                "done": True,
                "is_deleted": False,
                "created_at": "2026-06-01T10:00"
            }
        ]
        
        # 写入测试数据
        self.storage.write(self.test_data)
    
    def tearDown(self):
        """
        测试后清理
        
        删除临时目录和所有测试文件
        """
        # 删除临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_read_json(self):
        """
        测试读取 JSON 文件
        
        验证能够正确读取 JSON 文件并返回数据
        """
        # 读取数据
        data = self.storage.read()
        
        # 验证数据
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 'test-001')
        self.assertEqual(data[1]['id'], 'test-002')
    
    def test_write_json(self):
        """
        测试写入 JSON 文件
        
        验证能够将数据写入 JSON 文件
        """
        # 创建新数据
        new_data = [
            {"id": "new-001", "title": "新待办1", "done": False},
            {"id": "new-002", "title": "新待办2", "done": True}
        ]
        
        # 写入数据
        success = self.storage.write(new_data)
        
        # 验证写入成功
        self.assertTrue(success)
        
        # 读取并验证
        data = self.storage.read()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], 'new-001')
        self.assertEqual(data[1]['id'], 'new-002')
    
    def test_append_json(self):
        """
        测试追加 JSON 数据
        
        验证能够向 JSON 文件追加数据
        """
        # 追加新数据
        new_item = {"id": "append-001", "title": "追加的待办", "done": False}
        success = self.storage.append(new_item)
        
        # 验证追加成功
        self.assertTrue(success)
        
        # 读取并验证
        data = self.storage.read()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[2]['id'], 'append-001')
    
    def test_update_json(self):
        """
        测试更新 JSON 数据
        
        验证能够更新 JSON 文件中的数据
        """
        # 更新数据
        updated_item = {
            "id": "test-001",
            "title": "更新后的待办",
            "done": True
        }
        success = self.storage.update(updated_item)
        
        # 验证更新成功
        self.assertTrue(success)
        
        # 读取并验证
        data = self.storage.read()
        self.assertEqual(data[0]['title'], '更新后的待办')
        self.assertTrue(data[0]['done'])
    
    def test_delete_json(self):
        """
        测试删除 JSON 数据
        
        验证能够从 JSON 文件中删除数据
        """
        # 删除数据
        success = self.storage.delete("test-001")
        
        # 验证删除成功
        self.assertTrue(success)
        
        # 读取并验证
        data = self.storage.read()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 'test-002')
    
    def test_soft_delete_json(self):
        """
        测试软删除 JSON 数据
        
        验证能够将数据标记为已删除而不是真正删除
        """
        # 软删除数据
        success = self.storage.soft_delete("test-001")
        
        # 验证软删除成功
        self.assertTrue(success)
        
        # 读取并验证
        data = self.storage.read()
        self.assertEqual(len(data), 2)
        
        # 验证被软删除的数据
        deleted_item = next(item for item in data if item['id'] == 'test-001')
        self.assertTrue(deleted_item['is_deleted'])
        
        # 验证未被软删除的数据
        active_item = next(item for item in data if item['id'] == 'test-002')
        self.assertFalse(active_item['is_deleted'])
    
    def test_count_json(self):
        """
        测试计算 JSON 数据条数
        
        验证能够正确计算数据条数
        """
        # 计算条数
        count = self.storage.count()
        
        # 验证条数
        self.assertEqual(count, 2)
    
    def test_exists_json(self):
        """
        测试检查 JSON 文件是否存在
        
        验证能够正确检查文件是否存在
        """
        # 检查文件存在
        exists = self.storage.exists()
        self.assertTrue(exists)
        
        # 删除文件后检查
        self.test_todo_file.unlink()
        exists = self.storage.exists()
        self.assertFalse(exists)
    
    def test_read_nonexistent_file(self):
        """
        测试读取不存在的文件
        
        验证读取不存在的文件时返回空列表
        """
        # 创建指向不存在文件的 storage
        nonexistent_storage = JsonStorage(str(self.temp_dir / "nonexistent.json"))
        
        # 读取并验证
        data = nonexistent_storage.read()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
    
    def test_write_creates_directory(self):
        """
        测试写入时自动创建目录
        
        验证写入文件时如果目录不存在会自动创建
        """
        # 创建指向不存在目录的 storage
        new_dir = self.temp_dir / "new_dir"
        new_storage = JsonStorage(str(new_dir / "todo.json"))
        
        # 写入数据
        success = new_storage.write([{"id": "test", "title": "test"}])
        
        # 验证写入成功
        self.assertTrue(success)
        self.assertTrue(new_dir.exists())
        self.assertTrue((new_dir / "todo.json").exists())
    
    def test_write_invalid_json_file(self):
        """
        测试读取损坏的 JSON 文件
        
        验证读取损坏的 JSON 文件时返回空列表
        """
        # 写入无效的 JSON 内容
        with open(self.test_todo_file, 'w', encoding='utf-8') as f:
            f.write("这不是有效的JSON内容")
        
        # 读取并验证
        data = self.storage.read()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)
        
        # 验证备份文件被创建
        backup_file = self.test_todo_file.with_suffix('.json.corrupted')
        self.assertTrue(backup_file.exists())
    
    def test_write_preserves_format(self):
        """
        测试写入保持数据格式
        
        验证写入的数据格式与原始数据一致
        """
        # 创建 Todo 对象
        todo = Todo(
            id="format-test-001",
            title="格式测试",
            description="测试数据格式",
            notification="2026-06-15T17:30",
            repeat="daily",
            done=False,
            created_at="2026-06-10T09:00"
        )
        
        # 转换为字典并写入
        data = [todo.to_dict()]
        self.storage.write(data)
        
        # 读取并转换为 Todo 对象
        loaded_data = self.storage.read()
        restored_todo = Todo.from_dict(loaded_data[0])
        
        # 验证数据完整性
        self.assertEqual(restored_todo.id, todo.id)
        self.assertEqual(restored_todo.title, todo.title)
        self.assertEqual(restored_todo.description, todo.description)
        self.assertEqual(restored_todo.notification, todo.notification)
        self.assertEqual(restored_todo.repeat, todo.repeat)
        self.assertEqual(restored_todo.done, todo.done)
        self.assertEqual(restored_todo.is_deleted, todo.is_deleted)
        self.assertEqual(restored_todo.created_at, todo.created_at)
    
    def test_multiple_operations(self):
        """
        测试多次操作
        
        验证连续进行多次读写操作的正确性
        """
        # 1. 追加数据
        self.storage.append({"id": "multi-001", "title": "多操作测试1"})
        self.assertEqual(self.storage.count(), 3)
        
        # 2. 更新数据
        self.storage.update({"id": "test-001", "title": "已更新"})
        data = self.storage.read()
        self.assertEqual(data[0]['title'], '已更新')
        
        # 3. 删除数据
        self.storage.delete("test-002")
        self.assertEqual(self.storage.count(), 2)
        
        # 4. 写入新数据
        self.storage.write([{"id": "final-001", "title": "最终数据"}])
        self.assertEqual(self.storage.count(), 1)
        
        # 5. 验证最终状态
        data = self.storage.read()
        self.assertEqual(data[0]['id'], 'final-001')


if __name__ == '__main__':
    unittest.main()
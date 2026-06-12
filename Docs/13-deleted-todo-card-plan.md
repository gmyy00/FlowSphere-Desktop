# DeletedTodoCard 实现计划

## 目标

创建已删除待办事项卡片组件，显示在回收站窗口中，支持恢复和永久删除功能。

## 文件变更

### 1. 新建文件

| 文件 | 说明 |
|------|------|
| `ui/deleted_todo_card.py` | 已删除待办事项卡片组件 |

### 2. 修改文件

| 文件 | 修改内容 |
|------|----------|
| `ui/style.qss` | 添加恢复按钮和永久删除按钮样式 |
| `ui/recycle_bin.py` | 集成 TodoService + DeletedTodoCard，加载已删除待办事项 |

## 组件设计

### DeletedTodoCard

与 TodoCard 相同的部分：
- 显示 description、notification、repeat
- 使用相同卡片样式 `#todo_card`

与 TodoCard 不同的部分：
- 无复选框
- 无编辑按钮
- 有恢复按钮（restore.png）
- 有永久删除按钮（purge.png）

### 信号

| 信号 | 说明 |
|------|------|
| todo_recovered(str) | 恢复待办事项，传递 todo_id |
| todo_permanently_deleted(str) | 永久删除待办事项，传递 todo_id |

### QSS 样式

```css
/* Restore button */
#todo_restore_btn {
    background: transparent;
    border: none;
}

#todo_restore_btn:hover {
    background-color: #d4c9b8;
    border-radius: 4px;
}

/* Purge button */
#todo_purge_btn {
    background: transparent;
    border: none;
}

#todo_purge_btn:hover {
    background-color: #e0c8c0;
    border-radius: 4px;
}
```

## RecycleBinWindow 变更

- 导入 TodoService、DeletedTodoCard
- 初始化 TodoService（指向 data 目录）
- 添加 QScrollArea + QVBoxLayout 显示已删除待办事项
- 处理恢复信号：调用 service.restore_todo()，移除卡片
- 处理永久删除信号：调用 service.permanent_delete_todo()，移除卡片

# Todo Card 动态布局修复计划

## 问题描述

1. **缺少滚动条**：当前代码设置了 `ScrollBarAlwaysOff`，无法通过滚动条切换 todo
2. **卡片尺寸写死**：`TodoCard` 设置了 `setFixedHeight(70)`，高度不随内容变化
3. **滚动条样式默认**：使用系统默认样式，与米色主题不匹配

## 修复方案

### 1. 修改 `ui/todo_card.py`

- 移除 `setFixedHeight(70)`，让卡片高度自适应内容
- 移除固定宽度约束，让卡片填充父容器宽度
- 使用 `QSizePolicy.Expanding` 策略

### 2. 修改 `ui/main_window.py`

- 将 `todo_scroll` 的 `ScrollBarAlwaysOff` 改为 `ScrollBarAsNeeded`
- 设置 `QListWidget` 的宽度策略为 `Expanding`

### 3. 添加滚动条样式到 `ui/style.qss`

添加以下样式（无需额外素材，纯 QSS 实现）：

```css
/* Scrollbar track */
QScrollBar:vertical {
    background: #ebe5da;
    width: 8px;
    border-radius: 4px;
    margin: 0;
}

/* Scrollbar handle (thumb) */
QScrollBar::handle:vertical {
    background: #d4c9b8;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #b0a090;
}

/* Hide up/down arrows */
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Hide scrollbar background when not needed */
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}
```

## 预期效果

- 卡片高度随内容（文字行数）动态变化
- 卡片宽度随主窗口宽度动态变化
- 出现米色主题风格的滚动条
- 滚动条仅在内容超出时显示（`AsNeeded`）

## 需要修改的文件

| 文件 | 修改内容 |
|------|----------|
| `ui/todo_card.py` | 移除固定高度，添加尺寸策略 |
| `ui/main_window.py` | 启用滚动条，调整宽度策略 |
| `ui/style.qss` | 添加滚动条样式 |

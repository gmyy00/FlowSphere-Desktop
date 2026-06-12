# 数据模型设计

## 1. 设计理念

**统一模型**：所有日程本质上都是待办事项，日程是定时重复的待办。
因此本项目只保留一个核心数据模型 `Todo`，不再单独定义 Schedule。

## 2. Todo 数据模型

### 2.1 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识符，使用 UUID v4 生成 |
| `title` | string | 是 | 待办标题 |
| `description` | string | 否 | 待办的文字描述 |
| `deadline` | string (ISO 8601) | 否 | 截止时间，精确到分钟，格式：`YYYY-MM-DDTHH:MM` |
| `notification` | string (ISO 8601) | 否 | 提醒时间，精确到分钟，格式：`YYYY-MM-DDTHH:MM` |
| `repeat` | enum | 否 | 重复规则（见 2.2） |
| `done` | boolean | 是 | 完成状态，默认 `false` |
| `created_at` | string (ISO 8601) | 是 | 创建时间，格式：`YYYY-MM-DDTHH:MM` |

### 2.2 Repeat 重复规则枚举

| 值 | 说明 |
|----|------|
| `none` | 不重复（默认） |
| `yearly` | 每年重复 |
| `monthly` | 每月重复 |
| `weekly` | 每周重复 |
| `weekdays` | 工作日重复（周一至周五） |
| `daily` | 每日重复 |

### 2.3 展示文本生成规则（业务逻辑）

展示文本由业务层根据 `notification` 和 `repeat` 字段组合生成：

**输入**：
- `notification`: `2026-06-11T22:16`（星期四）
- `repeat`: `weekly`

**输出**：`每周星期四22:16`

**示例**：

| notification | repeat | 展示文本 |
|--------------|--------|----------|
| `2026-06-11T22:16` | `none` | 2026年6月11日星期四22:16 |
| `2026-06-11T22:16` | `daily` | 每天22:16 |
| `2026-06-11T22:16` | `weekdays` | 每个工作日22:16 |
| `2026-06-11T22:16` | `weekly` | 每周星期四22:16 |
| `2026-06-11T22:16` | `monthly` | 每月11日22:16 |
| `2026-06-11T22:16` | `yearly` | 每年6月11日22:16 |

## 3. 数据示例

### 3.1 单次待办（无重复）

```json
{
  "id": "todo-001",
  "title": "完成项目文档",
  "description": "需要完成项目的设计文档和用户手册",
  "deadline": "2026-06-15T18:00",
  "notification": "2026-06-15T17:30",
  "repeat": "none",
  "done": false,
  "created_at": "2026-06-10T09:00"
}
```

### 3.2 每日重复待办

```json
{
  "id": "todo-002",
  "title": "每日英语打卡",
  "description": "学习30分钟英语",
  "deadline": "2026-06-11T23:59",
  "notification": "2026-06-11T20:00",
  "repeat": "daily",
  "done": false,
  "created_at": "2026-05-01T08:00"
}
```

### 3.3 每周重复日程

```json
{
  "id": "todo-003",
  "title": "周会",
  "description": "部门周会，汇报本周工作",
  "deadline": "2026-06-12T14:00",
  "notification": "2026-06-12T13:50",
  "repeat": "weekly",
  "done": false,
  "created_at": "2026-05-01T10:00"
}
```

### 3.4 工作日站会

```json
{
  "id": "todo-004",
  "title": "工作日站会",
  "description": "每日站会，同步工作进度",
  "deadline": "2026-06-11T09:30",
  "notification": "2026-06-11T09:00",
  "repeat": "weekdays",
  "done": false,
  "created_at": "2026-04-01T09:00"
}
```

## 4. 行为规则

### 4.1 完成状态

- `done = false` 时，按 `repeat` 规则触发系统通知提醒
- 标记为 `done = true` 后停止提醒
- 逾期未完成的任务在 UI 中高亮显示

### 4.2 重复规则

- `repeat` 定义任务的重复频率
- `notification` 定义具体的提醒时间
- 应用层负责将两个字段组合生成展示文本

### 4.3 日程行为

- 无"完成"概念，时间过后保留但视觉淡化显示
- 重复规则按周期生成下一个实例
- 不进行冲突检测

## 5. 存储格式

### 5.1 文件结构

```
data/
└── todos.json
```

### 5.2 JSON 格式

```json
[
  { "id": "...", "title": "...", ... },
  { "id": "...", "title": "...", ... }
]
```
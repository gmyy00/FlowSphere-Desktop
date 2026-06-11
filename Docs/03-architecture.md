# 技术架构与项目结构

## 1. 一期技术栈

| 类别 | 技术 | 说明 |
|---|---|---|
| 编程语言 | Python 3.10+ | 开发效率高，适合桌面 Demo |
| UI 框架 | PySide6 | Qt 官方 Python 绑定 |
| 数据存储 | JSON 文件 | 一期足够简单，便于调试 |
| 时间处理 | datetime / zoneinfo | 标准库优先 |
| 提醒调度 | QTimer | 与 Qt 事件循环集成，避免额外调度复杂度 |
| 测试 | pytest | 单元测试和核心逻辑测试 |
| 打包 | PyInstaller | 后续打包 Windows exe |

一期不强制引入 APScheduler。原因是当前只做单次提醒，`QTimer` 每 30 秒扫描即可，复杂度更低。

## 2. 一期运行架构

```text
User
  -> PySide6 Frameless Floating Card
      -> Todo UI
      -> Schedule UI
      -> Dialogs
  -> Core Services
      -> TodoService
      -> ScheduleService
      -> ReminderService
      -> StorageService
  -> Local Files
      -> data/todos.json
      -> data/schedules.json
```

## 3. 推荐目录结构

```text
FlowSphere/
├── Docs/
│   ├── README.md
│   ├── 01-project-overview.md
│   ├── 02-phase1-requirements.md
│   ├── 03-architecture.md
│   ├── 04-development-plan.md
│   ├── 05-test-plan.md
│   ├── 06-roadmap.md
│   └── 07-technology-stack.md
│
├── desktop/
│   ├── src/
│   │   ├── main.py
│   │   ├── app.py
│   │   │
│   │   ├── ui/
│   │   │   ├── main_window.py
│   │   │   ├── tray_icon.py
│   │   │   ├── todo_tab.py
│   │   │   ├── schedule_tab.py
│   │   │   ├── todo_dialog.py
│   │   │   ├── schedule_dialog.py
│   │   │   └── widgets.py
│   │   │
│   │   ├── core/
│   │   │   ├── todo_service.py
│   │   │   ├── schedule_service.py
│   │   │   ├── reminder_service.py
│   │   │   └── storage_service.py
│   │   │
│   │   ├── models/
│   │   │   ├── todo.py
│   │   │   └── schedule.py
│   │   │
│   │   └── utils/
│   │       ├── paths.py
│   │       ├── time_utils.py
│   │       └── logger.py
│   │
│   ├── data/
│   │   ├── todos.json
│   │   └── schedules.json
│   │
│   ├── tests/
│   │   ├── test_storage_service.py
│   │   ├── test_todo_service.py
│   │   ├── test_schedule_service.py
│   │   └── test_reminder_service.py
│   │
│   ├── requirements.txt
│   ├── README.md
│   └── build.bat
│
└── oldDocs/
```

## 4. 模块职责

| 模块 | 职责 |
|---|---|
| `main.py` | 程序入口，创建 QApplication |
| `app.py` | 初始化服务、窗口、定时器 |
| `ui/main_window.py` | 无边框悬浮卡片窗口和标签页容器 |
| `ui/tray_icon.py` | 系统托盘图标、右键菜单、显示/关闭操作 |
| `ui/todo_tab.py` | 待办列表和操作按钮 |
| `ui/schedule_tab.py` | 日程列表和操作按钮 |
| `ui/todo_dialog.py` | 待办新增编辑表单 |
| `ui/schedule_dialog.py` | 日程新增编辑表单 |
| `core/storage_service.py` | JSON 读写、文件创建、损坏备份 |
| `core/todo_service.py` | 待办业务逻辑 |
| `core/schedule_service.py` | 日程业务逻辑 |
| `core/reminder_service.py` | 提醒扫描和触发 |
| `models/todo.py` | Todo 数据模型 |
| `models/schedule.py` | Schedule 数据模型 |
| `utils/time_utils.py` | 时间格式化和状态判断 |

## 5. 分层原则

| 层 | 规则 |
|---|---|
| UI 层 | 负责悬浮卡片展示和用户交互，不直接读写 JSON |
| Core 层 | 负责业务规则、校验和调用存储 |
| Models 层 | 负责数据结构和序列化 |
| Utils 层 | 放无业务状态的工具函数 |

## 6. 数据流

新增待办：

```text
TodoDialog
  -> TodoTab
  -> TodoService.create_todo()
  -> StorageService.save_todos()
  -> todos.json
  -> TodoTab.refresh()
```

触发提醒：

```text
QTimer timeout
  -> ReminderService.check_due_reminders()
  -> TodoService.list_pending_reminders()
  -> ScheduleService.list_pending_reminders()
  -> show notification/dialog
  -> mark reminded = true
  -> save files
```

## 7. 代码实现建议

| 建议 | 说明 |
|---|---|
| 使用 dataclass | Todo 和 Schedule 模型简单清晰 |
| ID 使用 uuid4 | 本地唯一即可 |
| 时间统一 ISO 字符串 | JSON 可读，后续易同步 |
| 存储写入用临时文件替换 | 避免写一半导致文件损坏 |
| UI 刷新先简单实现 | 一期不追求复杂状态管理 |
| 提醒先用应用弹窗 | Windows 原生通知可后续增强 |
| AI 先不接入 | Demo 不实现 AI，但服务层创建接口保持可被未来 AI 解析结果复用 |

## 8. 后续扩展预留

| 扩展 | 预留方式 |
|---|---|
| 系统托盘 | 已由 `ui/tray_icon.py` 实现，后续可替换自定义图标 |
| AI 输入 | 新增 `core/ai_service.py` 和 `ui/ai_input_dialog.py` |
| 主题 | 新增 `themes/` 和 `core/theme_service.py` |
| SQLite | 替换 `StorageService`，保持服务接口不变 |
| 云同步 | 新增 `core/sync_service.py`，模型增加 `remote_id` 和 `sync_status` |

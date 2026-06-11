# 技术栈选型文档

## 1. 文档目的

本文档用于明确 FlowSphere 当前阶段和后续阶段将使用的技术栈，避免一期 Demo 开发时过早引入云端、同步、AI 服务化等复杂技术。

当前开发重点是：

```text
Phase 1: FlowSphere Desktop Demo
```

也就是先完成一个本地待办日程桌面应用。

## 2. 技术栈分层

FlowSphere 的技术栈按阶段分为三类：

| 类型 | 说明 |
|---|---|
| 一期必选技术 | 当前 Demo 必须使用，直接参与开发 |
| 一期暂不引入技术 | 后续可能需要，但当前阶段不使用 |
| 后续阶段技术 | Web 平台、云同步、AI 工作流阶段再引入 |

## 3. Phase 1 必选技术栈

### 3.1 核心技术

| 类别 | 技术 | 版本建议 | 用途 | 选择理由 |
|---|---|---|---|---|
| 编程语言 | Python | 3.10+ | 桌面应用主语言 | 开发效率高，适合快速做 Demo |
| UI 框架 | PySide6 | 6.6+ | 桌面窗口、表单、列表、弹窗 | Qt 能力完整，适合 Windows 桌面应用 |
| 数据格式 | JSON | 标准库 | 本地数据持久化 | 简单、可读、调试成本低 |
| 数据模型 | dataclasses | 标准库 | Todo、Schedule 模型 | 轻量，适合一期数据结构 |
| 时间处理 | datetime | 标准库 | 时间校验、提醒判断 | 不额外引入依赖 |
| ID 生成 | uuid | 标准库 | 本地记录唯一 ID | 简单可靠 |
| 定时扫描 | QTimer | PySide6 内置 | 每 30 秒扫描提醒 | 与 Qt 事件循环集成，避免额外调度器 |
| 日志 | logging | 标准库 | 记录异常和关键操作 | 一期足够，后续可升级 |

### 3.2 测试技术

| 类别 | 技术 | 版本建议 | 用途 | 选择理由 |
|---|---|---|---|---|
| 单元测试 | pytest | 8.x | 测试服务层、存储层、提醒逻辑 | Python 生态主流，写法简洁 |
| 临时目录 | tempfile / pytest tmp_path | 标准库 / pytest 内置 | 隔离测试数据文件 | 避免污染真实 data 目录 |

### 3.3 打包技术

| 类别 | 技术 | 版本建议 | 用途 | 当前阶段 |
|---|---|---|---|---|
| Windows 打包 | PyInstaller | 6.x | 打包为 exe | 一期后半段或 Phase 2 使用 |

一期可以先源码运行，不强制第一时间打包 exe。

## 4. Phase 1 推荐依赖

一期 `requirements.txt` 建议保持极简：

```text
PySide6>=6.6.0
pytest>=8.0.0
```

如果要在一期末尾尝试打包，再加入：

```text
pyinstaller>=6.0.0
```

不建议一期引入过多依赖，尤其是调度、数据库、网络请求和 AI 相关依赖。

## 5. Phase 1 暂不引入技术

以下技术暂时不在一期 Demo 中使用：

| 技术 | 原计划用途 | 暂不引入原因 | 建议引入阶段 |
|---|---|---|---|
| APScheduler | 复杂定时任务、重复提醒 | 一期只做单次提醒，QTimer 足够 | Phase 2 或 Phase 4 |
| httpx | 调用 Ollama 或后端 API | 一期不做 AI 和云同步 | Phase 2 |
| pywin32 | 托盘增强、注册表、Windows 通知 | 一期可以用 PySide6 弹窗兜底 | Phase 2 |
| SQLite | 本地结构化存储 | 一期数据量小，JSON 更直观 | Phase 2 或 Phase 4 |
| pydantic | 数据校验 | 一期模型简单，手写校验即可 | 需要复杂输入时再引入 |
| qdarkstyle | 主题样式 | 一期不做复杂主题 | Phase 2 |
| Ollama | 本地 AI 解析 | 一期先完成手动创建闭环 | Phase 2 |
| Docker | 容器化 | 一期是本地桌面应用 | Phase 3 |
| PostgreSQL | 云端数据存储 | 一期没有后端 | Phase 3 |
| Redis | 缓存、Token、任务队列 | 一期没有后端 | Phase 3 |

## 6. 一期架构对应技术

```text
FlowSphere Desktop Demo
├── UI Layer
│   └── PySide6
│
├── Core Layer
│   ├── Python dataclasses
│   ├── datetime
│   ├── uuid
│   └── logging
│
├── Storage Layer
│   ├── json
│   └── pathlib
│
├── Reminder Layer
│   └── PySide6 QTimer
│
└── Test Layer
    └── pytest
```

## 7. 一期模块与技术映射

| 模块 | 使用技术 | 说明 |
|---|---|---|
| 悬浮卡片窗口 | PySide6 `QMainWindow` + `FramelessWindowHint` + `WindowStaysOnTopHint` | 自绘无边框置顶卡片 |
| 拖动移动 | PySide6 `QMouseEvent` | 鼠标拖动顶部标题栏改变位置 |
| 系统托盘 | PySide6 `QSystemTrayIcon` + `QMenu` + `QAction` | 隐藏到托盘、右键显示窗口或关闭 |
| 标签页 | PySide6 `QTabWidget` | 待办和日程双标签 |
| 列表展示 | PySide6 `QTableWidget` 或 `QListWidget` | 一期优先简单实现 |
| 新增编辑弹窗 | PySide6 `QDialog` | 表单输入 |
| 时间选择 | PySide6 `QDateTimeEdit` | 避免手写时间输入 |
| 表单校验 | Python 函数 | 标题、时间合法性校验 |
| 数据模型 | `dataclass` | Todo、Schedule |
| 数据存储 | `json` + `pathlib` | 本地文件读写 |
| 提醒扫描 | `QTimer` | 周期检查到期提醒 |
| 提醒弹窗 | PySide6 `QMessageBox` | 一期使用应用内提醒 |
| 日志 | `logging` | 错误和关键操作记录 |
| 测试 | pytest | 核心逻辑测试 |

## 8. 后续阶段技术栈

### 8.1 Phase 2：桌面智能助手增强

| 类别 | 技术 | 用途 |
|---|---|---|
| 系统能力 | pywin32 | 开机自启、Windows API、系统通知 |
| AI 请求 | httpx | 调用本地 Ollama |
| 本地模型 | Ollama + qwen3:0.6b | 自然语言解析待办和日程 |
| 主题 | QSS | 深色、浅色、自定义主题 |
| 打包 | PyInstaller | 生成 Windows exe |
| 数据库可选 | SQLite | 数据量增长后替换 JSON |

### 8.2 Phase 3：Web 协作平台

后端第一版采用 Phase 3A 策略：先用 Go 模块化单体完成 Auth、Project、Task API，技术和范围以 `09-backend-mvp-plan.md` 为准。

| 类别 | 技术 | 用途 |
|---|---|---|
| 后端语言 | Go | 微服务开发 |
| HTTP 框架 | Gin | REST API |
| ORM | GORM | PostgreSQL 访问 |
| 数据库 | PostgreSQL | 用户、项目、任务数据 |
| 缓存 | Redis | Token、缓存、限流辅助 |
| 前端框架 | Vue 3 | Web UI |
| UI 组件库 | Element Plus | 企业后台风格组件 |
| 状态管理 | Pinia | 前端状态 |
| 构建工具 | Vite | 前端构建 |

### 8.3 Phase 4：云同步与提醒服务

| 类别 | 技术 | 用途 |
|---|---|---|
| 同步 API | Go + Gin | Desktop 与云端同步 |
| 提醒服务 | Go Service | 个人待办和日程提醒 |
| 数据库 | PostgreSQL JSONB | 保存 notification、repeat 等结构化规则 |
| 本地缓存 | JSON 或 SQLite | Desktop 离线使用 |
| 后台任务 | 可选 cron / worker | 云端提醒扫描 |

### 8.4 Phase 5：AI 工作流能力

| 类别 | 技术 | 用途 |
|---|---|---|
| 本地 AI | Ollama | 离线自然语言解析 |
| HTTP 客户端 | httpx / Go HTTP Client | 调用 AI 服务 |
| AI 服务 | Go 或 Python | 统一封装模型调用 |
| Prompt 模板 | 文本文件 | 管理任务和日程解析提示词 |
| 结构化输出 | JSON Schema | 约束 AI 输出格式 |

## 9. 技术选型原则

| 原则 | 说明 |
|---|---|
| 一期少依赖 | 能用标准库解决的先不用第三方库 |
| UI 简单优先 | 先实现功能闭环，再做视觉优化 |
| 数据可读优先 | JSON 方便调试和演示 |
| 后续可替换 | StorageService 抽象好，后续可换 SQLite 或云同步 |
| 不提前服务化 | AI、提醒、同步在需求明确后再拆服务 |

## 10. 当前推荐结论

一期最终推荐技术栈：

```text
Python 3.10+
PySide6 6.6+
JSON 本地文件
dataclasses
QTimer
QMessageBox
logging
pytest
```

一期不推荐引入：

```text
Ollama
httpx
pywin32
APScheduler
SQLite
Docker
Go 后端
PostgreSQL
Redis
```

这样可以保证第一阶段开发目标足够清晰：先把本地待办日程 Demo 做完整、做稳定，再继续扩展桌面助手和云端平台。

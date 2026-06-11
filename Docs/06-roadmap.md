# 后续路线图

## 1. 路线总览

FlowSphere 建议按从本地到云端、从个人到团队、从手动到智能的顺序演进。

合并策略：

| 旧项目 | 迁移位置 | 说明 |
|---|---|---|
| FloatPlan 本地悬浮日程助手 | Phase 1-2 | 先吸收待办、日程、提醒，再吸收托盘、主题、AI 输入 |
| FlowSphere 云原生协作平台 | Phase 3 起 | 后续恢复认证、项目、任务、微服务、Web 前端和工程化能力 |

```text
Phase 1: 本地待办日程 Demo
  -> Phase 2: 桌面智能助手
  -> Phase 3: Web 协作平台
  -> Phase 4: 多端同步和提醒服务
  -> Phase 5: AI 工作流能力
```

## 2. Phase 2：桌面智能助手增强

目标：把 Phase 1 的 Demo 打磨成更像产品的桌面助手。

这一阶段主要承接旧 FloatPlan 的产品化能力，但仍保持单用户、本地优先，不引入账号和云端同步。

| 功能 | 说明 |
|---|---|
| 系统托盘 | 启动后可最小化到托盘 |
| 悬浮窗 | 支持置顶、小尺寸模式 |
| 主题切换 | 深色、浅色、自定义 QSS |
| 开机自启 | Windows 注册表配置 |
| AI 输入 | 接入本地 Ollama 解析自然语言 |
| 打包安装 | PyInstaller 生成 exe |

建议周期：1 到 2 周。

## 3. Phase 3：Web 协作平台

目标：恢复原 FlowSphere 云原生协作平台主线。

这一阶段承接 `oldDocs/docs01` 的核心能力，但建议先做可运行的 Web 协作 MVP，再逐步补 Kubernetes、监控和完整 CI/CD。

当前后端第一版按 Phase 3A 执行，范围见 `09-backend-mvp-plan.md`：先做模块化单体后端，稳定 Auth、Project、Task 的 API 和数据模型，再决定是否拆分服务。

核心架构：

```text
Frontend
  -> Gateway
      -> Auth Service
      -> Work Service
  -> PostgreSQL
  -> Redis
```

核心功能：

| 模块 | 功能 |
|---|---|
| Auth | 注册、登录、JWT、刷新令牌 |
| Work | 项目、成员、任务、任务状态 |
| Frontend | 登录、项目列表、任务看板 |
| DevOps | Docker、docker-compose、CI |

暂缓能力：

| 能力 | 暂缓原因 |
|---|---|
| Kubernetes | 可以在 Docker Compose MVP 稳定后再做 |
| Prometheus / Grafana | 先保证业务闭环和服务边界 |
| 复杂权限模型 | MVP 先支持 Owner / Assignee / Member 基础角色 |

建议周期：3 到 4 周。

## 4. Phase 4：多端同步和提醒服务

目标：让 Desktop 和 Web 使用同一账号体系和云端数据。

这一阶段是两个旧项目真正融合的关键点：桌面端保留离线体验，Web/后端提供账号、同步和跨端提醒。

新增服务：

```text
Reminder Service
```

职责：

| 能力 | 说明 |
|---|---|
| 个人待办 | 保存个人事项 |
| 日程 | 保存个人日程 |
| 提醒规则 | 保存 remind_at、repeat、notification |
| 同步接口 | Desktop 拉取和推送数据 |
| 冲突处理 | 一期可使用 updated_at 后写入优先 |

Desktop 需要新增：

| 模块 | 说明 |
|---|---|
| 登录页 | 复用 FlowSphere Auth |
| SyncService | 本地与云端同步 |
| 离线缓存 | 网络异常时继续本地使用 |
| 同步状态 | pending、synced、failed |

建议周期：2 到 3 周。

## 5. Phase 5：AI 工作流能力

目标：让 FlowSphere 可以通过自然语言创建任务、日程和项目事项。

能力设计：

| 能力 | 示例 |
|---|---|
| 创建待办 | “明天下午三点提醒我提交周报” |
| 创建日程 | “下周一上午十点开项目会” |
| 创建项目任务 | “给 Bob 分配部署 Grafana 的任务，优先级高” |
| 任务拆解 | “帮我把上线准备拆成任务列表” |

实现策略：

| 阶段 | 方式 |
|---|---|
| 初期 | Desktop 内部调用本地 Ollama |
| 中期 | 后端新增 AI Service |
| 后期 | 支持本地模型和外部 API 切换 |

## 6. 长期目标

长期 FlowSphere 可以形成这样的产品结构：

```text
FlowSphere
├── Desktop Assistant
│   ├── 待办
│   ├── 日程
│   ├── 提醒
│   └── AI 输入
│
├── Web Collaboration
│   ├── 项目
│   ├── 成员
│   ├── 任务
│   └── 看板
│
├── Cloud Services
│   ├── Gateway
│   ├── Auth Service
│   ├── Work Service
│   ├── Reminder Service
│   └── AI Service
│
└── DevOps
    ├── Docker
    ├── Kubernetes
    ├── CI/CD
    └── Observability
```

## 7. 推荐推进原则

| 原则 | 说明 |
|---|---|
| 先 Demo 后平台 | 先有可运行成果，再扩工程复杂度 |
| 先本地后云端 | 本地闭环稳定后再同步 |
| 先手动后 AI | 手动创建流程稳定后再加自然语言 |
| 先简单后完整 | 每阶段都保持可演示状态 |
| 不提前重构 | 只有当扩展需求明确时再抽象服务 |

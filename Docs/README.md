# FlowSphere 文档中心

本文档目录是 FlowSphere 合并后的新项目基准文档。当前策略是先完成一期本地待办日程 Demo，再根据时间逐步推进到桌面智能助手、云端协作平台和多端同步。

## 文档索引

| 文档 | 说明 |
|---|---|
| [00-demo-execution-checklist.md](./00-demo-execution-checklist.md) | Demo 阶段执行清单、TDD 顺序、验收步骤 |
| [01-project-overview.md](./01-project-overview.md) | 项目定位、阶段目标、整体路线 |
| [02-phase1-requirements.md](./02-phase1-requirements.md) | 一期本地待办日程 Demo 需求 |
| [03-architecture.md](./03-architecture.md) | 技术栈、系统架构、目录结构、数据模型 |
| [04-development-plan.md](./04-development-plan.md) | 开发周期、里程碑、任务拆分、风险控制 |
| [05-test-plan.md](./05-test-plan.md) | 测试策略、测试用例、验收标准 |
| [06-roadmap.md](./06-roadmap.md) | 后续阶段演进路线 |
| [07-technology-stack.md](./07-technology-stack.md) | 技术栈选型、阶段依赖、模块技术映射 |
| [08-merge-strategy.md](./08-merge-strategy.md) | oldDocs 两个旧项目的合并策略、能力迁移边界和执行建议 |
| [09-backend-mvp-plan.md](./09-backend-mvp-plan.md) | 后端 MVP 第一版范围、API、数据模型、权限和验收标准 |

## 当前开发基准

一期工程只做本地 Demo，不引入账号、云同步、Web 后端、AI 和 Kubernetes。

一期目标：

| 目标 | 说明 |
|---|---|
| 可运行 | Windows 本地可启动桌面程序 |
| 可管理 | 支持待办和日程的新增、编辑、删除、完成 |
| 可提醒 | 支持基础提醒规则和到期通知 |
| 可持久化 | 数据保存到本地文件 |
| 可演示 | 能完整展示一个本地待办日程助手 Demo |

## 推荐阅读顺序

1. 先读 `08-merge-strategy.md`，确认两个旧项目如何合并到新 FlowSphere。
2. 再读 `00-demo-execution-checklist.md`，确认 Demo 阶段执行范围和验收步骤。
3. 再读 `01-project-overview.md`，理解合并后的产品方向。
4. 再读 `02-phase1-requirements.md`，确认一期工程到底做什么、不做什么。
5. 然后读 `03-architecture.md`，按目录结构开始实现。
6. 开发时参考 `04-development-plan.md` 拆任务。
7. 每完成一个模块，用 `05-test-plan.md` 做验证。
8. 开始后端第一版时，按 `09-backend-mvp-plan.md` 执行。
9. 一期完成后，再参考 `06-roadmap.md` 规划下一阶段。

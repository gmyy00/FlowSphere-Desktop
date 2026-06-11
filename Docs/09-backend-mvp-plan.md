# 后端 MVP 第一版执行计划

## 1. 第一版目标

交付一个可本地运行、可测试、可对接未来 Web 前端和 Desktop 同步的 FlowSphere 后端 MVP。

第一版包含：

- 用户注册、登录、JWT 鉴权
- 项目创建、查看、加入、成员列表
- 项目任务创建、查看、状态更新、指派、删除
- PostgreSQL 持久化
- 数据库 migration
- 基础 API 文档
- 后端 README
- 核心 Go 测试
- Docker Compose 启动 PostgreSQL

第一版不做 Kubernetes、微服务拆分、独立 Gateway、Redis、AI Service、Desktop 云同步、复杂 RBAC、Web 前端和 Prometheus/Grafana。

## 2. 技术方案

后端采用模块化单体，服务边界按未来微服务拆分预留，但第一版只启动一个 API 服务。

| 类别 | 技术 |
|---|---|
| 语言 | Go |
| HTTP 框架 | Gin |
| ORM | GORM |
| 数据库 | PostgreSQL |
| 鉴权 | JWT Bearer Token |
| 密码 | bcrypt |
| 测试 | Go test + httptest |
| 本地数据库 | Docker Compose |

## 3. 目录结构

```text
backend/
├── cmd/server/main.go
├── internal/
│   ├── auth/
│   ├── config/
│   ├── db/
│   ├── httpapi/
│   ├── middleware/
│   ├── models/
│   ├── project/
│   ├── task/
│   └── testutil/
├── migrations/
├── api/
├── docker-compose.yml
├── .env.example
├── go.mod
└── README.md
```

## 4. 数据模型

第一版使用四张核心表：

| 表 | 用途 |
|---|---|
| `users` | 用户账号、邮箱、密码哈希 |
| `projects` | 项目基础信息和 owner |
| `project_members` | 项目成员关系和角色 |
| `tasks` | 项目任务、状态、优先级、负责人 |

角色先只支持 `OWNER` 和 `MEMBER`。任务负责人由 `tasks.assignee_id` 表达，不单独作为成员角色。

任务状态：

```text
TODO
IN_PROGRESS
DONE
```

## 5. API 范围

```text
GET  /health

POST /api/auth/register
POST /api/auth/login
GET  /api/me

POST   /api/projects
GET    /api/projects
GET    /api/projects/:id
POST   /api/projects/:id/join
GET    /api/projects/:id/members
DELETE /api/projects/:id

POST   /api/projects/:id/tasks
GET    /api/projects/:id/tasks
GET    /api/tasks/:id
PATCH  /api/tasks/:id/status
PATCH  /api/tasks/:id/assignee
DELETE /api/tasks/:id
```

## 6. 权限规则

| 场景 | 规则 |
|---|---|
| 创建项目 | 登录用户可创建，创建者自动成为 `OWNER` |
| 查看项目 | 项目成员可查看 |
| 加入项目 | 登录用户可加入，重复加入返回错误 |
| 删除项目 | 仅 `OWNER` 可删除 |
| 创建任务 | 项目成员可创建 |
| 查看任务 | 项目成员可查看 |
| 指派任务 | 仅 `OWNER` 可指派，且负责人必须是项目成员 |
| 更新任务状态 | `OWNER` 或任务负责人可更新 |
| 删除任务 | 仅 `OWNER` 可删除 |

## 7. 开发顺序

1. 写入本计划，并更新文档索引。
2. 搭建 `backend/` Go 工程骨架。
3. 实现配置、数据库连接、健康检查、统一错误响应和 JWT middleware。
4. 实现 migration 和 GORM 模型。
5. 实现 Auth 模块。
6. 实现 Project 模块。
7. 实现 Task 模块。
8. 补测试、API 文档和 README。
9. 运行 `go test ./...` 和本地启动验证。

## 8. 验收标准

第一版完成时必须满足：

- `docker compose up -d` 能启动 PostgreSQL
- migration 或自动迁移能创建表
- `go run ./cmd/server` 能启动 API 服务
- Auth、Project、Task 核心接口可用
- `go test ./...` 通过
- README 能说明从零启动后端
- 文档明确第一版做了什么、不做什么

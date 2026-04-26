# 架构审查报告：失败模式 · 命名规范字典 · 结构问题

> 审查者：高级架构师视角 · 2026-04-26  
> 范围：`services/` · `frontend/` · 根目录 · 配置体系

---

## 目录

1. [失败模式（Failure Patterns）](#一失败模式)
2. [命名规范字典（Naming Convention Dictionary）](#二命名规范字典)
3. [不合理目录结构](#三不合理目录结构)
4. [修复优先级清单](#四修复优先级清单)

---

## 一、失败模式

> 失败模式 = 当前已存在、会在规模增长或成员协作时触发真实故障的结构性问题。

---

### FP-01 · 后缀膨胀反模式（Suffix Proliferation）

**表现**：用 `_enhanced` / `_optimized` / `_old` / `_v2` 后缀创建平行文件，而非替换原文件。

```
# 后端 services/ 中的平行文件
audit_service.py
audit_service_enhanced.py       ← 谁在用？原版是否废弃？

llm_service.py
llm_service_enhanced.py         ← 两个并存，调用方怎么选？

vector_store.py
vector_store_optimized.py       ← 生产用哪个？

# 微服务级别
services/embedding-service/app.py
services/embedding-service/app_enhanced.py   ← 入口到底是哪个？

services/reranking-service/app.py
services/reranking-service/app_old.py        ← old 文件提交进了仓库

# 链路级别
chains/compliance_rag_chain.py
chains/optimized_rag_chain.py               ← 两套 RAG，无法判断哪套在跑
```

**后果**：
- 新成员不知道该用哪个，随机选一个
- `app_old.py` 被当成参考继续修改
- 两套实现各自修 bug，线上跑的不一定是"优化"版

**根因**：没有 feature branch + PR 合并机制，靠文件后缀区分迭代版本。

---

### FP-02 · API 路由层越权（Route Layer Boundary Violation）

**表现**：本该只做 HTTP 解包/组包的路由层，混入了基础设施逻辑和业务模块。

```
# api/v1/ 目录中不属于路由层的文件
app/api/v1/connection_manager.py   ← WebSocket 连接管理，应在 websocket/ 层
app/api/v1/message_queue.py        ← 消息队列，应在 infrastructure/ 或 services/
app/api/v1/performance_optimization.py  ← 性能优化，应在 services/
app/api/v1/production_monitoring.py     ← 监控，应在 services/
app/api/v1/rag_optimization.py          ← RAG 优化，应在 services/ 或 chains/
app/api/v1/security_enhancement.py     ← 安全增强，应在 middleware/ 或 services/
app/api/v1/security_testing.py          ← 测试工具，不该在生产代码路由层
app/api/v1/test.py                      ← 测试端点混在生产路由，安全风险
app/api/v1/client_examples/             ← 示例代码放在生产代码目录里
```

**后果**：
- 路由层变成垃圾桶，任何人有需求就往里塞
- `test.py` 和 `security_testing.py` 暴露在生产 API 路由中，存在安全风险
- 单元测试无法对路由层做隔离测试

---

### FP-03 · WebSocket 三处分裂（WebSocket Split Brain）

**表现**：WebSocket 相关代码散落在三个不同目录，功能重叠：

```
app/api/v1/websocket.py          ← 路由层
app/api/v1/audit_websocket.py    ← 路由层（audit专用）
app/websocket/audit_websocket.py ← 独立 websocket 层（同名！）
app/websocket/monitoring_websocket.py
```

`app/api/v1/audit_websocket.py` 与 `app/websocket/audit_websocket.py` **同名**，路由注册时实际引用的是哪个，需要逐行追踪。这是隐性 Bug 温床。

---

### FP-04 · 孤儿页面（Orphan Pages）

**表现**：`frontend/src/pages/` 中存在 5 个页面未在任何路由中注册：

```
❌ BedrockDashboard.tsx        → 无路由
❌ ComplianceMonitoringPage.tsx → 无路由
❌ QuickLoginPage.tsx           → 无路由（有 LoginPage 了）
❌ SimpleChatPage.tsx           → 无路由（有 ChatPage 了）
❌ TestKnowledgePage.tsx        → 无路由
```

同时存在**两个路由定义文件**：
- `frontend/src/routes.tsx`（根目录，旧版）
- `frontend/src/routes/index.tsx`（目录版，新版）

两者路由定义不一致，`App.tsx` 引用的是 `routes/index.tsx`，`routes.tsx` 处于游离状态。

**后果**：死代码随构建产出，Bundle 增大；`routes.tsx` 被误以为有效而修改，改了也没效果。

---

### FP-05 · 认证双轨制（Dual Auth State）

**表现**：认证状态同时存在于两套机制中，且行为不一致：

```
# 轨道 A：React Context
frontend/src/contexts/AuthContext.tsx
  → 维护 user 对象、isAuthenticated、login/logout 方法
  → 读取 localStorage 的 auth_token

# 轨道 B：Redux Store
frontend/src/store/slices/authSlice.ts
  → 同样维护认证状态

# 路由守卫
routes/index.tsx 中的 ProtectedRoute
  → 调用 authService.isAuthenticated()  ← 第三个认证源
```

**后果**：
- 组件可以从三个地方读取"是否已登录"，结果可能不同
- logout 只清掉一个，另外两个没清，导致幽灵登录态
- 新成员不知道该用哪套，随机选

---

### FP-06 · 根目录垃圾场（Root Directory Pollution）

**实际统计**：
```
根目录 .py 文件：51 个
根目录 .sh 文件：34 个
根目录 .md 文件：53 个
```

其中测试文件 39 个直接堆放在项目根目录（`test_*.py`），覆盖：
```
test_audit_enhanced_simple.py   test_chat_demo.py
test_audit_logs_enhanced.py     test_chat_fix.py      ← "fix" 进了正式仓库
test_cors_fix.py                test_correct_chat.py  ← "correct" 暗示之前是错的
test_rag_fix.py                 ...
```

文件名中的 `_fix` `_simple` `_demo` `_correct` 是典型的**调试残留**，不该出现在主分支。

---

### FP-07 · Audit 领域爆炸（Domain Explosion）

**表现**：单个 `audit` 领域膨胀出 11 个文件：

```
# API 层（4个）
api/v1/audit.py
api/v1/audit_enhanced.py
api/v1/audit_maintenance.py
api/v1/audit_websocket.py

# Service 层（4个）
services/audit_service.py
services/audit_service_enhanced.py
services/audit_backup_service.py
services/audit_cleanup_service.py
services/audit_monitoring_service.py   ← 5个！

# 其他
models/audit_log.py
websocket/audit_websocket.py
scripts/audit_maintenance.py           ← 还有一个在scripts
test_audit_*.py                        ← 根目录 6 个测试文件
```

这是 FP-01（后缀膨胀）+ 缺乏领域边界双重失效的结果。`audit` 本是一个领域，现在分裂成互不统属的碎片。

---

### FP-08 · 配置体系三叉戟（Config Fragmentation）

**表现**：配置分散在三套独立体系中，相互不感知：

```
/config/                          # 顶层配置目录
  app.yaml
  development.yaml / production.yaml
  environments/
  database/
  web/

/deployment/configs/              # 部署配置目录（独立）
  env-ubuntu-vllm.env
  presets/
  templates/
  user/

services/main-app/app/core/config.py  # 代码内配置（Pydantic）
```

**后果**：`config/` 和 `deployment/configs/` 同样存放环境配置，新成员改错地方，改了没效果。

---

### FP-09 · Shell 脚本命名双标（Script Naming Inconsistency）

根目录 34 个 shell 脚本同时使用两种命名风格：

```
# kebab-case（连字符）
start-system.sh
stop-services.sh
clean-vectorstore.sh
fix-dependencies.sh

# snake_case（下划线）
configure_production.sh
deploy_rag_optimization.sh
quick_test.sh
run_all_tests.sh
activate_venv.sh
```

两种风格随机混用，无规律可循。

---

### FP-10 · models 层严重萎缩（Anemic Model Layer）

**表现**：有大量 Service 层，但 models 只有 2 个文件：

```
models/
  audit_log.py
  document.py       ← 只有2个！
```

而 `services/` 有 20+ 个文件。这意味着大量数据结构被定义在 service 层或 API 层内部，导致：
- 数据结构无法跨 service 复用
- Pydantic schema 和 ORM model 界限模糊
- 没有统一的 `schemas/` 目录区分入参/出参/数据库模型

---

## 二、命名规范字典

> 以下是项目应统一遵守的命名规范。当前状态 vs 应有状态。

---

### 2.1 目录命名

| 层级 | 规范 | 示例 | 当前违规 |
|------|------|------|---------|
| 微服务目录 | `kebab-case` | `doc-processor` `embedding-service` | ✅ 正确 |
| Python 包目录 | `snake_case` | `main_app` `app/services` | ✅ 正确 |
| 前端组件目录 | `PascalCase` | `DocumentUpload/` `AuditLogs/` | ✅ 正确 |
| 前端功能目录 | `camelCase` | `store/` `hooks/` `services/` | ✅ 正确 |
| 配置目录 | `kebab-case` | `deployment/configs/` | ⚠️ 与 `config/` 重复 |

---

### 2.2 文件命名

#### Python 后端

| 类型 | 规范 | 正确示例 | 禁止示例 |
|------|------|---------|---------|
| 模块文件 | `snake_case.py` | `audit_service.py` | `auditService.py` `AuditService.py` |
| 测试文件 | `test_<模块名>.py` | `test_audit_service.py` | `test_audit_enhanced_simple.py` |
| 配置文件 | `<环境>.yaml` | `production.yaml` | `development_new.yaml` |
| **禁止后缀** | 无 `_enhanced` `_optimized` `_old` `_v2` `_new` `_simple` `_fix` | — | `audit_service_enhanced.py` |

#### TypeScript 前端

| 类型 | 规范 | 正确示例 | 禁止示例 |
|------|------|---------|---------|
| React 组件 | `PascalCase.tsx` | `DocumentUpload.tsx` | `documentUpload.tsx` |
| 工具/服务文件 | `camelCase.ts` | `authService.ts` | `AuthService.ts` `MessageQueue.ts`（大写错误） |
| Redux Slice | `<domain>Slice.ts` | `authSlice.ts` | `AuthSlice.ts` |
| 类型定义 | `<domain>.types.ts` 或 `types/index.ts` | `types/index.ts` | 分散定义 |
| Hooks | `use<Name>.ts` | `useFileUpload.ts` | `fileUpload.ts` |
| 测试文件 | `<Component>.test.tsx` | `AuditLogs.test.tsx` | 放在根目录 |

#### Shell 脚本

| 类型 | 规范 | 正确示例 | 禁止示例 |
|------|------|---------|---------|
| 所有脚本 | `kebab-case.sh` | `start-services.sh` | `start_services.sh` |

---

### 2.3 概念命名统一表（禁止同义词混用）

| 概念 | 统一用词 | 禁止使用 |
|------|---------|---------|
| 向量检索 | `rag` | `retrieval` `search_chain` `vector_search` 混用 |
| 文档块 | `chunk` | `segment` `piece` `fragment` 混用 |
| 嵌入向量 | `embedding` | `vector` `embed` 混用 |
| 知识库 | `knowledge_base` | `kb` `knowledge` `corpus` 混用 |
| 大语言模型 | `llm` | `model` `ai` `gpt` 混用 |
| 审计日志 | `audit_log` | `audit` `log` `audit_record` 混用 |
| 合规分析 | `compliance` | `regulation` `policy` `rule` 混用 |
| 重排序 | `reranking` | `rerank` `re_ranking` 混用（脚本里有 `rerank` 有 `reranking`）|
| 服务版本迭代 | 通过 Git branch/PR | ~~`_enhanced` `_v2` `_optimized`~~ |

---

### 2.4 API 路由命名规范

```
# 规范
GET    /api/v1/{resource}            # 列表
GET    /api/v1/{resource}/{id}       # 详情
POST   /api/v1/{resource}            # 创建
PUT    /api/v1/{resource}/{id}       # 全量更新
PATCH  /api/v1/{resource}/{id}       # 部分更新
DELETE /api/v1/{resource}/{id}       # 删除

# 当前违规（部分路由无 prefix，直接注册到根）
app.include_router(audit_enhanced.router, prefix="/api/v1")   # ⚠️ 无具体资源前缀
app.include_router(monitoring.router, prefix="/api/v1")       # ⚠️ 无具体资源前缀
app.include_router(rag_optimization.router)                   # ❌ 无任何 prefix
```

---

### 2.5 环境变量命名规范

```ini
# 规范：全大写 + 下划线，按服务前缀分组
LLM_PROVIDER=openai
LLM_MODEL=qwen3-8b
LLM_BASE_URL=http://localhost:8001/v1

EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=bge-base-en-v1.5
EMBEDDING_API_BASE=http://localhost:8002

DB_HOST=localhost
DB_PORT=5432
DB_NAME=compliance_db
DB_USER=langchain
DB_PASSWORD=...

REDIS_HOST=localhost
REDIS_PORT=6379

# 当前违规（风格不统一）
DATABASE_URL=postgresql://...    # 整串连接，不分项
VITE_BACKEND_URL=...             # 前端用 VITE_ 前缀，正确
OPENAI_API_BASE=...              # 混用 OPENAI_ 前缀，而不是 LLM_
```

---

## 三、不合理目录结构

### 3.1 当前结构（问题标注）

```
drass/
├── *.py (51个)          ❌ 测试/工具脚本污染根目录
├── *.sh (34个)          ❌ 脚本未归类，命名风格混乱
├── *.md (53个)          ❌ 文档未归类
│
├── config/              ⚠️ 与 deployment/configs/ 职责重叠
│   ├── app.yaml
│   ├── development.yaml
│   └── environments/
│
├── deployment/
│   └── configs/         ⚠️ 同样是配置，和 /config/ 重复
│
├── frontend/src/
│   ├── routes.tsx       ❌ 与 routes/index.tsx 并存，产生歧义
│   ├── routes/
│   │   └── index.tsx
│   ├── pages/
│   │   ├── SimpleChatPage.tsx    ❌ 孤儿页面，无路由
│   │   ├── QuickLoginPage.tsx    ❌ 孤儿页面，无路由
│   │   ├── BedrockDashboard.tsx  ❌ 孤儿页面，无路由
│   │   ├── TestPage.tsx          ❌ 测试页面在生产代码
│   │   └── TestKnowledgePage.tsx ❌ 测试页面在生产代码
│   └── services/
│       ├── MessageQueue.ts       ❌ 大写开头，命名风格错误
│       └── WebSocketService.ts   ❌ 大写开头，命名风格错误
│
└── services/main-app/app/
    ├── api/v1/
    │   ├── connection_manager.py  ❌ 不属于路由层
    │   ├── message_queue.py       ❌ 不属于路由层
    │   ├── performance_optimization.py ❌ 不属于路由层
    │   ├── production_monitoring.py    ❌ 不属于路由层
    │   ├── rag_optimization.py         ❌ 不属于路由层
    │   ├── security_enhancement.py    ❌ 不属于路由层
    │   ├── security_testing.py         ❌ 安全测试在生产路由
    │   ├── test.py                     ❌ 测试端点在生产路由
    │   ├── audit_enhanced.py           ❌ 后缀反模式
    │   └── client_examples/            ❌ 示例代码在生产目录
    │
    ├── websocket/               ⚠️ 独立目录
    │   ├── audit_websocket.py   ❌ 与 api/v1/audit_websocket.py 同名
    │   └── monitoring_websocket.py
    │
    ├── services/
    │   ├── audit_service.py
    │   ├── audit_service_enhanced.py  ❌ 后缀反模式
    │   ├── llm_service.py
    │   ├── llm_service_enhanced.py    ❌ 后缀反模式
    │   ├── vector_store.py
    │   ├── vector_store_optimized.py  ❌ 后缀反模式
    │   └── LLM_SERVICE_MIGRATION.md   ❌ 文档放在代码目录
    │
    ├── chains/
    │   ├── compliance_rag_chain.py
    │   ├── optimized_rag_chain.py     ❌ 后缀反模式
    │   ├── prompts.py
    │   └── compliance_prompts.py      ⚠️ 两个 prompts 文件，职责界限不清
    │
    ├── models/              ⚠️ 只有 2 个文件，严重萎缩
    │   ├── audit_log.py
    │   └── document.py
    │
    ├── crud/                ⚠️ 只有 1 个文件
    │   └── document_crud.py
    │
    └── tasks/               ⚠️ 只有 1 个文件
        └── document_processor.py
```

---

### 3.2 建议重构后结构

```
drass/
├── .env.example             # 环境变量模板
├── docker-compose.yml
├── README.md                # 只留一个入口文档
│
├── docs/                    # 所有文档归这里
│   ├── architecture/
│   ├── deployment/
│   └── api/
│
├── scripts/                 # 所有脚本归这里（已有，但需清理）
│   ├── start.sh             # 统一入口
│   ├── stop.sh
│   └── deploy/
│
├── config/                  # 唯一配置目录
│   ├── development.yaml
│   ├── production.yaml
│   └── nginx.conf
│
├── tests/                   # 根级测试统一归这里（39个 test_*.py 移入）
│   ├── e2e/
│   ├── integration/
│   └── performance/
│
├── frontend/src/
│   ├── routes/              # 只保留一个路由定义
│   │   └── index.tsx
│   ├── pages/               # 只放有路由的页面
│   ├── features/            # 按领域组织（替代当前 components/ 的平铺）
│   │   ├── audit/
│   │   ├── chat/
│   │   ├── documents/
│   │   └── knowledge/
│   ├── shared/              # 跨功能共享组件
│   │   └── components/
│   └── services/            # 统一 camelCase 命名
│       ├── authService.ts
│       ├── chatService.ts
│       └── websocketService.ts  # 小写开头
│
└── services/main-app/app/
    ├── api/v1/              # 只放路由，轻量
    │   ├── auth.py
    │   ├── chat.py
    │   ├── documents.py
    │   ├── knowledge.py
    │   ├── audit.py
    │   ├── settings.py
    │   └── monitoring.py
    │
    ├── websocket/           # WebSocket 统一在这里
    │   ├── manager.py       # connection_manager 移入
    │   ├── audit.py
    │   └── monitoring.py
    │
    ├── services/            # 保留，但清除后缀变体
    │   ├── audit/           # 按领域拆子目录（替代 audit_* 5个文件平铺）
    │   │   ├── service.py
    │   │   ├── backup.py
    │   │   └── cleanup.py
    │   ├── llm_service.py   # 只保留一个（enhanced 的能力合并进来）
    │   └── vector_store.py  # 只保留一个
    │
    ├── schemas/             # 新增：Pydantic 入参/出参 schema（当前缺失）
    │   ├── audit.py
    │   ├── chat.py
    │   └── document.py
    │
    ├── models/              # ORM 模型（扩充）
    ├── chains/              # 只保留一套 RAG 实现
    │   ├── rag_chain.py     # 合并 compliance_rag_chain + optimized_rag_chain
    │   └── prompts.py       # 合并 prompts + compliance_prompts
    │
    └── infrastructure/      # 新增：基础设施层
        ├── message_queue.py  # 从 api/v1/ 移出
        └── cache.py
```

---

## 四、修复优先级清单

| 优先级 | 问题 | 影响 | 操作 |
|--------|------|------|------|
| 🔴 P0 | `api/v1/test.py` 和 `security_testing.py` 在生产路由 | 安全风险 | 立即删除或移到非生产 profile |
| 🔴 P0 | 认证双轨（AuthContext + authSlice + authService） | Bug 温床 | 选一套，删掉另外两套 |
| 🔴 P0 | `audit_websocket.py` 同名文件存在两处 | 隐性 Bug | 确定哪个生效，删掉另一个 |
| 🟠 P1 | 后缀变体文件（`_enhanced` `_optimized` `_old`） | 可维护性崩溃 | 合并后删除原版或变体 |
| 🟠 P1 | 5 个孤儿页面 + 2 个路由文件 | 死代码，Bundle 增大 | 删除或注册路由，删掉旧 routes.tsx |
| 🟠 P1 | 39 个测试文件堆在根目录 | 开发体验极差 | 移入 `tests/` 目录 |
| 🟡 P2 | API 路由层越权（8 个非路由文件） | 架构腐化 | 逐步迁移到对应层 |
| 🟡 P2 | `config/` 与 `deployment/configs/` 重复 | 改错地方 | 合并为唯一配置目录 |
| 🟡 P2 | Shell 脚本命名混用 kebab/snake | 认知负担 | 统一改为 kebab-case |
| 🟢 P3 | `models/` 只有 2 个文件，缺少 `schemas/` | 技术债 | 补充 schemas 层 |
| 🟢 P3 | 前端 `MessageQueue.ts` `WebSocketService.ts` 大写 | 命名规范 | 改为 camelCase |
| 🟢 P3 | 两个 prompts 文件职责不清 | 认知负担 | 合并或明确边界 |

---

> **总结**：这个项目最核心的失败模式是「以文件后缀代替版本管理」——每次迭代不是替换，而是新建一个 `_enhanced` 变体。这在单人开发阶段勉强可用，一旦团队协作或规模增长，会迅速演变成没有人知道哪个是"真正跑在生产上的代码"。  
> 建议先解决 P0 安全问题，再推行命名规范字典，最后逐步重构目录结构。

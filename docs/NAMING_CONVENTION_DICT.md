# 命名规范字典 · Drass 合规助手平台

> 基于实际代码扫描整理 · 2026-04-26  
> 覆盖：Python 后端 / FastAPI 路由 / React 前端 / 目录结构 / 配置 / 数据库 / 脚本

---

## 速查表

| 场景 | 规范 | 示例 |
|------|------|------|
| Python 文件名 | `snake_case` | `audit_service.py` |
| Python 类名 | `PascalCase` | `AuditService` |
| Python 函数/方法 | `snake_case` | `log_audit_event()` |
| Python 私有方法 | `_snake_case` | `_load_audit_logs()` |
| Python 常量 | `UPPER_SNAKE_CASE` | `SECRET_KEY` |
| Python 变量 | `snake_case` | `conversation_id` |
| Pydantic 字段 | `snake_case` | `created_at` |
| FastAPI URL | `snake_case` | `/api/v1/audit_logs` |
| FastAPI Query Param | `snake_case` | `?start_date=` |
| React 组件文件 | `PascalCase.tsx` | `SimpleChatInterface.tsx` |
| React 组件名 | `PascalCase` | `MessageBubble` |
| React Props 接口 | `PascalCase + Props` | `DocumentUploadProps` |
| React Hook 文件 | `camelCase.ts` | `useFileUpload.ts` |
| React 事件处理器 | `handle + PascalCase` | `handleSendMessage` |
| Redux Slice 文件 | `camelCase + Slice.ts` | `chatSlice.ts` |
| Redux State Key | `camelCase` | `activeConversation` |
| Redux Action | `camelCase` | `setActiveConversation` |
| 环境变量 | `UPPER_SNAKE_CASE` | `LLM_PROVIDER` |
| 前端环境变量 | `VITE_UPPER_SNAKE_CASE` | `VITE_API_URL` |
| Docker 服务名 | `kebab-case` | `main-app` |
| Shell 脚本文件 | `kebab-case.sh` | `start-system.sh` |
| Python 脚本文件 | `snake_case.py` | `qwen3_api_server.py` |
| 数据库表名 | `snake_case`（复数） | `audit_logs` |
| 数据库字段名 | `snake_case` | `created_at` |
| 后端目录名 | `snake_case` | `agents/`, `api/v1/` |
| 前端目录名 | `camelCase` | `components/`, `store/slices/` |

---

## 一、Python 后端

### 1.1 文件命名

规则：**全小写 + 下划线分隔（snake_case）**

```
# 服务层
audit_service.py
document_service.py
llm_service_enhanced.py     ← 有 enhanced/optimized 后缀表示迭代版本（待合并）

# 路由层
auth.py
chat.py
audit_websocket.py
rag_optimization.py

# 模型/Schema 层
audit_log.py
document.py
chat.py

# 核心配置
config.py
logging.py
metrics.py
security.py

# 测试文件
test_agent.py
test_rag_chain.py
test_document_service.py
```

### 1.2 类命名

规则：**PascalCase**，类型后缀明确职责

| 后缀 | 用途 | 示例 |
|------|------|------|
| `Service` | 业务逻辑层 | `AuditService`, `DocumentService`, `LLMService` |
| `Chain` | LangChain 链 | `ComplianceRAGChain`, `OptimizedRAGChain` |
| `Agent` | Agent 实现 | `ComplianceAgent` |
| `Router` | FastAPI 路由器 | `ChatRouter`, `AuditRouter` |
| `Request` | 请求体 Schema | `ChatRequest`, `LoginRequest` |
| `Response` | 响应体 Schema | `ChatResponse`, `DocumentResponse` |
| `Base` | Pydantic 基类 | `DocumentBase`, `UserBase` |
| `Create` | 创建用 Schema | `DocumentCreate` |
| `Update` | 更新用 Schema | `DocumentUpdate` |
| `Enum` | 枚举类型 | `AuditEventType`, `AuditSeverity`, `DocumentStatus` |
| `Factory` | 工厂类 | `ComplianceRAGChainFactory`, `SpecializedAgentFactory` |
| `Orchestrator` | 编排类 | `AgentOrchestrator` |

### 1.3 函数 / 方法命名

规则：**snake_case**，动词开头

```python
# 公有方法（动词 + 名词）
log_audit_event()
process_chat()
get_audit_logs()
initialize()
upload_document()
decode_token()

# 私有方法（下划线前缀）
_load_audit_logs()
_save_audit_logs()
_get_user_info()
_build_chain()

# 工厂 / 工具函数
get_logger()
setup_logging()
create_chain()
get_db()            ← FastAPI 依赖注入习惯用 get_ 前缀
```

常用动词约定：

| 动词 | 含义 |
|------|------|
| `get_` | 查询单条或列表 |
| `create_` | 新建资源 |
| `update_` | 更新资源 |
| `delete_` | 删除资源 |
| `process_` | 处理/执行业务 |
| `build_` | 构建对象 |
| `initialize_` / `setup_` | 初始化 |
| `log_` | 记录日志/审计 |

### 1.4 变量 / 常量命名

```python
# 普通变量 — snake_case
conversation_id = "..."
user_info = {}
filtered_logs = []
audit_id = uuid4()

# 类实例属性 — snake_case
self.audit_logs = []
self.audit_file_path = Path("...")
self.llm_service = LLMService()

# 模块级常量 — UPPER_SNAKE_CASE
ENVIRONMENT = "production"
DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"
MAX_RETRIES = 3
DEFAULT_CHUNK_SIZE = 1000
```

### 1.5 Pydantic 字段命名

规则：**snake_case**，时间字段统一加 `_at` 后缀

```python
class AuditLogEntry(BaseModel):
    id: str
    event_type: AuditEventType
    user_id: str
    resource_type: str
    timestamp: datetime
    created_at: datetime

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    conversation_id: Optional[str]
    use_knowledge_base: bool = True
    temperature: float = 0.7
    max_tokens: int = 2000
```

---

## 二、FastAPI 路由

### 2.1 URL Path

规则：**全小写 + 下划线分隔（snake_case）**，统一前缀 `/api/v1/`

```
# 资源型
GET    /api/v1/auth
POST   /api/v1/auth/login
POST   /api/v1/chat
GET    /api/v1/chat/stream
GET    /api/v1/documents
POST   /api/v1/documents/upload
GET    /api/v1/knowledge

# 带路径参数（snake_case 参数名）
GET    /api/v1/audit/conversations/{conversation_id}
GET    /api/v1/documents/{document_id}

# WebSocket
WS     /api/v1/ws
WS     /api/v1/audit/ws
```

### 2.2 Query 参数

规则：**snake_case**

```
?limit=20
?offset=0
?start_date=2026-01-01
?end_date=2026-04-26
?event_type=LOGIN
?token=xxx
```

### 2.3 Request / Response Body 字段

规则：**snake_case**（与 Pydantic 保持一致）

```json
{
  "conversation_id": "abc-123",
  "messages": [...],
  "use_rag": true,
  "temperature": 0.7,
  "max_tokens": 2000
}
```

---

## 三、React / TypeScript 前端

### 3.1 文件命名

| 类型 | 规则 | 示例 |
|------|------|------|
| 组件 | `PascalCase.tsx` | `SimpleChatInterface.tsx`, `DocumentUpload.tsx` |
| Hook | `use + PascalCase.ts` | `useFileUpload.ts`, `useAppDispatch.ts` |
| Redux Slice | `camelCase + Slice.ts` | `authSlice.ts`, `chatSlice.ts` |
| 工具函数 | `camelCase.ts` | `formatDate.ts` |
| 类型定义 | `camelCase.ts` | `types.ts` |
| 样式 | `kebab-case.css` 或同名 `.module.css` | `index.css` |
| 入口/配置 | `camelCase` | `main.tsx`, `vite-env.d.ts` |

### 3.2 组件命名

规则：**PascalCase**，MUI Styled 组件也用 PascalCase

```tsx
// 普通组件
SimpleChatInterface
DocumentUpload
MessageBubble
LogTable

// MUI Styled 组件（语义化命名，不加 Styled 前缀）
ChatContainer
MessagesArea
InputArea
StyledTextField
```

### 3.3 Props 接口

规则：**组件名 + `Props` 后缀**

```ts
interface DocumentUploadProps { ... }
interface MessageBubbleProps { ... }
interface AuditLogsProps { ... }
```

### 3.4 Redux 命名

```ts
// Slice 文件名：camelCase + Slice
authSlice.ts / chatSlice.ts / knowledgeSlice.ts

// State key（createSlice name）：camelCase
name: 'auth'
name: 'chat'
name: 'documents'

// Action creators：camelCase 动词
setActiveConversation
addMessage
updateStreamingMessage
clearMessages

// Async Thunk：camelCase 动词
sendMessage
loadConversations
createConversation
uploadDocument
```

### 3.5 事件处理函数

规则：**`handle` + 事件对象（PascalCase）**

```ts
handleSendMessage
handleKeyPress
handleDrop
handleRetryFile
handleUploadComplete
handleClose
handleSubmit
```

### 3.6 CSS / className

- MUI `sx` prop：行内对象，key 用 camelCase（`fontSize`, `marginTop`）
- Styled Components：组件名用 PascalCase
- DOM 传递布尔属性：全小写（`isuser` 而非 `isUser`，避免 React DOM 警告）

---

## 四、目录结构

### 4.1 后端目录（snake_case）

```
services/main-app/app/
├── agents/
│   └── tools/
├── api/
│   └── v1/
├── chains/
│   └── tests/
├── core/
├── crud/
├── database/
│   └── migrations/
├── models/
├── services/
│   └── providers/
├── tasks/
└── websocket/
```

### 4.2 前端目录（camelCase）

```
frontend/src/
├── components/
├── config/
├── contexts/
├── hooks/
├── layouts/
├── pages/
├── services/
├── store/
│   └── slices/
└── types/
```

---

## 五、配置 / 环境变量

### 5.1 环境变量

规则：**UPPER_SNAKE_CASE**，前端变量强制加 `VITE_` 前缀

```bash
# 后端
LLM_PROVIDER=openrouter
LLM_MODEL=qwen3-8b-mlx
LLM_API_KEY=sk-xxx
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=xxx
JWT_ALGORITHM=HS256
EMBEDDING_MODEL=text-embedding-3-small
RERANKING_ENABLED=true

# 前端（Vite 注入）
VITE_API_URL=http://localhost:8000
VITE_BACKEND_URL=http://localhost:8000
VITE_WEBSOCKET_ENABLED=true
VITE_MAX_FILE_SIZE=10485760
```

### 5.2 Docker Compose 服务名

规则：**kebab-case**

```yaml
services:
  frontend:
  main-app:
  embedding-service:
  reranking-service:
  doc-processor:
  postgres:
  redis:
  chromadb:
```

---

## 六、数据库

规则：表名和字段名统一 **snake_case**，表名用**复数**

```sql
-- 表名
audit_logs
documents
users
conversations
messages

-- 字段名
id            -- 主键统一用 id
user_id       -- 外键：关联表单数 + _id
event_type
resource_type
file_size
storage_path
created_at    -- 创建时间统一用 created_at
updated_at    -- 更新时间统一用 updated_at
```

---

## 七、脚本文件

### 7.1 Shell 脚本

规则：**kebab-case + 动词开头**

```
start-system.sh
stop-services.sh
deploy.sh
configure_production.sh   ← 历史遗留（部分用了 snake_case，建议统一 kebab）
clean-vectorstore.sh
fix-dependencies.sh
```

### 7.2 Python 脚本

规则：**snake_case**

```
qwen3_api_server.py
run_migration.py
check_knowledge_base.py
start_chromadb.py
```

---

## 八、常见反模式（禁止）

| 反模式 | 错误示例 | 正确示例 |
|--------|---------|---------|
| 用版本后缀代替重构 | `audit_service_enhanced.py` | 合并到 `audit_service.py`，用 git 追踪历史 |
| 混用大小写风格 | `auditService.py` | `audit_service.py` |
| 前端组件用小写文件名 | `chatinterface.tsx` | `ChatInterface.tsx` |
| URL 用大写或驼峰 | `/api/v1/auditLogs` | `/api/v1/audit_logs` |
| 环境变量用小写 | `database_url=xxx` | `DATABASE_URL=xxx` |
| 布尔变量用 is/has 以外前缀 | `streaming_enabled` | `is_streaming` / `enable_streaming` |
| Props 接口不加后缀 | `interface Upload {}` | `interface UploadProps {}` |
| 事件处理不加 handle | `onSend()` / `submit()` | `handleSend()` / `handleSubmit()` |

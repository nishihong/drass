# 测试指南 - Drass LangChain合规助手

## 快速开始

### 1. 一键启动（推荐）

```bash
# 首次运行 - 安装依赖并配置环境
./quick_start.sh setup

# 编辑.env文件，添加API密钥
vi .env

# 启动所有服务
./quick_start.sh start

# 检查服务状态
./quick_start.sh status
```

### 2. 访问应用

启动成功后，可以访问：
- 🎨 **前端应用**: http://localhost:5173
- 📚 **API文档**: http://localhost:8000/docs
- 🔧 **Dify平台**: http://localhost

## 必需的API密钥配置

在`.env`文件中至少需要配置以下之一：

### 选项1: OpenRouter（推荐快速测试）
```env
LLM_PROVIDER=openrouter
LLM_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_API_KEY=sk-or-v1-xxxxx  # 从 https://openrouter.ai 获取
```

### 选项2: OpenAI
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-xxxxx  # 从 https://platform.openai.com 获取
```

## 功能测试流程

### 1. API健康检查
```bash
# 检查后端API是否正常
curl http://localhost:8000/health

# 查看API文档
open http://localhost:8000/docs
```

### 2. 测试聊天功能（通过API）
```bash
# 获取JWT token（需要先实现认证）
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}' \
  | jq -r '.access_token')

# 发送聊天消息
curl -X POST "http://localhost:8000/api/v1/chat/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "什么是GDPR？",
    "session_id": "test-session"
  }'
```

### 3. 测试WebSocket连接
```javascript
// 在浏览器控制台测试
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected to WebSocket');
    ws.send(JSON.stringify({
        type: 'chat',
        message: '你好，请介绍一下数据合规'
    }));
};

ws.onmessage = (event) => {
    console.log('Received:', event.data);
};
```

### 4. 测试文档上传（需要实现UI组件）
```bash
# 通过API上传文档
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf"
```

## 当前可测试功能

### ✅ 可以测试
1. **后端API启动** - FastAPI服务器
2. **API文档浏览** - Swagger UI
3. **数据库连接** - PostgreSQL
4. **Redis连接** - 缓存服务
5. **前端页面加载** - React应用

### ⚠️ 部分可测试（需要配置）
1. **LangChain RAG** - 需要配置LLM API密钥
2. **Agent系统** - 需要配置工具和LLM
3. **向量搜索** - 需要初始化向量数据库

### ❌ 暂时无法测试
1. **聊天界面** - UI组件未实现
2. **文档上传界面** - UI组件未实现
3. **知识库管理** - UI组件未实现
4. **Embedding服务** - 服务未部署
5. **Reranking服务** - 服务未部署

## 常见问题排查

### 1. Docker服务启动失败
```bash
# 检查Docker状态
docker-compose ps

# 查看错误日志
docker-compose logs api
docker-compose logs db

# 重启服务
./quick_start.sh restart
```

### 2. 后端API无法启动
```bash
# 检查Python依赖
cd services/main-app
source venv/bin/activate
pip list

# 查看错误日志
tail -f data/backend.log

# 手动启动调试
python -m uvicorn app.main:app --reload --log-level debug
```

### 3. 前端无法访问
```bash
# 检查Node依赖
cd frontend
npm list

# 查看错误日志
tail -f data/frontend.log

# 手动启动调试
npm run dev
```

### 4. LLM调用失败
- 检查`.env`中的API密钥是否正确
- 确认API密钥有足够的额度
- 检查网络连接是否正常

## 性能测试

### 基础负载测试
```python
# 安装locust
pip install locust

# 创建locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class ComplianceUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def health_check(self):
        self.client.get("/health")
    
    @task(3)
    def chat_message(self):
        self.client.post("/api/v1/chat/messages", json={
            "message": "测试消息",
            "session_id": "test"
        })
EOF

# 运行负载测试
locust -f locustfile.py --host=http://localhost:8000
```

访问 http://localhost:8089 查看负载测试界面

## 日志查看

```bash
# 查看所有Docker服务日志
./quick_start.sh logs docker

# 查看后端日志
./quick_start.sh logs backend

# 查看前端日志
./quick_start.sh logs frontend

# 实时监控所有日志
tail -f data/*.log
```

## 停止和清理

```bash
# 停止所有服务
./quick_start.sh stop

# 完全清理（包括数据）
./quick_start.sh clean
```

## 下一步建议

1. **配置LLM服务** - 获取并配置OpenRouter或OpenAI API密钥
2. **实现UI组件** - 完成ChatInterface等核心组件
3. **部署模型服务** - 启动Embedding和Reranking服务
4. **添加测试数据** - 上传一些测试文档到知识库
5. **编写自动化测试** - 添加单元测试和集成测试

## 联系支持

如遇到问题，请查看：
- 项目状态报告: `PROJECT_STATUS_REPORT.md`
- 任务列表: `TASK_LIST_LANGCHAIN.md`
- 设计文档: `docs/LANGCHAIN_COMPLIANCE_ASSISTANT_DESIGN.md`
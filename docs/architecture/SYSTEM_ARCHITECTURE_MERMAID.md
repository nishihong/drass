# 磐石数据合规分析系统 - Mermaid 架构图

---

## 1. 系统整体架构图

```mermaid
graph TB
    subgraph UI["🖥️ 用户界面层 UI Layer · :5173"]
        React["React / Vite"]
        MUI["Material-UI Components"]
        TS["TypeScript Frontend"]
    end

    subgraph GW["🔀 API 网关层 API Gateway · :8888"]
        FastAPI["FastAPI"]
        CORS["CORS Middleware"]
        JWT["JWT Auth Token"]
    end

    subgraph AI["🤖 AI 服务层 AI Services"]
        LLM["vLLM LLM\n:8001\nDeepSeek-R1"]
        Embed["vLLM Embedding\n:8010\nQwen3-Embed"]
        Rerank["vLLM Reranking\n:8012\nQwen3-Reranker"]
    end

    subgraph DB["💾 数据存储层 Data Storage"]
        Chroma["ChromaDB\n:8005\n向量数据库"]
        PG["PostgreSQL\n:5432\n关系数据库"]
        Redis["Redis\n:6379\n缓存数据库"]
    end

    User(["👤 用户"]) --> UI
    UI -->|"HTTP REST"| GW
    GW --> AI
    GW --> DB

    style UI fill:#1a1a2e,stroke:#4fc3f7,color:#fff
    style GW fill:#16213e,stroke:#4fc3f7,color:#fff
    style AI fill:#0f3460,stroke:#4fc3f7,color:#fff
    style DB fill:#533483,stroke:#4fc3f7,color:#fff
```

---

## 2. 服务依赖关系图

```mermaid
graph TD
    FE["🖥️ 前端 React\n:5173"]
    API["⚙️ 后端 FastAPI\n:8888"]
    LLM["🤖 vLLM LLM\n:8001"]
    Embed["📐 vLLM Embedding\n:8010"]
    Rerank["🔃 vLLM Reranking\n:8012"]
    Chroma["🗄️ ChromaDB\n:8005"]
    PG["🗃️ PostgreSQL\n:5432"]
    Redis["⚡ Redis\n:6379"]

    M1["DeepSeek-R1-0528-Qwen3-8B"]
    M2["Qwen3-Embedding-8B"]
    M3["Qwen3-Reranker-8B"]

    FE -->|"HTTP API"| API
    API -->|"推理请求"| LLM
    API -->|"向量化"| Embed
    API -->|"重排序"| Rerank
    API -->|"向量检索"| Chroma
    API -->|"用户/文档数据"| PG
    API -->|"缓存/会话"| Redis

    LLM -->|"加载"| M1
    Embed -->|"加载"| M2
    Rerank -->|"加载"| M3

    style FE fill:#0d7377,color:#fff
    style API fill:#14a085,color:#fff
    style LLM fill:#e94560,color:#fff
    style Embed fill:#e94560,color:#fff
    style Rerank fill:#e94560,color:#fff
    style Chroma fill:#533483,color:#fff
    style PG fill:#533483,color:#fff
    style Redis fill:#533483,color:#fff
```

---

## 3. 启动流程图

```mermaid
flowchart TD
    Start(["🚀 执行启动脚本\nstart-ubuntu-services.sh"]) --> Step1

    Step1["① 环境检查\n检查已运行服务\n创建必要目录\n配置环境变量"]
    Step1 --> Check{{"端口是否冲突?"}}
    Check -->|"是"| Option{{"选择操作"}}
    Option -->|"重启所有"| Kill["Kill 旧进程"]
    Option -->|"仅启动停止的"| Step2
    Option -->|"取消"| End2(["❌ 退出"])
    Kill --> Step2
    Check -->|"否"| Step2

    Step2["② AI 服务启动\nvLLM LLM :8001\nvLLM Embedding :8010\nvLLM Reranking :8012"]
    Step2 --> Step3

    Step3["③ 数据存储启动\nPostgreSQL :5432\nRedis :6379\nChromaDB :8005"]
    Step3 --> Step4

    Step4["④ 后端 API 启动\nFastAPI + Uvicorn\n中间件配置\n路由注册\n:8888"]
    Step4 --> Step5

    Step5["⑤ 前端服务启动\nReact + Vite\nHot Reload\n:5173"]
    Step5 --> Step6

    Step6["⑥ 健康检查\n端口监听验证\n服务状态验证\nAPI 端点测试"]
    Step6 --> OK{{"全部通过?"}}
    OK -->|"✅ 是"| Done(["🎉 系统就绪"])
    OK -->|"❌ 否"| Retry["查看日志\n排查错误"]
    Retry --> Step6
```

---

## 4. 数据流向图

```mermaid
sequenceDiagram
    actor User as 👤 用户
    participant FE as 🖥️ 前端 React
    participant API as ⚙️ FastAPI :8888
    participant Embed as 📐 Embedding :8010
    participant Chroma as 🗄️ ChromaDB :8005
    participant Rerank as 🔃 Reranking :8012
    participant LLM as 🤖 vLLM LLM :8001
    participant PG as 🗃️ PostgreSQL

    User->>FE: 输入查询问题
    FE->>API: POST /api/v1/chat
    API->>PG: 记录会话 / 鉴权
    API->>Embed: 向量化用户问题
    Embed-->>API: 返回 Query Vector
    API->>Chroma: 相似度检索 Top-K
    Chroma-->>API: 返回候选文档块
    API->>Rerank: 重排序候选结果
    Rerank-->>API: 返回精排文档
    API->>LLM: RAG Prompt + 上下文
    LLM-->>API: 流式生成响应
    API-->>FE: SSE 流式返回
    FE-->>User: 实时展示回答
```

---

## 5. 核心功能模块图

```mermaid
mindmap
  root(("🏛️ 磐石数据\n合规分析系统"))
    用户认证模块
      JWT Token 管理
      用户注册 / 登录
      权限控制 RBAC
      会话自动过期
    文档处理模块
      文档上传
      格式转换 PDF/DOCX
      内容 OCR 提取
      向量化处理
    知识库管理模块
      文档索引构建
      向量相似度搜索
      ChromaDB 持久化
      重排序优化
    聊天对话模块
      RAG 检索增强
      上下文窗口管理
      SSE 流式响应
      历史记录存储
    合规分析模块
      风险识别扫描
      合规规则检查
      分析报告生成
      审计日志记录
```

---

## 6. 端口分配总览

```mermaid
graph LR
    subgraph Ports["🌐 端口分配"]
        direction TB
        P1["5173 · 前端 React Dev Server · HTTP"]
        P2["8888 · 后端 FastAPI · HTTP"]
        P3["8001 · vLLM LLM DeepSeek-R1 · HTTP"]
        P4["8010 · vLLM Embedding Qwen3 · HTTP"]
        P5["8012 · vLLM Reranking Qwen3 · HTTP"]
        P6["8005 · ChromaDB 向量数据库 · HTTP"]
        P7["5432 · PostgreSQL 关系数据库 · TCP"]
        P8["6379 · Redis 缓存数据库 · TCP"]
    end
```

---

## 7. 目录结构图

```mermaid
graph TD
    Root["/home/qwkj/drass/"] --> D1
    Root --> D2
    Root --> D3
    Root --> D4
    Root --> D5
    Root --> D6
    Root --> QS["quick-start.sh"]

    D1["📁 deployment/scripts/"]
    D1 --> D1A["start-ubuntu-services.sh\n主启动脚本"]
    D1 --> D1B["stop-ubuntu-services.sh\n停止脚本"]
    D1 --> D1C["check-frontend.sh\n前端检查脚本"]

    D2["📁 services/main-app/"]
    D2 --> D2A["app/\nFastAPI 应用代码"]
    D2 --> D2B["requirements.txt\nPython 依赖"]
    D2 --> D2C["start_api.sh\nAPI 启动脚本"]

    D3["📁 frontend/"]
    D3 --> D3A["src/\nReact 源码"]
    D3 --> D3B["package.json\nNode.js 依赖"]
    D3 --> D3C["vite.config.ts\nVite 配置"]

    D4["📁 data/"]
    D4 --> D4A["chromadb/\n向量数据库文件"]
    D4 --> D4B["uploads/\n上传文件"]
    D4 --> D4C["processed/\n处理后的文件"]

    D5["📁 logs/"]
    D5 --> D5A["drass-api.log"]
    D5 --> D5B["drass-frontend.log"]
    D5 --> D5C["vllm-llm.log"]
    D5 --> D5D["vllm-embedding.log"]
    D5 --> D5E["vllm-reranking.log"]
    D5 --> D5F["chromadb.log"]

    D6["📁 models/\nAI 模型文件"]
```

---

## 8. 故障排除决策树

```mermaid
flowchart TD
    Problem(["❓ 系统异常"]) --> Q1{{"哪类问题?"}}

    Q1 -->|"端口冲突"| A1["lsof -i :端口号\n查找占用进程"]
    A1 --> A1B["kill -9 PID"]
    A1B --> A1C["重新启动服务"]

    Q1 -->|"GPU 内存不足"| B1["nvidia-smi 或 rocm-smi\n查看 GPU 使用率"]
    B1 --> B1B["调整 gpu_memory_utilization\n降低并行 tensor-parallel-size"]

    Q1 -->|"服务启动失败"| C1["查看对应 log 文件\nlogs/ 目录"]
    C1 --> C1B{{"依赖缺失?"}}
    C1B -->|"是"| C1C["pip install -r requirements.txt"]
    C1B -->|"否"| C1D["检查配置文件\n环境变量"]

    Q1 -->|"数据库连接失败"| D1["检查 PostgreSQL / Redis\n服务状态"]
    D1 --> D1B["systemctl restart postgresql\nsystemctl restart redis"]

    Q1 -->|"API 无响应"| E1["curl http://localhost:8888/health\n测试健康端点"]
    E1 --> E1B["查看 drass-api.log"]
```

---

## 9. 安全架构图

```mermaid
graph TB
    subgraph Security["🔒 安全配置"]
        subgraph Access["访问控制"]
            FW["防火墙规则"]
            Port["限制端口访问"]
        end

        subgraph Auth["认证授权"]
            JWT["JWT Token\n无状态认证"]
            PWD["密码哈希存储\nbcrypt"]
            Expire["会话自动过期"]
        end

        subgraph DataProt["数据保护"]
            Enc["数据加密传输\nHTTPS"]
            Backup["备份策略\n定期快照"]
        end

        subgraph Audit["日志审计"]
            OpLog["操作日志记录"]
            Rotate["日志自动轮转"]
            Alert["异常行为告警"]
        end
    end

    FE["前端请求"] -->|"HTTPS"| FW
    FW -->|"通过"| JWT
    JWT -->|"验证成功"| API["FastAPI 业务处理"]
    API --> OpLog
```

---

> 📌 **渲染提示**：使用 VSCode 插件 `Markdown Preview Mermaid Support` 或 [mermaid.live](https://mermaid.live) 查看图表效果。
>
> 📅 文档版本：v2.0 · 最后更新：2026-04-26

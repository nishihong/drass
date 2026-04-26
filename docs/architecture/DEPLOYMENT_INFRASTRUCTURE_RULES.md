# Drass 部署与基础设施规则

> 基于实际代码结构整理 · 2026-04-26

---

## 目录

1. [部署模式](#1-部署模式)
2. [服务清单与端口规则](#2-服务清单与端口规则)
3. [Docker 规则](#3-docker-规则)
4. [网络规则](#4-网络规则)
5. [存储与卷规则](#5-存储与卷规则)
6. [环境变量规则](#6-环境变量规则)
7. [健康检查规则](#7-健康检查规则)
8. [资源限制规则](#8-资源限制规则)
9. [Nginx 规则](#9-nginx-规则)
10. [监控规则](#10-监控规则)
11. [安全规则](#11-安全规则)
12. [启动与停止规则](#12-启动与停止规则)
13. [日志规则](#13-日志规则)

---

## 1. 部署模式

项目支持两套独立部署模式，不可混用：

| 模式 | 平台 | LLM 服务 | 入口脚本 |
|------|------|---------|---------|
| **Docker Compose** | 通用（Linux / Mac） | Qwen3-8B-MLX 本地进程 | `docker-compose up -d` |
| **Ubuntu 裸机** | Ubuntu 22.04 + AMD GPU | vLLM（DeepSeek-R1 / Qwen3） | `deployment/scripts/start-ubuntu-services.sh` |

- **开发环境**：直接运行各服务进程，无 Nginx
- **生产环境**：启用 `production` profile，Nginx 接管流量，强制 HTTPS

---

## 2. 服务清单与端口规则

### 2.1 核心服务（必须启动）

| 服务名 | 容器名 | 宿主机端口 | 容器端口 | 镜像/构建 |
|--------|--------|-----------|---------|----------|
| frontend | langchain-frontend | 5173 | 5173 | `./frontend` 构建 |
| main-app | langchain-backend | 8000 | 8000 | `./services/main-app` 构建 |
| postgres | langchain-postgres | 5432 | 5432 | `postgres:15-alpine` |
| redis | langchain-redis | 6379 | 6379 | `redis:7-alpine` |
| chromadb | langchain-chromadb | 8005 | 8000 | `chromadb/chroma:latest` |
| embedding-service | langchain-embedding | 8002 | 8001 | `./services/embedding-service` 构建 |
| reranking-service | langchain-reranking | 8004 | 8002 | `./services/reranking-service` 构建 |
| doc-processor | langchain-doc-processor | 5003 | 5003 | `./services/doc-processor` 构建 |

### 2.2 可选服务

| 服务名 | 容器名 | 宿主机端口 | Profile | 用途 |
|--------|--------|-----------|---------|------|
| llm-gateway | langchain-llm-gateway | 8003 | — | 多 LLM Provider 路由 |
| nginx | langchain-nginx | 80 / 443 | `production` | 反向代理（生产必须） |
| prometheus | langchain-prometheus | 9090 | `monitoring` | 指标采集 |
| grafana | langchain-grafana | 3001 | `monitoring` | 监控看板 |

### 2.3 裸机部署额外端口（Ubuntu vLLM）

| 服务 | 端口 | 说明 |
|------|------|------|
| vLLM LLM | 8001 | DeepSeek-R1-0528-Qwen3-8B |
| vLLM Embedding | 8010 | Qwen3-Embedding-8B |
| vLLM Reranking | 8012 | Qwen3-Reranker-8B |
| FastAPI（裸机） | 8888 | 与 Docker 的 8000 不同，注意区分 |

> ⚠️ **端口冲突规则**：启动前必须检查以上所有端口是否被占用，脚本内置冲突检测，发现冲突时提供 **重启 / 跳过 / 取消** 三种处理选项。

---

## 3. Docker 规则

### 3.1 镜像构建规则

- **main-app** 采用**多阶段构建**（Multi-stage build）：
  - `builder` 阶段：安装编译依赖，构建 Python 包
  - `production` 阶段：仅复制运行时产物，最小化镜像体积
- 基础镜像统一使用 `python:3.11-slim`
- 必须设置以下环境变量：
  ```
  PYTHONDONTWRITEBYTECODE=1
  PYTHONUNBUFFERED=1
  ```
- 所有服务容器必须以**非 root 用户**（`appuser` uid=1000）运行

### 3.2 reranking-service 构建规则

```yaml
target: app           # 跳过模型预下载阶段
cache_from:
  - drass-reranking-service:latest
args:
  BUILDKIT_INLINE_CACHE: 1
```

> 构建时必须使用 BuildKit 缓存，避免每次重下模型文件。

### 3.3 启动依赖顺序（depends_on）

```
postgres, redis
    ↓
chromadb, embedding-service, reranking-service, doc-processor
    ↓
main-app
    ↓
frontend, nginx
```

---

## 4. 网络规则

- 所有服务必须加入统一网络 `langchain-network`，驱动为 `bridge`
- 服务间通信使用**容器名**作为 hostname（不使用 localhost）
- 主服务通过 `host.docker.internal` 访问宿主机上的本地 LLM 进程（Qwen3-8B-MLX）

```yaml
networks:
  langchain-network:
    driver: bridge
```

---

## 5. 存储与卷规则

### 5.1 命名卷（持久化数据，不可删除）

| 卷名 | 挂载路径 | 用途 |
|------|---------|------|
| `postgres_data` | `/var/lib/postgresql/data` | 数据库持久化 |
| `redis_data` | `/data` | Redis AOF 持久化 |
| `chroma_data` | `/chroma/chroma` | 向量索引持久化 |
| `prometheus_data` | `/prometheus` | 监控数据（200h / 10GB 上限） |
| `grafana_data` | `/var/lib/grafana` | 看板配置持久化 |

### 5.2 绑定挂载（Bind Mount）

| 宿主机路径 | 容器路径 | 服务 | 说明 |
|-----------|---------|------|------|
| `./services/main-app` | `/app` | main-app | 开发热重载 |
| `./data/uploads` | `/app/uploads` | main-app | 上传文件共享 |
| `./models/embeddings` | `/app/models` | embedding-service | 模型文件 |
| `./models/reranking` | `/app/model_cache` | reranking-service | 模型缓存 |
| `./data/documents` | `/app/documents` | doc-processor | 待处理文档 |
| `./data/processed` | `/app/processed` | doc-processor | 处理结果 |
| `./logs/reranking` | `/app/logs` | reranking-service | 日志输出 |
| `./nginx/nginx.conf` | `/etc/nginx/nginx.conf` | nginx | Nginx 配置 |
| `./nginx/ssl` | `/etc/nginx/ssl` | nginx | SSL 证书 |

### 5.3 目录初始化规则

启动前必须确保以下目录存在：
```bash
logs/
data/chromadb/
data/uploads/
data/documents/
data/processed/
models/embeddings/
models/reranking/
```

---

## 6. 环境变量规则

### 6.1 管理规则

- 本地开发：复制 `env.example` 为 `.env`，**禁止提交 `.env` 到 Git**
- 生产环境：通过系统环境变量或 Docker secrets 注入，不使用 `.env` 文件
- 配置读取由 `services/main-app/app/core/config.py`（Pydantic BaseSettings）统一管理

### 6.2 必填变量

| 变量 | 说明 | 生产默认值要求 |
|------|------|--------------|
| `SECRET_KEY` | JWT 签名密钥 | **必须替换**，不可使用默认值 |
| `DATABASE_URL` | PostgreSQL 连接串 | 使用强密码 |
| `REDIS_URL` | Redis 连接串 | — |
| `LLM_API_KEY` | LLM 服务密钥 | 按 Provider 配置 |

### 6.3 LLM 配置变量

```ini
LLM_PROVIDER=openai          # LM Studio / vLLM 均使用 openai 协议
LLM_MODEL=qwen3-8b-mlx
LLM_BASE_URL=http://localhost:8001/v1   # 本地 LLM 地址
LLM_API_KEY=none             # 本地部署无需密钥
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
LLM_TIMEOUT=60
LLM_CONTEXT_LENGTH=32768
```

### 6.4 功能开关变量

```ini
ENABLE_STREAMING=true        # SSE 流式响应
ENABLE_AGENT=true            # LangChain Agent 系统
ENABLE_MEMORY=true           # 对话记忆
RERANKING_ENABLED=true       # 重排序（启用后必须启动 reranking-service）
ENABLE_DOCS=true             # FastAPI Swagger 文档（生产建议关闭）
```

### 6.5 文档处理变量

```ini
MAX_FILE_SIZE_MB=50          # 单文件最大 50MB
OCR_ENABLED=true             # OCR 识别
OCR_LANGUAGE=chi_sim+eng     # 中英文混合识别
CHUNK_SIZE=1000              # 文档切片大小
CHUNK_OVERLAP=200            # 切片重叠长度
```

---

## 7. 健康检查规则

所有核心服务必须配置 Health Check：

| 服务 | 检查命令 | 间隔 | 超时 | 重试 | 启动等待 |
|------|---------|------|------|------|---------|
| main-app | `curl -f http://localhost:8000/health` | 30s | 10s | 3 | 5s |
| postgres | `pg_isready -U langchain` | 10s | 5s | 5 | — |
| redis | `redis-cli ping` | 10s | 5s | 5 | — |
| reranking-service | `curl -f http://localhost:8002/health` | 30s | 10s | 3 | 60s |

> reranking-service 的 `start_period=60s` 是因为模型加载耗时较长，60s 内失败不计入重试次数。

---

## 8. 资源限制规则

仅 `reranking-service` 配置了显式资源限制，其他服务依赖宿主机调度：

```yaml
# reranking-service
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

### 裸机部署 GPU 规则（Ubuntu vLLM）

```bash
# vLLM 启动参数规则
--tensor-parallel-size=2         # 双 GPU 张量并行
--gpu-memory-utilization=0.45    # 单 GPU 占用率上限 45%
--max-model-len=12288            # 最大序列长度
```

---

## 9. Nginx 规则

生产环境（`production` profile）下 Nginx 为必选服务。

### 9.1 基础规则

```nginx
worker_connections 1024;
client_max_body_size 100M;    # 支持大文件上传
keepalive_timeout 65;
```

### 9.2 HTTPS 规则

- HTTP（:80）**强制重定向** 至 HTTPS（:443），仅 `/health` 例外
- TLS 版本：仅允许 `TLSv1.2` 和 `TLSv1.3`
- 加密套件：ECDHE-RSA-AES128/256-GCM-SHA256/384
- 证书路径：`/etc/nginx/ssl/cert.pem` + `key.pem`

### 9.3 限流规则

| 区域 | 速率 | burst | 适用路径 |
|------|------|-------|---------|
| `api` zone | 10r/s | 20 | `/api/*` |
| `web` zone | 30r/s | 50 | `/` |

### 9.4 安全响应头规则（必须）

```nginx
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 9.5 静态资源缓存规则

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    Cache-Control: public, immutable;
}
```

### 9.6 Gzip 压缩规则

启用 Gzip，压缩级别 6，最小压缩体积 1024 bytes，覆盖以下类型：
`text/plain` `text/css` `text/xml` `text/javascript` `application/json` `application/javascript` `image/svg+xml`

---

## 10. 监控规则

启动监控：`docker-compose --profile monitoring up -d`

### 10.1 Prometheus 采集规则

| Job | Target | 采集路径 | 间隔 |
|-----|--------|---------|------|
| prometheus | localhost:9090 | /metrics | 15s |
| drass-app | drass-app:8000 | /metrics | 30s |
| postgres | postgres:5432 | /metrics | 30s |
| redis | redis:6379 | /metrics | 30s |
| nginx | nginx:80 | /nginx_status | 30s |
| node | host.docker.internal:9100 | /metrics | 30s |
| docker | host.docker.internal:9323 | /metrics | 30s |

### 10.2 数据保留规则

```yaml
retention.time: 200h    # 约 8 天
retention.size: 10GB    # 磁盘上限
```

### 10.3 告警规则

- 告警规则文件路径：`monitoring/prometheus/rules/*.yml`
- AlertManager 地址：`alertmanager:9093`
- Grafana 管理员密码：**生产环境必须修改**（默认 `admin`）
- Grafana 安装插件：`redis-datasource`

---

## 11. 安全规则

### 11.1 认证规则

- JWT 算法：`HS256`
- Access Token 有效期：**30 分钟**
- Refresh Token 有效期：**7 天**
- 密码存储：bcrypt 哈希，禁止明文

### 11.2 CORS 规则

开发环境允许来源：
```
http://localhost:3000
http://localhost:5173
http://localhost:5174
```
生产环境必须通过 `CORS_ORIGINS` 环境变量**明确指定域名**，禁止使用 `*`。

### 11.3 ChromaDB 认证规则

```yaml
CHROMA_SERVER_AUTH_PROVIDER: TokenAuthenticationServerProvider
CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER: AUTHORIZATION
CHROMA_SERVER_AUTH_CREDENTIALS: test-token    # ⚠️ 生产必须修改
```

### 11.4 数据库密码规则

```yaml
# docker-compose.yml 默认值（生产必须替换）
POSTGRES_USER: langchain
POSTGRES_PASSWORD: langchain123    # ⚠️ 生产必须修改
```

### 11.5 速率限制规则

```ini
RATE_LIMIT_PER_MINUTE=60    # 每个 IP 每分钟最多 60 次 API 请求
```

---

## 12. 启动与停止规则

### 12.1 Docker Compose 启动规则

```bash
# 开发环境（核心服务）
docker-compose up -d

# 生产环境（含 Nginx）
docker-compose --profile production up -d

# 含监控
docker-compose --profile monitoring up -d

# 全部
docker-compose --profile production --profile monitoring up -d
```

### 12.2 裸机启动顺序规则（Ubuntu）

必须严格按以下顺序启动，每步等待就绪后再继续：

```
① 环境检查（端口冲突检测）
② vLLM LLM    :8001  →  等待模型加载完成
③ vLLM Embed  :8010  →  等待模型加载完成
④ vLLM Rerank :8012  →  等待模型加载完成
⑤ PostgreSQL  :5432  →  pg_isready 通过
⑥ Redis       :6379  →  redis-cli ping 通过
⑦ ChromaDB    :8005  →  HTTP 200
⑧ FastAPI     :8888  →  /health 通过
⑨ React Dev   :5173  →  页面可访问
```

### 12.3 停止规则

```bash
# 优雅停止（先 SIGTERM，2 秒后未退出则 SIGKILL）
./stop-services.sh

# Docker 停止
docker-compose down              # 保留数据卷
docker-compose down -v           # ⚠️ 删除所有数据卷（不可恢复）
```

---

## 13. 日志规则

### 13.1 日志格式规则

- 应用日志统一使用 **JSON 结构化格式**（`LOG_FORMAT=json`）
- 日志级别默认 `INFO`，生产可调整为 `WARNING`

### 13.2 日志文件规则

| 日志文件 | 对应服务 |
|---------|---------|
| `logs/drass-api.log` | FastAPI 后端 |
| `logs/drass-frontend.log` | React 前端 |
| `logs/vllm-llm.log` | vLLM LLM 服务 |
| `logs/vllm-embedding.log` | vLLM Embedding |
| `logs/vllm-reranking.log` | vLLM Reranking |
| `logs/chromadb.log` | ChromaDB |
| `/var/log/nginx/access.log` | Nginx 访问日志 |
| `/var/log/nginx/error.log` | Nginx 错误日志（warn 级别） |

### 13.3 Nginx 日志格式

```nginx
'$remote_addr - $remote_user [$time_local] "$request" '
'$status $body_bytes_sent "$http_referer" '
'"$http_user_agent" "$http_x_forwarded_for"'
```

---

> ⚠️ **生产上线前必检清单**
> - [ ] `SECRET_KEY` 已替换为随机强密钥
> - [ ] `POSTGRES_PASSWORD` 已修改
> - [ ] `CHROMA_SERVER_AUTH_CREDENTIALS` 已修改
> - [ ] `GF_SECURITY_ADMIN_PASSWORD` 已修改
> - [ ] `CORS_ORIGINS` 已指定为实际域名
> - [ ] SSL 证书已配置（非自签名）
> - [ ] `ENABLE_DOCS=false`（关闭 Swagger 文档）
> - [ ] 所有数据目录已初始化并设置正确权限

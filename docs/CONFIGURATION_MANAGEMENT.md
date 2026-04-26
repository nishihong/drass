# 统一配置管理系统

## 概述

为了解决端口配置硬编码和配置分散的问题，我们实现了一个统一的配置管理系统，支持所有服务和组件的配置需求。

## 架构设计

### 1. 配置文件结构

```
config/
├── app.yaml                 # 主配置文件
├── config_manager.py        # Python配置管理器
├── environments/
│   ├── development.yaml     # 开发环境配置
│   └── production.yaml      # 生产环境配置
└── web/
    └── config.js           # 前端配置（已废弃，使用TypeScript版本）

frontend/src/config/
└── config.ts               # 前端TypeScript配置管理器

env.example                 # 环境变量示例文件
```

### 2. 配置层次结构

1. **环境变量** (最高优先级)
2. **YAML配置文件** (中间优先级)
3. **默认值** (最低优先级)

## 核心组件

### 1. Python配置管理器 (`config/config_manager.py`)

```python
from config_manager import get_config, get_port, get_url

# 获取配置
config = get_config()

# 获取端口
backend_port = get_port('backend')  # 8000

# 获取URL
backend_url = get_url('backend')   # http://localhost:8000

# 获取特定配置
llm_config = config.get_llm_config()
cors_config = config.get_cors_config()
```

### 2. 前端配置管理器 (`frontend/src/config/config.ts`)

```typescript
import { getApiUrl, getWebSocketUrl, isFeatureEnabled } from '../../config/config';

// 获取API URL
const backendUrl = getApiUrl('backend');

// 获取WebSocket URL
const wsUrl = getWebSocketUrl();

// 检查功能是否启用
const fileUploadEnabled = isFeatureEnabled('fileUpload');
```

## 配置项说明

### 服务端口配置

```yaml
ports:
  frontend: 3000
  backend: 8000
  llm: 8001
  embedding: 8002
  reranking: 8003
  document_processor: 8004
  chroma: 8005
  postgres: 5432
  redis: 6379
```

### API端点配置

```yaml
api:
  base_url: "http://localhost"
  frontend_url: "http://localhost:3000"
  backend_url: "http://localhost:8000"
  llm_url: "http://localhost:8001"
  embedding_url: "http://localhost:8002"
  reranking_url: "http://localhost:8003"
```

### 文件上传配置

```yaml
upload:
  max_file_size: 10485760  # 10MB
  allowed_types:
    - "application/pdf"
    - "application/msword"
    - "text/plain"
    - "text/markdown"
    # ... 更多类型
```

### 功能开关

```yaml
features:
  file_upload: true
  websocket: true
  streaming: true
  knowledge_base: true
  experimental_features: false
```

## 使用方法

### 1. 后端服务

```python
# simple_backend.py
from config_manager import get_config

config = get_config()

# 使用配置
port = config.get_port("backend")
cors_origins = config.get_cors_config()["allowed_origins"]
llm_url = config.get_url("llm")
```

### 2. 前端组件

```typescript
// ChatInterface.tsx
import { getApiUrl } from '../../config/config';

const response = await fetch(`${getApiUrl('backend')}/api/v1/chat`, {
  // ...
});
```

### 3. 启动脚本

```bash
# start-simple.sh
CONFIG_FILE="$PROJECT_ROOT/config/app.yaml"
if [ -f "$CONFIG_FILE" ]; then
    FRONTEND_PORT=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['ports']['frontend'])" 2>/dev/null || echo "3000")
    BACKEND_PORT=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['ports']['backend'])" 2>/dev/null || echo "8000")
fi
```

## 环境变量支持

### 前端环境变量

```bash
# .env
VITE_BACKEND_PORT=8000
VITE_FRONTEND_PORT=3000
VITE_BACKEND_URL=http://localhost:8000
VITE_WEBSOCKET_ENABLED=true
VITE_FEATURE_FILE_UPLOAD=true
```

### 后端环境变量

```bash
# 环境变量
OPENROUTER_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
```

## 配置验证

### 测试配置系统

```bash
# 测试Python配置管理器
python3 config/config_manager.py

# 输出示例：
# Configuration Test:
# Frontend Port: 3000
# Backend Port: 8000
# Backend URL: http://localhost:8000
# WebSocket URL: ws://localhost:8000
# File Upload Enabled: True
# Environment: development
```

## 优势

### 1. 统一管理
- 所有配置集中在一个地方
- 避免硬编码和配置分散
- 易于维护和更新

### 2. 环境支持
- 支持开发、测试、生产环境
- 环境变量覆盖配置文件
- 灵活的配置层次

### 3. 类型安全
- TypeScript类型定义
- 编译时错误检查
- IDE智能提示

### 4. 向后兼容
- 保持现有功能不变
- 渐进式迁移
- 默认值支持

## 迁移指南

### 1. 后端服务迁移

**之前：**
```python
LLM_API_BASE = "http://localhost:8001/v1"
port = 8080 if "--port" in sys.argv else 8000
```

**之后：**
```python
from config_manager import get_config
config = get_config()
LLM_API_BASE = f"{config.get_url('llm')}/v1"
port = config.get_port("backend")
```

### 2. 前端组件迁移

**之前：**
```typescript
const response = await fetch('http://localhost:8000/api/v1/chat', {
```

**之后：**
```typescript
import { getApiUrl } from '../../config/config';
const response = await fetch(`${getApiUrl('backend')}/api/v1/chat`, {
```

### 3. 启动脚本迁移

**之前：**
```bash
FRONTEND_PORT=3000
BACKEND_PORT=8080
```

**之后：**
```bash
CONFIG_FILE="$PROJECT_ROOT/config/app.yaml"
FRONTEND_PORT=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['ports']['frontend'])" 2>/dev/null || echo "3000")
BACKEND_PORT=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG_FILE'))['ports']['backend'])" 2>/dev/null || echo "8000")
```

## 未来扩展

### 1. Docker支持
- 环境变量注入
- 配置文件挂载
- 多环境部署

### 2. 配置热重载
- 运行时配置更新
- 服务自动重启
- 配置变更通知

### 3. 配置验证
- 配置项验证
- 依赖关系检查
- 错误提示

### 4. 配置加密
- 敏感信息加密
- 密钥管理
- 安全存储

## 总结

通过实现统一的配置管理系统，我们解决了：

1. ✅ **端口硬编码问题** - 所有端口配置统一管理
2. ✅ **配置分散问题** - 集中配置，易于维护
3. ✅ **环境差异问题** - 支持多环境配置
4. ✅ **类型安全问题** - TypeScript类型支持
5. ✅ **向后兼容问题** - 渐进式迁移

这个系统为项目的可维护性和可扩展性奠定了坚实的基础。

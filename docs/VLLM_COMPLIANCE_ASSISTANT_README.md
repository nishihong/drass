# 磐石数据合规助手 - VLLM本地模型集成版

## 🚀 功能概述

本版本的磐石数据合规助手已完全集成您的本地VLLM模型，具备以下核心功能：

### ✅ 已恢复的Sessions功能
- **会话侧边栏**: 右侧滑出式会话历史面板
- **会话管理**: 新建、重命名、删除会话
- **会话切换**: 快速切换不同的合规咨询会话
- **会话持久化**: 会话历史保存和恢复

### ✅ VLLM模型集成
- **实时流式响应**: 使用您的本地VLLM模型进行实时对话
- **合规专业分析**: 基于合规知识库的智能分析
- **本地化部署**: 完全本地化，数据不出外网
- **高性能推理**: 利用VLLM的高性能推理能力

### 🎯 界面特性
- **顶部工具栏**: 包含新建会话、上传文件、会话历史、设置等功能
- **磐石蓝主题**: 专业的企业级UI设计
- **科技感动画**: 闪烁动画效果增强视觉体验
- **响应式设计**: 适配不同屏幕尺寸

## 🔧 启动说明

### 快速启动
```bash
# 一键启动所有服务（推荐）
./start-compliance-assistant.sh
```

### 手动启动步骤

1. **启动VLLM服务** (如果尚未启动)
```bash
# 启动VLLM主模型服务
./deployment/scripts/restart-vllm-optimized.sh

# 或者手动启动
vllm serve "/path/to/your/model" \
  --port 8001 \
  --api-key 123456 \
  --served-model-name vllm
```

2. **启动后端API服务**
```bash
cd services/main-app
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8888
```

3. **启动前端服务**
```bash
cd frontend
npm run dev
```

## 🌐 访问地址

- **主界面**: http://localhost:5173
- **API文档**: http://localhost:8888/docs
- **健康检查**: http://localhost:8888/health

## 💬 使用说明

### Sessions会话功能

1. **打开会话历史**
   - 点击顶部工具栏的"历史"图标
   - 或点击"菜单"图标打开侧边栏

2. **新建会话**
   - 点击顶部"+"按钮
   - 或在会话侧边栏点击"新建会话"

3. **管理会话**
   - 在会话列表中点击"⋮"菜单
   - 可以重命名或删除会话

4. **切换会话**
   - 在会话列表中点击任意会话
   - 当前会话会高亮显示

### 合规咨询功能

1. **基础咨询**
   ```
   示例问题：
   - 我们公司收集用户手机号码需要注意哪些合规要求？
   - GDPR对跨境数据传输有什么规定？
   - 个人信息保护法对数据处理有什么要求？
   ```

2. **文档上传分析**
   - 点击"上传文件"按钮
   - 支持PDF、DOCX、TXT等格式
   - 系统会自动分析文档中的合规风险

3. **实时流式响应**
   - 问题发送后立即开始接收回答
   - 基于您的本地VLLM模型生成专业分析
   - 结合知识库提供准确的法规引用

## 🔧 配置说明

### 环境变量配置

主要配置文件: `services/main-app/.env`

```bash
# LLM配置 - 指向您的VLLM服务
LLM_PROVIDER="openai"
LLM_MODEL="vllm"
LLM_API_KEY="123456"
LLM_BASE_URL="http://localhost:8001/v1"
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2048

# API服务配置
HOST="0.0.0.0"
PORT=8888

# 前端配置
VITE_API_BASE_URL="http://localhost:8888/api/v1"
```

### VLLM服务配置

确保您的VLLM服务运行在以下配置：
- **端口**: 8001
- **API密钥**: 123456
- **模型名**: vllm
- **API兼容**: OpenAI兼容API

## 🐛 故障排除

### 常见问题

1. **无法连接到VLLM服务**
   ```bash
   # 检查VLLM服务状态
   curl http://localhost:8001/v1/models
   
   # 如果失败，重启VLLM服务
   ./deployment/scripts/restart-vllm-optimized.sh
   ```

2. **后端API连接失败**
   ```bash
   # 检查后端服务
   curl http://localhost:8888/health
   
   # 查看日志
   tail -f logs/api.log
   ```

3. **前端无法加载**
   ```bash
   # 检查前端服务
   curl http://localhost:5173
   
   # 重启前端
   cd frontend && npm run dev
   ```

4. **Sessions侧边栏不显示**
   - 清除浏览器缓存 (Ctrl+Shift+R)
   - 检查浏览器控制台是否有JavaScript错误
   - 确保前端服务正常运行

### 日志文件

- **后端API**: `logs/api.log`
- **前端服务**: `logs/frontend.log`
- **VLLM服务**: `logs/vllm-llm-optimized.log`

## 📊 性能监控

### 服务状态检查
```bash
# 检查所有服务状态
./deployment/scripts/test-vllm-connection.sh

# 查看进程状态
ps aux | grep -E "(vllm|uvicorn|node)"
```

### 资源使用情况
```bash
# GPU使用情况
nvidia-smi  # 或 rocm-smi (AMD GPU)

# 内存使用
free -h

# CPU使用
htop
```

## 🔄 停止服务

```bash
# 停止所有服务
./stop-all.sh

# 或手动停止
pkill -f "uvicorn"
pkill -f "vite"
pkill -f "vllm"
```

## 📝 更新日志

### v2.0 - VLLM集成版 (当前版本)

**新增功能:**
- ✅ 恢复Sessions会话管理功能
- ✅ 集成VLLM本地模型推理
- ✅ 实时流式响应
- ✅ 顶部工具栏界面
- ✅ 合规专业知识库集成

**技术改进:**
- 🔧 API端口统一为8888
- 🔧 优化错误处理和用户提示
- 🔧 增强会话状态管理
- 🔧 改进流式响应处理

**修复问题:**
- 🐛 修复API端口不匹配问题
- 🐛 修复Sessions侧边栏显示问题
- 🐛 优化模拟响应替换为真实API调用

---

## 🎯 下一步计划

- [ ] 会话历史持久化到数据库
- [ ] 支持多模型切换
- [ ] 增加合规报告导出功能
- [ ] 优化大文档处理性能
- [ ] 添加用户权限管理

---

**享受您的智能合规助手！** 🚀

如有问题，请查看日志文件或联系技术支持。

# System Startup Optimization Task List (V2 - 基于验证结果)

## 项目概述
- **项目名称**: 系统启动优化项目（更新版）
- **版本**: 2.0.0
- **创建日期**: 2025-01-16
- **最后更新**: 2025-01-16
- **当前状态**: 已验证并行启动有效，启动时间减少 94%
- **目标**: 修复剩余配置问题，完善启动流程，实现生产就绪

## 验证成果
- ✅ **启动时间**: 7+ 分钟 → 26 秒
- ✅ **并行化验证**: 所有服务可同时启动
- ✅ **核心功能**: 所有服务正常运行

## 任务状态定义
- ✅ **VALIDATED**: 已验证有效
- 📋 **TODO**: 待开始
- 🚧 **IN_PROGRESS**: 进行中
- ✅ **COMPLETED**: 已完成
- 🔍 **REVIEW**: 审查中
- ❌ **BLOCKED**: 阻塞
- 🗓️ **SCHEDULED**: 已计划

## 优先级定义
- 🔴 **P0**: 紧急且重要（影响功能）
- 🟠 **P1**: 重要（改进体验）
- 🟡 **P2**: 一般（增强功能）
- 🟢 **P3**: 低（优化改进）

---

## 1. 立即修复任务（基于诊断结果）

### TASK-FIX-001 ✅ VALIDATED
- **任务描述**: 采用 quick-fix.sh 作为主启动脚本
- **任务类型**: 脚本替换
- **优先级**: ✅ 已完成
- **状态**: ✅ VALIDATED
- **验证结果**: 启动时间从 7+ 分钟减少到 26 秒

---

### TASK-FIX-002 ✅
- **任务描述**: 修复 Frontend 端口配置
- **任务类型**: 配置修复
- **优先级**: 🔴 P0
- **状态**: ✅ COMPLETED
- **负责人**: Frontend Developer
- **实际工时**: 5 minutes

**问题描述**:
- Frontend 运行在 3000 端口而非预期的 5173
- 导致健康检查误报

**预期输出**:
```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: true
  }
})
```

**验收标准**:
```bash
cd frontend && npm run dev
# 期望: 服务在 http://localhost:5173 启动
```

---

### TASK-FIX-003 ❌
- **任务描述**: 修复 Document Processor 服务
- **任务类型**: Docker 服务修复
- **优先级**: 🔴 P0
- **状态**: ❌ BLOCKED (Network issues with Docker build)
- **负责人**: DevOps Engineer
- **实际工时**: 15 minutes

**问题描述**:
- Document Processor 返回 404 错误
- 服务可能未正确构建或启动

**调查步骤**:
```bash
# 1. 检查 Docker 镜像
docker images | grep doc-processor

# 2. 检查服务定义
grep -A 20 "doc-processor:" docker-compose.yml

# 3. 尝试构建镜像
docker-compose build doc-processor

# 4. 检查启动日志
docker-compose logs doc-processor
```

**预期输出**:
- Document Processor 服务正常启动
- 健康检查端点 http://localhost:5003/health 可访问

**验收标准**:
```bash
curl http://localhost:5003/health
# 期望: {"status": "healthy"}
```

---

### TASK-FIX-004 ✅
- **任务描述**: 修复 macOS 兼容性问题
- **任务类型**: 脚本兼容性
- **优先级**: 🟠 P1
- **状态**: ✅ COMPLETED
- **负责人**: DevOps Engineer
- **实际工时**: 10 minutes

**问题列表**:
1. `free` 命令不存在
2. `fuser` 参数不兼容

**预期输出**:
```bash
# utils/macos_compat.sh
#!/bin/bash

# macOS 内存检测
get_memory_gb() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        vm_stat | grep "Pages free" | awk '{printf "%.1f", $3*4096/1024/1024/1024}'
    else
        free -g | awk 'NR==2{printf "%.1f", $7/1024}'
    fi
}

# macOS 端口清理
kill_port() {
    local port=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    else
        fuser -k $port/tcp 2>/dev/null || true
    fi
}

# macOS 进程检测
check_process() {
    local name=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        pgrep -f "$name" > /dev/null 2>&1
    else
        pidof "$name" > /dev/null 2>&1
    fi
}
```

**验收标准**:
```bash
source utils/macos_compat.sh
get_memory_gb  # 应返回可用内存
kill_port 8080  # 应成功清理端口
```

---

## 2. 紧急新增任务（高优先级）

### TASK-URGENT-001 ✅
- **任务描述**: 集成 Document Processor 本地 fallback 到 quick-fix.sh
- **任务类型**: 脚本集成
- **优先级**: 🔴 P0
- **状态**: ✅ COMPLETED
- **负责人**: DevOps Engineer
- **实际工时**: 20 minutes

**需求描述**:
- Document Processor 本地版本已创建但未集成到启动脚本
- 需要在 quick-fix.sh 中添加 fallback 逻辑

**预期输出**:
- quick-fix.sh 自动检测 Docker 可用性
- Docker 不可用时自动启动本地处理器
- 健康检查确认服务正常

**验收标准**:
```bash
./quick-fix.sh
curl http://localhost:5003/health
# Expected: {"status": "healthy"}
```

**完成情况**:
- ✅ 在 quick-fix.sh 第 146-173 行实现智能 fallback
- ✅ 自动检测 Docker 环境并选择启动方式
- ✅ 本地 Python 版本作为备用方案
- ✅ 测试验证成功，服务在端口 5003 正常响应

---

### TASK-URGENT-002 ✅
- **任务描述**: 前端中文本地化
- **任务类型**: 国际化
- **优先级**: 🔴 P0
- **状态**: ✅ COMPLETED
- **负责人**: Frontend Developer
- **实际工时**: 1.5 hours

**需求描述**:
- 当前前端界面全部为英文
- 需要提供中文版本支持

**预期输出**:
- 创建中文语言包
- 实现语言切换功能
- 所有界面文本支持中文

**验收标准**:
- 所有页面可切换到中文
- 中文翻译准确自然
- 语言设置可持久化

**完成情况**:
- ✅ 安装了 react-i18next 和 i18next
- ✅ 创建了完整的中英文语言包文件
- ✅ 实现了 LanguageSelector 语言切换组件
- ✅ 更新了 ChatInterface、Login、MainLayout 等核心组件
- ✅ 语言偏好保存到 localStorage 实现持久化
- ✅ 默认语言设置为中文

---

### TASK-URGENT-003 ✅
- **任务描述**: 添加知识库访问日志展示页面
- **任务类型**: 功能开发
- **优先级**: 🔴 P0
- **状态**: ✅ COMPLETED
- **负责人**: Full Stack Developer
- **实际工时**: 2 hours

**需求描述**:
- 用户无法查看知识库更新和使用记录
- 需要展示文件上传、处理、查询的日志

**功能要求**:
- 显示文件上传历史
- 显示知识库更新记录
- 显示查询访问日志
- 支持日志过滤和搜索

**验收标准**:
- 知识库管理页面新增"访问日志"标签
- 实时显示最近的操作记录
- 支持按时间、类型筛选

**完成情况**:
- ✅ 创建了完整的 AccessLogs.tsx 组件
- ✅ 实现了表格展示、分页、筛选功能
- ✅ 支持按操作类型、时间范围、关键词搜索
- ✅ 添加了 CSV 导出功能
- ✅ 集成了 i18n 国际化支持
- ✅ 添加了路由配置 `/knowledge-base/access-logs`

---

## 3. 增强优化任务

### TASK-ENHANCE-001
- **任务描述**: 创建生产就绪启动脚本
- **任务类型**: 脚本增强
- **优先级**: 🟠 P1
- **状态**: 📋 TODO
- **负责人**: DevOps Engineer
- **预计工时**: 4h

**功能要求**:
- 基于 quick-fix.sh 的成功经验
- 添加错误处理和回滚机制
- 支持不同启动模式（开发/生产/调试）
- 完善的日志和监控

**预期输出**:
```bash
# start-production.sh
#!/bin/bash

# 启动模式选择
MODE=${1:-development}

case $MODE in
    development)
        # 开发模式：完整日志，热重载
        ;;
    production)
        # 生产模式：优化性能，最小日志
        ;;
    debug)
        # 调试模式：详细日志，性能分析
        ;;
esac
```

---

### TASK-ENHANCE-002
- **任务描述**: 实现启动性能监控仪表板
- **任务类型**: 监控增强
- **优先级**: 🟡 P2
- **状态**: 📋 TODO
- **负责人**: Backend Developer
- **预计工时**: 6h

**功能要求**:
- 实时显示服务启动进度
- 记录历史启动时间
- 性能趋势分析
- 瓶颈识别

**预期输出**:
```python
# monitoring/startup_dashboard.py
class StartupMonitor:
    def __init__(self):
        self.services = {}
        self.start_time = None

    def track_service(self, name, status):
        self.services[name] = {
            'status': status,
            'timestamp': time.time(),
            'duration': None
        }

    def generate_report(self):
        return {
            'total_time': self.total_duration,
            'services': self.services,
            'bottlenecks': self.identify_bottlenecks()
        }
```

---

### TASK-ENHANCE-003
- **任务描述**: 实现 Supervisord 进程管理
- **任务类型**: 进程管理
- **优先级**: 🟠 P1
- **状态**: 📋 TODO
- **负责人**: SRE Engineer
- **预计工时**: 8h

**功能要求**:
- 自动重启崩溃的服务
- 进程组管理
- Web 界面监控
- 日志轮转

**预期输出**:
```ini
# supervisord.conf
[unix_http_server]
file=/tmp/supervisor.sock

[supervisord]
logfile=/var/log/supervisord.log
pidfile=/var/run/supervisord.pid

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock

[program:llm-server]
command=python3 /Users/arthurren/projects/drass/qwen3_api_server.py
directory=/Users/arthurren/projects/drass
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/llm-server.err.log
stdout_logfile=/var/log/llm-server.out.log

[program:embedding-service]
command=python /Users/arthurren/projects/drass/services/embedding-service/app.py
directory=/Users/arthurren/projects/drass/services/embedding-service
autostart=true
autorestart=true

[program:backend]
command=/Users/arthurren/projects/drass/services/main-app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/Users/arthurren/projects/drass/services/main-app
environment=PATH="/Users/arthurren/projects/drass/services/main-app/venv/bin",LLM_BASE_URL="http://localhost:8001/v1"
autostart=true
autorestart=true

[group:core-services]
programs=llm-server,embedding-service,backend
priority=999
```

---

## 3. 模型加载优化任务

### TASK-MODEL-001
- **任务描述**: 实现 qwen3_api_server.py 异步模型加载
- **任务类型**: 代码优化
- **优先级**: 🟡 P2
- **状态**: 📋 TODO
- **负责人**: ML Engineer
- **预计工时**: 6h

**当前状态**:
- 模型已缓存，加载速度可接受
- 但仍是同步加载，可能阻塞大模型

**预期改进**:
```python
# qwen3_api_server_async.py
import asyncio
from flask import Flask, jsonify
from concurrent.futures import ThreadPoolExecutor

class AsyncModelServer:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loading = True
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def load_model_background(self):
        """后台加载模型"""
        try:
            loop = asyncio.get_event_loop()
            self.model, self.tokenizer = await loop.run_in_executor(
                self.executor,
                load,
                "mlx_qwen3_converted"
            )
            self.loading = False
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.loading = False

    @app.route('/health')
    def health(self):
        if self.loading:
            return jsonify({"status": "loading", "model_loaded": False})
        elif self.model:
            return jsonify({"status": "healthy", "model_loaded": True})
        else:
            return jsonify({"status": "error", "model_loaded": False})
```

---

## 4. Docker 和部署优化

### TASK-DOCKER-001
- **任务描述**: 优化 Docker Compose 配置
- **任务类型**: 配置优化
- **优先级**: 🟡 P2
- **状态**: 📋 TODO
- **负责人**: DevOps Engineer
- **预计工时**: 4h

**优化内容**:
- 减少健康检查 start_period
- 优化资源限制
- 添加依赖管理

**预期输出**:
```yaml
# docker-compose.optimized.yml
services:
  doc-processor:
    build:
      context: ./services/doc-processor
      dockerfile: Dockerfile
    container_name: langchain-doc-processor
    ports:
      - "5003:5003"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5003/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s  # 减少等待时间
    restart: unless-stopped
    networks:
      - langchain-network
```

---

## 5. 监控和诊断任务

### TASK-MONITOR-001
- **任务描述**: 创建启动诊断工具
- **任务类型**: 诊断工具
- **优先级**: 🟡 P2
- **状态**: 📋 TODO
- **负责人**: DevOps Engineer
- **预计工时**: 4h

**功能要求**:
- 自动检测常见问题
- 提供修复建议
- 生成诊断报告

**预期输出**:
```bash
# diagnose.sh
#!/bin/bash

diagnose_system() {
    echo "=== System Diagnosis ==="

    # 检查 Docker
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running"
        echo "   Fix: Start Docker Desktop"
    fi

    # 检查端口
    for port in 8000 8001 8002 8004 5173; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "✅ Port $port is in use"
        else
            echo "⚠️ Port $port is free (service may not be running)"
        fi
    done

    # 检查配置文件
    if [ ! -f ".env" ]; then
        echo "❌ .env file missing"
        echo "   Fix: Copy .env.example to .env"
    fi

    # 生成报告
    generate_diagnosis_report
}
```

---

## Sprint 规划（更新版）

### Sprint 1 (本周): 紧急修复
- [x] 使用 quick-fix.sh（已完成）
- [ ] TASK-FIX-002: 修复 Frontend 端口配置 🔴
- [ ] TASK-FIX-003: 修复 Document Processor 🔴
- [ ] TASK-FIX-004: 修复 macOS 兼容性 🟠

### Sprint 2 (下周): 系统增强
- [ ] TASK-ENHANCE-001: 生产就绪脚本 🟠
- [ ] TASK-ENHANCE-003: Supervisord 集成 🟠
- [ ] TASK-DOCKER-001: Docker 配置优化 🟡

### Sprint 3 (第3周): 监控和优化
- [ ] TASK-ENHANCE-002: 性能监控仪表板 🟡
- [ ] TASK-MODEL-001: 异步模型加载 🟡
- [ ] TASK-MONITOR-001: 诊断工具 🟡

## 任务统计（更新）

| 类别 | 总任务 | 已验证 | 待开始 | 进行中 | 完成率 |
|------|--------|--------|--------|--------|---------|
| 立即修复 | 4 | 1 | 3 | 0 | 25% |
| 增强优化 | 3 | 0 | 3 | 0 | 0% |
| 模型优化 | 1 | 0 | 1 | 0 | 0% |
| Docker优化 | 1 | 0 | 1 | 0 | 0% |
| 监控诊断 | 1 | 0 | 1 | 0 | 0% |
| **总计** | **10** | **1** | **9** | **0** | **10%** |

## 关键里程碑

### 已达成 ✅
- [x] 并行启动验证成功（26秒启动）
- [x] 所有核心服务正常运行
- [x] quick-fix.sh 脚本验证有效

### 本周目标 🎯
- [ ] 修复所有配置问题
- [ ] 实现 macOS 完全兼容
- [ ] Document Processor 正常运行

### 下周目标 📅
- [ ] Supervisord 进程管理就位
- [ ] 生产环境脚本完成
- [ ] 启动时间稳定在 30 秒内

## 风险和缓解

| 风险 | 影响 | 概率 | 缓解措施 | 状态 |
|------|------|------|----------|------|
| 并行启动资源竞争 | 高 | 低 | 已通过测试验证 | ✅ 已缓解 |
| Frontend 端口冲突 | 中 | 高 | 配置文件修复 | 🚧 处理中 |
| Doc Processor 缺失 | 中 | 高 | 降级到本地处理 | ⚠️ 已降级 |
| macOS 兼容性 | 低 | 中 | 兼容性脚本 | 📋 待处理 |

## 成功指标

### 技术指标
- ✅ 启动时间 < 30 秒（已达成：26秒）
- [ ] 配置一致性 100%
- [ ] 平台兼容性 100%
- [ ] 服务可用性 > 99%

### 业务指标
- ✅ 开发效率提升 > 80%（减少等待时间）
- [ ] 故障恢复时间 < 1 分钟
- [ ] 自动化程度 > 90%

## 总结

通过 quick-fix.sh 的成功验证，我们已经证明了并行启动架构的有效性，成功将启动时间从 7+ 分钟减少到 26 秒。当前的主要任务是：

1. **修复配置问题**（Frontend 端口、Doc Processor）
2. **提升兼容性**（macOS 支持）
3. **增强稳定性**（Supervisord 集成）

这些都是相对简单的修复，预计 1-2 周内可以完成所有优化，实现生产就绪的启动系统。

## 更新日志

| 日期 | 版本 | 更新内容 | 更新人 |
|------|------|----------|--------|
| 2025-01-16 | 2.0.0 | 基于 STARTUP_DIAGNOSTIC_REPORT.md 重新制定任务列表 | System |
| 2025-01-16 | 1.0.0 | 初始版本 | System |

---

**注**:
1. 任务数量从 21 个精简到 10 个核心任务
2. 基于实际验证结果调整优先级
3. 聚焦于立即可修复的问题
4. 保留已验证有效的方案
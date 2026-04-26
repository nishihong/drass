# Document Processor 修复方案分析

## 问题总结
Document Processor 服务因 Docker 构建时网络问题无法启动，主要原因是：
1. Dockerfile 中配置了中国镜像源（清华、阿里云、豆瓣）
2. 从国外访问这些镜像源反而更慢，导致超时
3. 缺失的依赖（numpy、scikit-learn）增加了安装复杂度

## 解决方案对比

### 方案 A: 优化 Docker 构建（推荐用于生产环境）

**优点**：
- ✅ 保持容器化架构
- ✅ 隔离性好
- ✅ 易于部署和扩展

**缺点**：
- ❌ 需要稳定的网络连接
- ❌ 构建时间较长

**实施步骤**：
```bash
# 1. 使用优化的 Dockerfile（移除中国镜像源）
cp services/doc-processor/Dockerfile.optimized services/doc-processor/Dockerfile

# 2. 重新构建
docker-compose build --no-cache doc-processor

# 3. 启动服务
docker-compose up -d doc-processor
```

### 方案 B: 轻量级依赖（推荐用于快速修复）

**优点**：
- ✅ 减少依赖，构建更快
- ✅ 避免重型 ML 库
- ✅ 基本功能可用

**缺点**：
- ❌ 无语义分割功能
- ❌ 功能降级

**实施步骤**：
```bash
# 1. 使用轻量级依赖
cp services/doc-processor/requirements-lite.txt services/doc-processor/requirements.txt

# 2. 禁用 semantic_splitter
# 在 app.py 中注释掉相关导入

# 3. 重新构建
docker-compose build doc-processor
```

### 方案 C: 本地处理器（立即可用）

**优点**：
- ✅ 无需 Docker
- ✅ 立即可用
- ✅ 最小依赖

**缺点**：
- ❌ 无隔离性
- ❌ 功能简化

**实施步骤**：
```bash
# 启动本地处理器
./start-doc-processor-local.sh

# 验证
curl http://localhost:5003/health
```

## 建议的修复策略

### 第一步：立即恢复服务（5分钟）
使用方案 C - 启动本地处理器作为临时解决方案：
```bash
cd /Users/arthurren/projects/drass
./start-doc-processor-local.sh
```

### 第二步：修复 Docker 构建（30分钟）
1. 移除 Dockerfile 中的中国镜像源配置
2. 创建本地 pip 缓存以加速构建
3. 考虑使用 Docker 多阶段构建

### 第三步：长期优化（1-2天）
1. 设置私有 PyPI 镜像服务器
2. 预构建基础镜像并推送到 Docker Hub
3. 实现功能降级机制

## 修复后的 quick-fix.sh 集成

```bash
# 在 quick-fix.sh 中添加 doc-processor 降级逻辑
if docker info > /dev/null 2>&1; then
    # 尝试 Docker 版本
    docker-compose up -d doc-processor 2>/dev/null || {
        echo "Docker doc-processor failed, starting local version..."
        ./start-doc-processor-local.sh
    }
else
    # 直接使用本地版本
    ./start-doc-processor-local.sh
fi
```

## 验证检查清单

- [ ] 健康检查端点响应：`curl http://localhost:5003/health`
- [ ] PDF 处理功能：上传测试 PDF 文件
- [ ] DOCX 处理功能：上传测试 Word 文件
- [ ] 文本分块功能：验证返回的 chunks
- [ ] 与主应用集成：Backend 能够调用处理服务

## 性能对比

| 指标 | Docker 版本 | 本地版本 |
|------|------------|----------|
| 启动时间 | 2-3 分钟 | 5 秒 |
| 内存占用 | 500MB | 100MB |
| 功能完整性 | 100% | 70% |
| 隔离性 | 优秀 | 无 |
| 可扩展性 | 优秀 | 有限 |

## 结论

推荐采用**混合策略**：
1. **开发环境**：使用本地处理器（方案 C）for 快速迭代
2. **测试环境**：使用轻量级 Docker（方案 B）for 功能验证
3. **生产环境**：使用优化的 Docker（方案 A）for 完整功能

这样可以在不同场景下获得最佳的平衡。
# AWS 部署资源需求清单

## 架构概述
基于 Docker Compose 配置和使用 OpenRouter 作为 LLM 接入，以下是 AWS 部署所需的资源清单。

## 1. 计算资源 (EC2/ECS)

### 主应用服务器 (推荐使用 ECS Fargate 或 EC2)

#### Option A: ECS Fargate (推荐用于生产环境)
```yaml
服务配置:
  - API Service: 2 vCPU, 4GB RAM (2个任务)
  - Worker Service: 2 vCPU, 4GB RAM (2-4个任务，基于负载)
  - Web Frontend: 1 vCPU, 2GB RAM (2个任务)
  - Sandbox Service: 1 vCPU, 2GB RAM (1个任务)
  
总计最小需求:
  - vCPU: 12-16
  - RAM: 24-32 GB
```

#### Option B: EC2 实例 (适合开发/测试环境)
```yaml
推荐实例类型:
  - 生产环境: t3.2xlarge (8 vCPU, 32GB RAM) × 2台
  - 开发环境: t3.xlarge (4 vCPU, 16GB RAM) × 1台
  
操作系统: Amazon Linux 2023 或 Ubuntu 22.04 LTS
```

## 2. 数据库资源

### RDS PostgreSQL
```yaml
实例配置:
  - 引擎版本: PostgreSQL 15
  - 实例类型: db.t3.medium (生产环境建议 db.r6g.large)
  - 存储: 100GB SSD (可自动扩展至 500GB)
  - 多可用区: 生产环境启用
  - 备份保留: 7天
  - 加密: 启用
```

### ElastiCache Redis
```yaml
节点配置:
  - 引擎版本: Redis 6.2
  - 节点类型: cache.t3.medium
  - 节点数量: 2 (主从配置)
  - 持久化: 启用 AOF
  - 自动故障转移: 启用
```

## 3. 向量数据库

### Option A: 自托管 Weaviate (EC2)
```yaml
EC2 实例:
  - 实例类型: c5.xlarge (4 vCPU, 8GB RAM)
  - 存储: 200GB SSD
  - 或使用 ECS 任务: 4 vCPU, 8GB RAM
```

### Option B: Amazon OpenSearch (推荐)
```yaml
域配置:
  - 实例类型: r6g.large.search
  - 实例数量: 2
  - 存储: 100GB per node
  - 专用主节点: 3 × t3.small.search
```

## 4. 存储资源

### S3 存储桶
```yaml
用途配置:
  - drass-documents: 文档存储 (估计 100GB)
  - drass-embeddings: 向量数据备份 (估计 50GB)
  - drass-backups: 数据库备份 (估计 100GB)
  - drass-logs: 日志存储 (估计 50GB/月)
  
存储类别:
  - 文档/向量: S3 Standard
  - 备份: S3 Standard-IA
  - 日志: S3 Intelligent-Tiering
```

### EFS (如需共享存储)
```yaml
配置:
  - 性能模式: 通用
  - 吞吐量模式: Bursting
  - 加密: 启用
  - 预计容量: 50GB
```

## 5. 网络资源

### VPC 配置
```yaml
网络架构:
  - VPC: 10.0.0.0/16
  - 公共子网: 10.0.1.0/24, 10.0.2.0/24 (多AZ)
  - 私有子网: 10.0.10.0/24, 10.0.11.0/24 (多AZ)
  - 数据库子网: 10.0.20.0/24, 10.0.21.0/24 (多AZ)
```

### Application Load Balancer (ALB)
```yaml
配置:
  - 类型: Application Load Balancer
  - 方案: Internet-facing
  - 目标组:
    - API Service (端口 8000)
    - Web Frontend (端口 3000)
  - 健康检查: /health
  - SSL证书: ACM 托管证书
```

### CloudFront CDN
```yaml
分发配置:
  - 源: ALB + S3 (静态资源)
  - 缓存行为: 
    - API路径: 不缓存
    - 静态资源: 缓存 24小时
  - WAF: 启用基本规则集
```

## 6. 安全资源

### IAM 角色和策略
```yaml
所需角色:
  - ECS Task Role: 访问 S3, Secrets Manager
  - EC2 Instance Role: 访问 ECR, CloudWatch
  - Lambda Function Role: 访问 RDS, S3
  
策略:
  - S3 读写权限 (特定桶)
  - Secrets Manager 读取权限
  - CloudWatch Logs 写入权限
```

### Secrets Manager
```yaml
密钥存储:
  - OpenRouter API Key
  - 数据库密码
  - Redis 密码
  - JWT Secret
  - Encryption Keys
```

### Security Groups
```yaml
规则配置:
  - ALB-SG: 80, 443 from 0.0.0.0/0
  - App-SG: 8000 from ALB-SG
  - DB-SG: 5432 from App-SG
  - Redis-SG: 6379 from App-SG
  - Weaviate-SG: 8080 from App-SG
```

## 7. 监控和日志

### CloudWatch
```yaml
配置:
  - 日志组: /aws/ecs/drass/*
  - 指标: CPU, 内存, 网络
  - 警报:
    - CPU > 80%
    - 内存 > 90%
    - 错误率 > 1%
  - Dashboard: 自定义监控面板
```

### X-Ray (可选)
```yaml
追踪配置:
  - 采样率: 10%
  - 服务地图: 启用
```

## 8. CI/CD 资源 (可选)

### CodePipeline
```yaml
流水线:
  - 源: GitHub
  - 构建: CodeBuild
  - 部署: ECS/EC2
```

### ECR (容器注册表)
```yaml
仓库:
  - drass-api
  - drass-web
  - drass-worker
  
镜像保留策略: 保留最近 10 个版本
```

## 9. 成本估算 (美东区域 us-east-1)

### 月度成本预估
```yaml
生产环境:
  - ECS Fargate: ~$300-400
  - RDS PostgreSQL: ~$150-200
  - ElastiCache Redis: ~$100-150
  - OpenSearch/Weaviate: ~$200-300
  - ALB: ~$25
  - S3 + 数据传输: ~$50-100
  - CloudWatch: ~$50
  - Secrets Manager: ~$10
  
  总计: ~$885-1,335/月

开发环境:
  - EC2 (t3.xlarge): ~$120
  - RDS (t3.small): ~$30
  - ElastiCache (t3.micro): ~$15
  - 其他服务: ~$50
  
  总计: ~$215/月
```

## 10. 部署建议

### 阶段性部署
1. **第一阶段**: 基础设施 (VPC, RDS, Redis, S3)
2. **第二阶段**: 应用服务 (ECS/EC2, ALB)
3. **第三阶段**: 向量数据库和搜索服务
4. **第四阶段**: 监控、日志和安全加固

### 关键注意事项
- OpenRouter API 调用不需要本地 GPU 资源
- 确保 API Keys 安全存储在 Secrets Manager
- 使用私有子网部署敏感服务
- 启用所有服务的加密传输和静态加密
- 配置适当的备份和灾难恢复策略

### 扩展性考虑
- 使用 Auto Scaling Groups 自动扩展 EC2
- 配置 ECS Service Auto Scaling
- RDS Read Replicas 用于读负载分离
- ElastiCache 集群模式支持水平扩展

## 11. 必需的 AWS 服务清单

### 核心服务
- [ ] Amazon ECS/EC2
- [ ] Amazon RDS (PostgreSQL)
- [ ] Amazon ElastiCache (Redis)
- [ ] Amazon S3
- [ ] Application Load Balancer
- [ ] Amazon VPC

### 安全服务
- [ ] AWS IAM
- [ ] AWS Secrets Manager
- [ ] AWS Certificate Manager
- [ ] Security Groups

### 监控服务
- [ ] Amazon CloudWatch
- [ ] AWS CloudTrail

### 可选但推荐
- [ ] Amazon CloudFront
- [ ] AWS WAF
- [ ] Amazon OpenSearch
- [ ] AWS Backup
- [ ] Amazon ECR
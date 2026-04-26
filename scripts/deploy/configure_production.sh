#!/bin/bash

# 生产环境配置优化脚本

set -e

echo "🔧 开始配置生产环境参数..."

# 创建生产环境配置目录
mkdir -p /home/qwkj/drass/config/production
mkdir -p /home/qwkj/drass/logs/production

# 1. 优化后端服务配置
echo "📝 配置后端服务参数..."

# 创建生产环境配置文件
cat > /home/qwkj/drass/config/production/backend.env << 'EOF'
# 生产环境后端配置
APP_NAME="Drass Compliance Assistant - Production"
ENVIRONMENT="production"
DEBUG=false
LOG_LEVEL="WARNING"

# 服务器配置优化
HOST="0.0.0.0"
PORT=8888
WORKERS=4
WORKER_CLASS="uvicorn.workers.UvicornWorker"

# 数据库连接池优化
DATABASE_URL="sqlite:///./data/production.db"
DB_ECHO=false
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# 缓存配置优化
CACHE_ENABLED=true
CACHE_TTL=1800
CACHE_MAX_SIZE=1000

# 性能优化参数
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=300
KEEP_ALIVE_TIMEOUT=65

# 监控配置
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30

# 安全配置
SECRET_KEY="production-secret-key-change-in-real-deployment"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# 文件上传优化
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_CHUNK_SIZE=8192
UPLOAD_TIMEOUT=300

# 向量存储优化
VECTOR_STORE_TYPE="chroma"
CHROMA_HOST="localhost"
CHROMA_PORT=8005
CHROMA_PERSIST_DIRECTORY="/home/qwkj/drass/data/chromadb_production"
COLLECTION_NAME="drass_documents_production"

# 文档处理优化
MAX_CHUNK_SIZE=800
CHUNK_OVERLAP=100
BATCH_SIZE=10
PROCESSING_TIMEOUT=600

# LLM配置优化
LLM_PROVIDER="openai"
LLM_MODEL="vllm"
LLM_API_KEY="123456"
LLM_BASE_URL="http://localhost:8001/v1"
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1024
LLM_TIMEOUT=120

# 嵌入配置优化
EMBEDDING_PROVIDER="openai"
EMBEDDING_MODEL="Qwen3-Embedding-8B"
EMBEDDING_API_KEY="123456"
EMBEDDING_API_BASE="http://localhost:8010/v1"
EMBEDDING_DIMENSION=1024
EMBEDDING_BATCH_SIZE=32

# 重排序配置
RERANKING_ENABLED=true
RERANKING_PROVIDER="custom"
RERANKING_MODEL="Qwen3-Reranker-8B"
RERANKING_API_KEY="123456"
RERANKING_API_BASE="http://localhost:8012/v1"

# 限流配置
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BURST=50

# 功能开关
ENABLE_STREAMING=true
ENABLE_AGENT=true
ENABLE_MEMORY=true
ENABLE_TOOLS=true
ENABLE_AUDIT=true
ENABLE_MONITORING=true

# 日志配置
LOG_FORMAT="json"
LOG_FILE="/home/qwkj/drass/logs/production/backend.log"
LOG_ROTATION="daily"
LOG_RETENTION=30

# 性能监控
PERFORMANCE_MONITORING=true
SLOW_QUERY_THRESHOLD=5.0
MEMORY_USAGE_THRESHOLD=80
CPU_USAGE_THRESHOLD=80
EOF

# 2. 创建系统服务配置
echo "🔧 配置系统服务..."

# 创建systemd服务文件
sudo tee /etc/systemd/system/drass-api-production.service > /dev/null << 'EOF'
[Unit]
Description=Drass Compliance Assistant API - Production
After=network.target

[Service]
Type=exec
User=qwkj
Group=qwkj
WorkingDirectory=/home/qwkj/drass/services/main-app
Environment=PATH=/home/qwkj/drass/venv/bin
ExecStart=/home/qwkj/drass/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8888 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=drass-api

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/qwkj/drass/data
ReadWritePaths=/home/qwkj/drass/logs

[Install]
WantedBy=multi-user.target
EOF

# 3. 创建Nginx配置
echo "🌐 配置Nginx反向代理..."

sudo tee /etc/nginx/sites-available/drass-production > /dev/null << 'EOF'
upstream drass_backend {
    server 127.0.0.1:8888;
    keepalive 32;
}

upstream drass_frontend {
    server 127.0.0.1:5173;
    keepalive 16;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 客户端最大请求体大小
    client_max_body_size 100M;
    
    # 超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 300s;
    
    # API代理
    location /api/ {
        proxy_pass http://drass_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 缓存设置
        proxy_cache_bypass $http_upgrade;
        proxy_no_cache $cookie_nocache $arg_nocache$arg_comment;
        
        # 压缩
        gzip on;
        gzip_types application/json application/javascript text/css text/plain;
    }
    
    # WebSocket代理
    location /ws/ {
        proxy_pass http://drass_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 前端代理
    location / {
        proxy_pass http://drass_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 静态资源缓存
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 健康检查
    location /health {
        proxy_pass http://drass_backend/health;
        access_log off;
    }
}
EOF

# 4. 创建监控配置
echo "📊 配置监控系统..."

cat > /home/qwkj/drass/config/production/monitoring.yml << 'EOF'
# 生产环境监控配置
monitoring:
  enabled: true
  interval: 30s
  
  # 系统监控
  system:
    cpu_threshold: 80
    memory_threshold: 85
    disk_threshold: 90
    
  # 应用监控
  application:
    response_time_threshold: 5.0
    error_rate_threshold: 5.0
    throughput_threshold: 1000
    
  # 数据库监控
  database:
    connection_pool_threshold: 80
    query_time_threshold: 2.0
    slow_query_threshold: 5.0
    
  # 缓存监控
  cache:
    hit_rate_threshold: 70
    memory_usage_threshold: 80
    
  # 告警配置
  alerts:
    email:
      enabled: true
      recipients: ["admin@yourdomain.com"]
    webhook:
      enabled: true
      url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    
  # 日志监控
  logs:
    error_patterns:
      - "ERROR"
      - "CRITICAL"
      - "Exception"
      - "Traceback"
    warning_patterns:
      - "WARNING"
      - "WARN"
      - "DeprecationWarning"
EOF

# 5. 创建备份配置
echo "💾 配置备份策略..."

cat > /home/qwkj/drass/config/production/backup.yml << 'EOF'
# 生产环境备份配置
backup:
  enabled: true
  
  # 数据库备份
  database:
    schedule: "0 2 * * *"  # 每天凌晨2点
    retention: 30  # 保留30天
    compression: true
    
  # 文件备份
  files:
    schedule: "0 3 * * *"  # 每天凌晨3点
    retention: 7  # 保留7天
    include:
      - "/home/qwkj/drass/data/uploads"
      - "/home/qwkj/drass/data/chromadb_production"
    exclude:
      - "*.tmp"
      - "*.log"
      
  # 配置备份
  config:
    schedule: "0 1 * * *"  # 每天凌晨1点
    retention: 90  # 保留90天
    include:
      - "/home/qwkj/drass/config"
      - "/home/qwkj/drass/services/main-app/app"
      
  # 备份存储
  storage:
    local:
      path: "/home/qwkj/drass/backups"
    remote:
      enabled: false
      # s3:
      #   bucket: "drass-backups"
      #   region: "us-west-2"
EOF

# 6. 创建日志轮转配置
echo "📝 配置日志轮转..."

sudo tee /etc/logrotate.d/drass-production > /dev/null << 'EOF'
/home/qwkj/drass/logs/production/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 qwkj qwkj
    postrotate
        systemctl reload drass-api-production
    endscript
}
EOF

# 7. 创建性能优化脚本
echo "⚡ 创建性能优化脚本..."

cat > /home/qwkj/drass/scripts/optimize_production.sh << 'EOF'
#!/bin/bash

# 生产环境性能优化脚本

echo "⚡ 开始生产环境性能优化..."

# 1. 系统参数优化
echo "🔧 优化系统参数..."

# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
sudo tee -a /etc/sysctl.conf > /dev/null << 'SYSCTL'
# 网络优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# 内存优化
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# 文件系统优化
fs.file-max = 2097152
SYSCTL

# 应用内核参数
sudo sysctl -p

# 2. 数据库优化
echo "🗄️ 优化数据库配置..."

# 创建SQLite优化配置
cat > /home/qwkj/drass/config/production/sqlite_optimize.sql << 'SQL'
-- SQLite性能优化
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;
PRAGMA optimize;
SQL

# 3. 创建启动优化脚本
cat > /home/qwkj/drass/scripts/start_production.sh << 'START'
#!/bin/bash

# 生产环境启动脚本

echo "🚀 启动生产环境服务..."

# 设置环境变量
export ENVIRONMENT=production
export LOG_LEVEL=WARNING
export WORKERS=4

# 启动VLLM服务
echo "启动VLLM服务..."
cd /home/qwkj/drass
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model /home/qwkj/drass/models/DeepSeek-R1-0528-Qwen3-8B \
    --host 0.0.0.0 \
    --port 8001 \
    --api-key 123456 \
    --served-model-name vllm \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.8 \
    --tensor-parallel-size 1 \
    --trust-remote-code \
    > logs/vllm_production.log 2>&1 &

# 启动嵌入服务
echo "启动嵌入服务..."
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model /home/qwkj/drass/models/Qwen3-Embedding-8B \
    --host 0.0.0.0 \
    --port 8010 \
    --api-key 123456 \
    --served-model-name Qwen3-Embedding-8B \
    --max-model-len 2048 \
    --gpu-memory-utilization 0.6 \
    --tensor-parallel-size 1 \
    --trust-remote-code \
    > logs/embedding_production.log 2>&1 &

# 启动ChromaDB
echo "启动ChromaDB..."
nohup chroma run --host 0.0.0.0 --port 8005 --path /home/qwkj/drass/data/chromadb_production \
    > logs/chromadb_production.log 2>&1 &

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 启动后端API
echo "启动后端API..."
sudo systemctl start drass-api-production
sudo systemctl enable drass-api-production

# 启动前端
echo "启动前端服务..."
cd /home/qwkj/drass/frontend
nohup npm run build && npm run preview -- --host 0.0.0.0 --port 5173 \
    > ../logs/frontend_production.log 2>&1 &

# 启动Nginx
echo "启动Nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

echo "✅ 生产环境服务启动完成！"
echo "🌐 访问地址: http://yourdomain.com"
echo "📊 监控地址: http://yourdomain.com:9090"
START

chmod +x /home/qwkj/drass/scripts/start_production.sh

# 8. 创建健康检查脚本
echo "🏥 创建健康检查脚本..."

cat > /home/qwkj/drass/scripts/health_check_production.sh << 'HEALTH'
#!/bin/bash

# 生产环境健康检查脚本

echo "🏥 执行生产环境健康检查..."

# 检查服务状态
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    
    if curl -s -f "http://localhost:$port$endpoint" > /dev/null; then
        echo "✅ $service_name (端口 $port) - 正常"
        return 0
    else
        echo "❌ $service_name (端口 $port) - 异常"
        return 1
    fi
}

# 检查所有服务
echo "检查服务状态..."
check_service "VLLM服务" 8001 "/health"
check_service "嵌入服务" 8010 "/health"
check_service "ChromaDB" 8005 "/api/v1/heartbeat"
check_service "后端API" 8888 "/health"
check_service "前端服务" 5173

# 检查系统资源
echo "检查系统资源..."
echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "内存使用率: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "磁盘使用率: $(df -h / | awk 'NR==2{print $5}')"

# 检查日志错误
echo "检查最近错误..."
if [ -f "/home/qwkj/drass/logs/production/backend.log" ]; then
    error_count=$(tail -n 100 /home/qwkj/drass/logs/production/backend.log | grep -c "ERROR\|CRITICAL")
    echo "最近100行日志中的错误数量: $error_count"
fi

echo "✅ 健康检查完成"
HEALTH

chmod +x /home/qwkj/drass/scripts/health_check_production.sh

echo "✅ 生产环境配置完成！"
echo ""
echo "📋 配置摘要："
echo "  ✅ 后端服务配置优化"
echo "  ✅ 系统服务配置"
echo "  ✅ Nginx反向代理配置"
echo "  ✅ 监控系统配置"
echo "  ✅ 备份策略配置"
echo "  ✅ 日志轮转配置"
echo "  ✅ 性能优化脚本"
echo "  ✅ 启动脚本"
echo "  ✅ 健康检查脚本"
echo ""
echo "🚀 启动生产环境: ./scripts/start_production.sh"
echo "🏥 健康检查: ./scripts/health_check_production.sh"
echo "⚡ 性能优化: ./scripts/optimize_production.sh"

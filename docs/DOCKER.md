# Docker Guide for Drass Dify Platform

This guide explains how to deploy and use the complete Dify platform with Drass applications using Docker.

## 🐳 Overview

The Docker setup is based on the [official Dify documentation](https://docs.dify.ai/zh-hans/getting-started/install-self-hosted/docker-compose) and includes:

- **Complete Dify Platform**: Full-featured AI application development platform
- **Core Services**: API, Worker, Web frontend, Database, Redis, Weaviate
- **Security**: SSRF proxy, Sandbox for code execution
- **Reverse Proxy**: Nginx with SSL support
- **Monitoring**: Prometheus and Grafana (optional)
- **Drass Applications**: Pre-configured data regulation and legal applications

## 🚀 One-Click Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available
- Python 3.7+ (for deployment scripts)

### Quick Start
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run one-click deployment
./deploy.sh
```

This will:
1. ✅ Check all prerequisites
2. 🚀 Deploy the complete Dify platform
3. 👤 Set up admin account automatically
4. 📥 Import Drass applications
5. 🌐 Make platform available at http://localhost

## 🏗️ Service Architecture

### Core Dify Services
- **api**: Dify API service (port 5001)
- **worker**: Celery worker for background tasks
- **web**: Dify web frontend (port 3000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **weaviate**: Vector database for embeddings (port 8080)

### Security Services
- **ssrf_proxy**: SSRF protection proxy (port 3128)
- **sandbox**: Code execution sandbox

### Infrastructure Services
- **nginx**: Reverse proxy (ports 80, 443)
- **prometheus**: Metrics collection (port 9090)
- **grafana**: Monitoring dashboards (port 3000)

## 🔧 Deployment Options

### 1. One-Click Deployment (Recommended)
```bash
./deploy.sh
```

### 2. Python Script Deployment
```bash
# Deploy without monitoring
python3 scripts/dify-deploy.py

# Deploy with monitoring
python3 scripts/dify-deploy.py --monitoring
```

### 3. Manual Docker Compose
```bash
# Start core services
docker-compose up -d db redis weaviate

# Start Dify services
docker-compose up -d api worker web

# Start optional services
docker-compose up -d ssrf_proxy sandbox

# Start monitoring (optional)
docker-compose --profile monitoring up -d
```

## 📊 Platform Access

### After Deployment
- **Main Platform**: http://localhost
- **Admin Setup**: http://localhost/install (first time only)
- **API Documentation**: http://localhost/v1
- **Health Check**: http://localhost/health

### Default Credentials
- **Email**: admin@drass.local
- **Password**: admin123

## 🗄️ Data Management

### Persistent Data
- **PostgreSQL**: `postgres_data` volume
- **Redis**: `redis_data` volume
- **Weaviate**: `weaviate_data` volume
- **Application Data**: `./data/` directory

### Backup and Restore
```bash
# Backup database
docker exec drass-db pg_dump -U dify dify > backup.sql

# Restore database
docker exec -i drass-db psql -U dify dify < backup.sql
```

## 🔒 Security Features

### Network Security
- All services run in isolated `drass-network`
- Internal communication only between services
- External access only through Nginx proxy

### SSRF Protection
- Dedicated SSRF proxy service
- Blocks access to local network ranges
- Configurable access controls

### Code Execution Safety
- Sandboxed code execution environment
- Isolated from host system
- Resource limits and timeouts

## 📈 Monitoring and Observability

### Prometheus Metrics
- **Application Metrics**: All Dify services
- **Infrastructure Metrics**: Database, Redis, Weaviate
- **Custom Metrics**: Drass application specific

### Grafana Dashboards
- **Pre-configured**: Dify platform monitoring
- **Custom Dashboards**: Drass application metrics
- **Real-time**: Live data visualization

### Health Checks
```bash
# Platform health
curl http://localhost/health

# Service health
docker-compose ps

# Individual service health
docker-compose exec api curl -f http://localhost:5001/health
```

## 🛠️ Management Commands

### Service Management
```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Application Management
```bash
# View Drass applications
docker-compose exec db psql -U dify -d dify -c "SELECT * FROM drass_applications;"

# Update application configs
# Edit files in apps/ directory, then restart services
```

### Monitoring Management
```bash
# Start monitoring
docker-compose --profile monitoring up -d

# Stop monitoring
docker-compose --profile monitoring down

# View monitoring logs
docker-compose logs prometheus grafana
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Platform Not Starting
```bash
# Check service logs
docker-compose logs api

# Check database connectivity
docker-compose exec db pg_isready -U dify

# Check Redis connectivity
docker-compose exec redis redis-cli ping
```

#### 2. Memory Issues
```bash
# Check available memory
docker system info --format '{{.MemTotal}}'

# Increase Docker memory limit in Docker Desktop
# Settings > Resources > Memory: 4GB+
```

#### 3. Port Conflicts
```bash
# Check port usage
lsof -i :80
lsof -i :443
lsof -i :3000

# Stop conflicting services
sudo lsof -ti:80 | xargs kill -9
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
docker-compose up -d

# View detailed logs
docker-compose logs -f --tail=100
```

## 🚀 Production Deployment

### Environment Configuration
```bash
# Update .env file with production values
cp .env .env.production
# Edit .env.production with secure values

# Use production environment
docker-compose --env-file .env.production up -d
```

### SSL Configuration
```bash
# Place SSL certificates
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# Update nginx configuration for HTTPS
# Edit nginx/dify.conf
```

### Scaling
```bash
# Scale API services
docker-compose up -d --scale api=3 --scale worker=3

# Scale with load balancer
docker-compose up -d --scale api=3 --scale worker=3 nginx
```

## 📚 Additional Resources

- [Official Dify Documentation](https://docs.dify.ai/)
- [Dify Docker Deployment](https://docs.dify.ai/zh-hans/getting-started/install-self-hosted/docker-compose)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Redis Docker Image](https://hub.docker.com/_/redis)
- [Weaviate Docker Image](https://hub.docker.com/r/semitechnologies/weaviate)
- [Nginx Docker Image](https://hub.docker.com/_/nginx)
- [Prometheus Docker Image](https://hub.docker.com/r/prom/prometheus)
- [Grafana Docker Image](https://hub.docker.com/r/grafana/grafana)

## 🆘 Getting Help

### Support Channels
1. Check service logs: `docker-compose logs -f`
2. Verify service status: `docker-compose ps`
3. Check health endpoints: `curl http://localhost/health`
4. Review configuration files in `config/` directory

### Common Commands Reference
```bash
# Full system status
docker-compose ps && docker stats --no-stream

# Service logs with timestamps
docker-compose logs -t -f

# Execute commands in containers
docker-compose exec api python -c "import os; print(os.environ.get('EDITION'))"
docker-compose exec db psql -U dify -d dify -c "SELECT version();"
```

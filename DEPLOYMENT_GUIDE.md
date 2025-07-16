# Wiki Entry Impact Assessment System - Deployment Guide
# 维基条目影响评估系统 - 部署指南

## Prerequisites / 先决条件

### System Requirements / 系统要求
- **Python 3.9+**: Backend runtime environment
- **Node.js 18+**: Frontend development and build environment
- **PostgreSQL 13+**: Primary database
- **Redis 6+**: Caching and session storage
- **Docker & Docker Compose**: Containerization (recommended)

### Development Tools / 开发工具
- **Git**: Version control
- **VS Code** (recommended): IDE with Python and React extensions
- **Postman**: API testing
- **pgAdmin**: PostgreSQL administration (optional)

## Quick Start / 快速开始

### 1. Clone the Repository / 克隆仓库
```bash
git clone https://gitlab.scss.tcd.ie/jucui/wiki_entry_impact.git
cd wiki_entry_impact
```

### 2. Environment Setup / 环境设置
```bash
# Copy environment configuration
cp env.example .env

# Edit environment variables
nano .env
```

### 3. Install Dependencies / 安装依赖

#### Backend Dependencies / 后端依赖
```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Frontend Dependencies / 前端依赖
```bash
cd frontend
npm install
cd ..
```

### 4. Database Setup / 数据库设置

#### Using Docker (Recommended) / 使用Docker（推荐）
```bash
# Start PostgreSQL and Redis with Docker Compose
docker-compose up -d db redis

# Wait for services to start
sleep 10

# Run database migrations
cd backend
python -m alembic upgrade head
cd ..
```

#### Manual Setup / 手动设置
```bash
# Install PostgreSQL and Redis locally
# Create database
createdb wiki_impact

# Run migrations
cd backend
python -m alembic upgrade head
cd ..
```

### 5. Start Development Servers / 启动开发服务器

#### Option 1: Using NPM Scripts (Recommended) / 选项1：使用NPM脚本（推荐）
```bash
# Install root dependencies
npm install

# Start both backend and frontend
npm run dev
```

#### Option 2: Manual Start / 选项2：手动启动
```bash
# Terminal 1: Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 6. Access the Application / 访问应用程序
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Production Deployment / 生产部署

### Docker Deployment / Docker部署

#### 1. Build Production Images / 构建生产镜像
```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Or build individually
docker build -t wiki-impact-backend ./backend
docker build -t wiki-impact-frontend ./frontend
```

#### 2. Production Environment / 生产环境
```bash
# Create production environment file
cp env.example .env.prod

# Edit production settings
nano .env.prod

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment / Kubernetes部署

#### 1. Prepare Kubernetes Manifests / 准备Kubernetes清单
```bash
# Create namespace
kubectl create namespace wiki-impact

# Apply configurations
kubectl apply -f k8s/
```

#### 2. Configure Secrets / 配置密钥
```bash
# Database credentials
kubectl create secret generic db-credentials \
  --from-literal=username=postgres \
  --from-literal=password=your-secure-password \
  -n wiki-impact

# Application secrets
kubectl create secret generic app-secrets \
  --from-literal=secret-key=your-jwt-secret \
  --from-literal=redis-password=your-redis-password \
  -n wiki-impact
```

### Cloud Deployment Options / 云部署选项

#### AWS Deployment / AWS部署
```bash
# Using AWS ECS
aws ecs create-cluster --cluster-name wiki-impact-cluster

# Using AWS EKS
eksctl create cluster --name wiki-impact --region us-west-2
```

#### Google Cloud Deployment / Google Cloud部署
```bash
# Using Google Cloud Run
gcloud run deploy wiki-impact-api \
  --image gcr.io/your-project/wiki-impact-backend \
  --platform managed \
  --region us-central1

# Using Google Kubernetes Engine
gcloud container clusters create wiki-impact-cluster \
  --zone us-central1-a
```

## Configuration / 配置

### Environment Variables / 环境变量

#### Required Variables / 必需变量
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/wiki_impact
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=wiki_impact

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key
```

#### Optional Variables / 可选变量
```bash
# Application Settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# Wikipedia API
WIKIPEDIA_API_URL=https://en.wikipedia.org/w/api.php
WIKIPEDIA_RATE_LIMIT=10
```

### Database Configuration / 数据库配置

#### Production Database Setup / 生产数据库设置
```sql
-- Create production database
CREATE DATABASE wiki_impact_prod;

-- Create application user
CREATE USER wiki_app WITH PASSWORD 'secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE wiki_impact_prod TO wiki_app;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

#### Database Migrations / 数据库迁移
```bash
# Create new migration
cd backend
python -m alembic revision --autogenerate -m "description"

# Apply migrations
python -m alembic upgrade head

# Rollback if needed
python -m alembic downgrade -1
```

### SSL/TLS Configuration / SSL/TLS配置

#### Nginx Configuration / Nginx配置
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring & Logging / 监控与日志

### Application Monitoring / 应用监控

#### Prometheus Configuration / Prometheus配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'wiki-impact-api'
    static_configs:
      - targets: ['backend:8000']
```

#### Grafana Dashboard / Grafana仪表板
```bash
# Import dashboard
curl -X POST \
  http://admin:admin@localhost:3001/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/grafana-dashboard.json
```

### Logging Configuration / 日志配置

#### Structured Logging / 结构化日志
```python
# backend/logging_config.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

## Performance Optimization / 性能优化

### Database Optimization / 数据库优化

#### Connection Pooling / 连接池
```python
# backend/app/core/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
```

#### Query Optimization / 查询优化
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM contributors 
WHERE overall_impact_score > 50.0 
ORDER BY overall_impact_score DESC;

-- Add performance indexes
CREATE INDEX CONCURRENTLY idx_contributors_active_score 
ON contributors(overall_impact_score DESC) 
WHERE is_active = true;
```

### Caching Strategy / 缓存策略

#### Redis Caching / Redis缓存
```python
# Cache frequently accessed data
@cache_result(expire=3600)
async def get_contributor_metrics(contributor_id: int):
    # Expensive computation
    return computed_metrics
```

#### CDN Configuration / CDN配置
```bash
# CloudFlare settings
Cache Level: Standard
Browser Cache TTL: 1 hour
Edge Cache TTL: 1 day
```

## Security Hardening / 安全加固

### Application Security / 应用安全

#### Rate Limiting / 速率限制
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/contributors/")
@limiter.limit("100/minute")
async def get_contributors(request: Request):
    # API endpoint
    pass
```

#### Input Validation / 输入验证
```python
from pydantic import BaseModel, validator

class ContributorQuery(BaseModel):
    username: str
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid username format')
        return v
```

### Infrastructure Security / 基础设施安全

#### Firewall Configuration / 防火墙配置
```bash
# UFW rules
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 5432/tcp  # Block direct database access
ufw enable
```

#### Docker Security / Docker安全
```dockerfile
# Use non-root user
FROM python:3.9-slim
RUN useradd --create-home --shell /bin/bash app
USER app

# Read-only filesystem
RUN chmod -R 755 /app
VOLUME /app/data
```

## Backup & Recovery / 备份与恢复

### Database Backup / 数据库备份

#### Automated Backups / 自动备份
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

pg_dump $DATABASE_URL | gzip > $BACKUP_DIR/wiki_impact_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "wiki_impact_*.sql.gz" -mtime +7 -delete
```

#### Backup Restoration / 备份恢复
```bash
# Restore from backup
gunzip -c backup_file.sql.gz | psql $DATABASE_URL
```

### Application Data Backup / 应用数据备份
```bash
# Redis backup
redis-cli --rdb /backups/redis_backup.rdb

# File system backup
tar -czf /backups/app_data_$(date +%Y%m%d).tar.gz /app/data
```

## Troubleshooting / 故障排除

### Common Issues / 常见问题

#### Database Connection Issues / 数据库连接问题
```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Check connection limits
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"

# Reset connections if needed
psql $DATABASE_URL -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'wiki_impact';"
```

#### Redis Connection Issues / Redis连接问题
```bash
# Test Redis connectivity
redis-cli -u $REDIS_URL ping

# Check Redis memory usage
redis-cli -u $REDIS_URL info memory

# Clear cache if needed
redis-cli -u $REDIS_URL flushdb
```

#### Application Debugging / 应用调试
```bash
# Check application logs
docker logs wiki-impact-backend --tail 100 -f

# Check system resources
docker stats

# Check service health
curl http://localhost:8000/health
```

### Performance Issues / 性能问题

#### Slow Database Queries / 慢查询
```sql
-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### High Memory Usage / 高内存使用
```bash
# Check memory usage
free -h
docker stats --no-stream

# Optimize Python memory
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1
```

## Maintenance / 维护

### Regular Maintenance Tasks / 定期维护任务

#### Weekly Tasks / 每周任务
```bash
#!/bin/bash
# weekly_maintenance.sh

# Update dependencies
pip list --outdated
npm audit

# Database maintenance
psql $DATABASE_URL -c "VACUUM ANALYZE;"

# Clean up logs
find /var/log -name "*.log" -mtime +7 -delete

# Check disk space
df -h
```

#### Monthly Tasks / 每月任务
```bash
#!/bin/bash
# monthly_maintenance.sh

# Security updates
apt update && apt upgrade -y

# Certificate renewal
certbot renew --dry-run

# Performance review
pg_stat_reset();
```

### GDPR Compliance Maintenance / GDPR合规维护

#### Data Retention Cleanup / 数据保留清理
```python
# Automated cleanup script
async def cleanup_expired_data():
    # Delete old audit logs
    await db.execute(
        "DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '6 years'"
    )
    
    # Anonymize old user data
    await db.execute(
        "UPDATE users SET email = 'anonymized@example.com' WHERE last_login < NOW() - INTERVAL '2 years'"
    )
```

## Support & Contact / 支持与联系

### Technical Support / 技术支持
- **Email**: tech-support@wikiimpact.org
- **Documentation**: https://docs.wikiimpact.org
- **Issue Tracker**: https://gitlab.scss.tcd.ie/jucui/wiki_entry_impact/issues

### Privacy & GDPR / 隐私与GDPR
- **Privacy Officer**: privacy@wikiimpact.org
- **Data Protection**: gdpr@wikiimpact.org
- **User Rights**: rights@wikiimpact.org

This deployment guide provides comprehensive instructions for setting up, deploying, and maintaining the Wiki Entry Impact Assessment System in various environments.

该部署指南为在各种环境中设置、部署和维护维基条目影响评估系统提供了全面的说明。 
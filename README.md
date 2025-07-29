# Wiki Entry Impact Assessment System / 维基条目影响评估系统

A comprehensive computational model for assessing the impact of various contributors on the collaborative process of wiki entry formation. This system provides data-driven metrics to quantify contributor actions based on Wikipedia platform data.

一个全面的计算模型，用于评估各种贡献者对维基条目形成协作过程的影响。该系统提供基于维基百科平台数据的数据驱动指标来量化贡献者行为。

## Core Features / 核心功能

- **Contributor Impact Analysis / 贡献者影响分析**: Quantify contributor impact based on text volume, discussion influence, and contribution types / 基于文本量、讨论影响和贡献类型量化贡献者影响
- **Contribution Type Classification / 贡献类型分类**: Differentiate between content creation and maintenance contributions / 区分内容创建和维护贡献
- **Discussion Impact Metrics / 讨论影响指标**: Measure influence on collaborative decision-making / 测量对协作决策的影响
- **GDPR Compliance / GDPR合规**: Built-in data privacy and consumer rights protection / 内置数据隐私和消费者权利保护
- **Real-time Analytics / 实时分析**: Live dashboard for contributor impact visualization / 贡献者影响可视化的实时仪表板
- **Intelligent Search / 智能搜索**: Search contributors by username or display name / 按用户名或显示名称搜索贡献者
- **Comparative Analysis / 比较分析**: Multi-contributor metrics comparison functionality / 多贡献者指标比较功能
- **Analysis History / 分析历史**: Historical analysis record management / 历史分析记录管理

## System Architecture / 系统架构

### Frontend / 前端
- **React 18** + **TypeScript** - Modern frontend framework / 现代前端框架
- **Vite** - Fast build tool / 快速构建工具
- **Material-UI (MUI)** - Modern UI component library / 现代UI组件库
- **Recharts** - Data visualization chart library / 数据可视化图表库
- **React Router** - Single page application routing / 单页应用路由
- **Axios** - HTTP client / HTTP客户端

### Backend / 后端
- **FastAPI** - High-performance Python web framework / 高性能Python网络框架
- **SQLAlchemy** (Async) - ORM database operations / ORM数据库操作
- **PostgreSQL** - Primary database / 主数据库
- **Redis** - Caching and session storage / 缓存和会话存储
- **Uvicorn** - ASGI server / ASGI服务器
- **Pydantic** - Data validation / 数据验证
- **structlog** - Structured logging / 结构化日志
- **NLTK** - Natural language processing / 自然语言处理

### API Design / API设计
- **RESTful API** endpoints / RESTful API端点
- **OAuth2** authentication mechanism / OAuth2认证机制
- **Rate limiting and security measures** / 速率限制和安全措施
- **Comprehensive error handling** / 全面的错误处理
- **Structured logging** / 结构化日志

## Quick Start / 快速开始

### Prerequisites / 前置要求
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+

### Installation Steps / 安装步骤

```bash
# Clone the repository / 克隆仓库
git clone <your-gitlab-url>
cd wiki_entry_impact

# Backend setup / 后端设置
pip install -r requirements.txt

# Frontend setup / 前端设置
cd frontend
npm install
cd ..

# Environment configuration / 环境配置
cp .env.example .env
# Edit .env file to configure database and Redis connections
# 编辑.env文件配置数据库和Redis连接

# Database initialization / 数据库初始化
python resetdtb_fixed.py

# Start application / 启动应用
python run.py
```

### Development Mode / 开发模式

```bash
# Start backend (port 8080) / 启动后端（端口8080）
python run.py

# Start frontend (new terminal, port 5173) / 启动前端（新终端，端口5173）
cd frontend
npm run dev
```

## Project Structure / 项目结构

```
wiki_entry_impact/
├── backend/                  # FastAPI backend application / FastAPI后端应用
│   ├── app/
│   │   ├── api/             # API routes and endpoints / API路由和端点
│   │   │   └── v1/
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   │           ├── analysis_sessions.py
│   │   │           ├── analytics.py
│   │   │           ├── auth.py
│   │   │           ├── contributors.py
│   │   │           └── wikipedia.py
│   │   ├── core/            # Core configuration and utilities / 核心配置和工具
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── redis_client.py
│   │   │   └── security.py
│   │   ├── middleware/      # Middleware / 中间件
│   │   │   ├── logging.py
│   │   │   ├── rate_limit.py
│   │   │   └── security.py
│   │   ├── models/          # Database models / 数据库模型
│   │   │   ├── analysis_session.py
│   │   │   ├── contributor.py
│   │   │   └── user.py
│   │   └── services/        # Business logic services / 业务逻辑服务
│   │       ├── impact_calculator.py
│   │       └── wikipedia_service.py
│   ├── tests/              # Test files / 测试文件
│   │   ├── test_api.py
│   │   ├── test_basic.py
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── conftest.py         # Pytest configuration / Pytest配置
│   ├── main.py             # FastAPI application entry point / FastAPI应用入口
│   └── pytest.ini         # Pytest settings / Pytest设置
├── frontend/               # React frontend application / React前端应用
│   ├── src/
│   │   ├── components/     # Reusable components / 可复用组件
│   │   │   ├── ContributorDashboard.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── NotificationPanel.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── contexts/       # React Context / React上下文
│   │   │   ├── ApiContext.tsx
│   │   │   ├── LanguageContext.tsx
│   │   │   ├── NotificationContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   ├── pages/          # Page components / 页面组件
│   │   │   ├── AnalysisHistory.tsx
│   │   │   ├── Analytics.tsx
│   │   │   ├── Comparison.tsx
│   │   │   ├── ContributorDetail.tsx
│   │   │   ├── Contributors.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Settings.tsx
│   │   │   └── WikiAnalysis.tsx
│   │   ├── App.tsx         # Main application component / 主应用组件
│   │   └── main.tsx        # Application entry point / 应用入口点
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── docs/                   # Project documentation / 项目文档
│   └── SYSTEM_ARCHITECTURE.md
├── resetdtb_fixed.py      # Database reset script / 数据库重置脚本
├── run_tests.py           # Test runner script / 测试运行脚本
├── run.py                 # Application startup script / 应用启动脚本
├── requirements.txt       # Python dependencies / Python依赖
├── TESTING.md             # Testing documentation / 测试文档
└── README.md
```

## Core API Endpoints / 核心API端点

### Contributor Management / 贡献者管理
- `GET /api/v1/contributors/` - Get contributors list (with filtering and pagination) / 获取贡献者列表（带过滤和分页）
- `GET /api/v1/contributors/{id}` - Get specific contributor details / 获取特定贡献者详情
- `GET /api/v1/contributors/{id}/impact` - Get contributor impact metrics / 获取贡献者影响指标
- `GET /api/v1/contributors/search/` - Search contributors / 搜索贡献者
- `GET /api/v1/contributors/compare/` - Compare multiple contributors / 比较多个贡献者

### Analytics Features / 分析功能
- `GET /api/v1/analytics/trends` - Get impact trend data / 获取影响趋势数据
- `GET /api/v1/contributors/stats/overview` - Get overview statistics / 获取概览统计

### Authentication / 认证
- `POST /api/v1/auth/login/access-token` - User login authentication / 用户登录认证

## Frontend Pages / 前端页面

- **Dashboard** (`/`) - Main dashboard and overview / 主仪表板和概览
- **Contributors** (`/contributors`) - Contributor list and management / 贡献者列表和管理
- **Contributor Detail** (`/contributors/:id`) - Individual contributor detail page / 个人贡献者详情页面
- **Analytics** (`/analytics`) - Analysis and trend charts / 分析和趋势图表
- **Comparison** (`/comparison`) - Contributor comparison functionality / 贡献者比较功能
- **Wiki Analysis** (`/wiki-analysis`) - Wikipedia entry analysis / 维基百科条目分析
- **Analysis History** (`/analysis-history`) - Analysis history records / 分析历史记录
- **Settings** (`/settings`) - System settings / 系统设置

## GDPR Compliance / GDPR合规

This system implements comprehensive data privacy measures / 该系统实施全面的数据隐私措施:
- Data anonymization and pseudonymization / 数据匿名化和假名化
- Right to be forgotten implementation / 被遗忘权实施
- Data portability features / 数据可移植性功能
- Consent management system / 同意管理系统
- Audit logging for data access / 数据访问审计日志

## Configuration / 配置

Configure the following environment variables in the `.env` file / 在`.env`文件中配置以下环境变量:

```env
# Database configuration / 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/wiki_impact
POSTGRES_DB=wiki_impact
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Redis configuration / Redis配置
REDIS_URL=redis://localhost:6379

# Security configuration / 安全配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Wikipedia API / 维基百科API
WIKIPEDIA_API_URL=https://en.wikipedia.org/w/api.php
```

## Testing / 测试

### Run Tests / 运行测试
```bash
# Run all tests / 运行所有测试
python run_tests.py

# Run specific test types / 运行特定类型的测试
python run_tests.py --unit          # Unit tests only / 仅单元测试
python run_tests.py --integration   # Integration tests only / 仅集成测试
python run_tests.py --api           # API tests only / 仅API测试

# Generate coverage report / 生成覆盖率报告
python run_tests.py --coverage

# Verbose output / 详细输出
python run_tests.py --verbose
```

## Deployment / 部署

### Docker Deployment (Recommended) / Docker部署（推荐）
```bash
docker-compose up -d
```

### Manual Deployment / 手动部署
```bash
# Build frontend / 构建前端
cd frontend
npm run build

# Start backend service / 启动后端服务
python run.py
```

## Contributing / 贡献

1. Fork the project / Fork项目
2. Create a feature branch / 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. Commit your changes / 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch / 推送到分支 (`git push origin feature/AmazingFeature`)
5. Open a Pull Request / 开启Pull Request

## Development Tools / 开发工具

- **resetdtb_fixed.py** - Database reset and initialization script / 数据库重置和初始化脚本
- **run_tests.py** - Comprehensive test runner with coverage reporting / 带覆盖率报告的综合测试运行器
- **run.py** - Development server launcher / 开发服务器启动器

---

> **Research Background / 研究背景**: This system is an academic research tool developed to quantify and analyze the impact of contributors in the collaborative editing process of Wikipedia. / 该系统是一个学术研究工具，用于量化和分析贡献者在维基百科协作编辑过程中的影响。

# Wiki Entry Impact Assessment System

A comprehensive computational model for assessing the impact of various contributors on the collaborative process of wiki entry formation. This system provides data-driven metrics to quantify contributor actions based on Wikipedia platform data.

## Core Features

- **Contributor Impact Analysis**: Quantify contributor impact based on text volume, discussion influence, and contribution types
- **Contribution Type Classification**: Differentiate between content creation and maintenance contributions
- **Discussion Impact Metrics**: Measure influence on collaborative decision-making
- **GDPR Compliance**: Built-in data privacy and consumer rights protection
- **Real-time Analytics**: Live dashboard for contributor impact visualization
- **Intelligent Search**: Search contributors by username or display name
- **Comparative Analysis**: Multi-contributor metrics comparison functionality
- **Analysis History**: Historical analysis record management

## System Architecture

### Frontend
- **React 18** + **TypeScript** - Modern frontend framework
- **Vite** - Fast build tool
- **Material-UI (MUI)** - Modern UI component library
- **Recharts** - Data visualization chart library
- **React Router** - Single page application routing
- **Axios** - HTTP client

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** (Async) - ORM database operations
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **structlog** - Structured logging
- **NLTK** - Natural language processing

### API Design
- **RESTful API** endpoints
- **OAuth2** authentication mechanism
- **Rate limiting and security measures**
- **Comprehensive error handling**
- **Structured logging**

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+

### Installation Steps

```bash
# Clone the repository
git clone <your-gitlab-url>
cd wiki_entry_impact

# Backend setup
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Environment configuration
cp .env.example .env
# Edit .env file to configure database and Redis connections

# Database initialization
python resetdtb_fixed.py

# Start application
python run.py
```

### Development Mode

```bash
# Start backend (port 8080)
python run.py

# Start frontend (new terminal, port 5173)
cd frontend
npm run dev
```

## Project Structure

```
wiki_entry_impact/
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/             # API routes and endpoints
│   │   ├── core/            # Core configuration and utilities
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic services
│   │   └── middleware/      # Middleware
│   └── main.py              # FastAPI application entry point
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── contexts/        # React Context
│   │   └── App.tsx          # Main application component
│   └── package.json
├── docs/                     # Project documentation
├── requirements.txt          # Python dependencies
├── run.py                   # Application startup script
└── README.md
```

## Core API Endpoints

### Contributor Management
- `GET /api/v1/contributors/` - Get contributors list (with filtering and pagination)
- `GET /api/v1/contributors/{id}` - Get specific contributor details
- `GET /api/v1/contributors/{id}/impact` - Get contributor impact metrics
- `GET /api/v1/contributors/search/` - Search contributors
- `GET /api/v1/contributors/compare/` - Compare multiple contributors

### Analytics Features
- `GET /api/v1/analytics/trends` - Get impact trend data
- `GET /api/v1/contributors/stats/overview` - Get overview statistics

### Authentication
- `POST /api/v1/auth/login/access-token` - User login authentication

## Frontend Pages

- **Dashboard** (`/`) - Main dashboard and overview
- **Contributors** (`/contributors`) - Contributor list and management
- **Contributor Detail** (`/contributors/:id`) - Individual contributor detail page
- **Analytics** (`/analytics`) - Analysis and trend charts
- **Comparison** (`/comparison`) - Contributor comparison functionality
- **Wiki Analysis** (`/wiki-analysis`) - Wikipedia entry analysis
- **Analysis History** (`/analysis-history`) - Analysis history records
- **Settings** (`/settings`) - System settings

## GDPR Compliance

This system implements comprehensive data privacy measures:
- Data anonymization and pseudonymization
- Right to be forgotten implementation
- Data portability features
- Consent management system
- Audit logging for data access

## Configuration

Configure the following environment variables in the `.env` file:

```env
# Database configuration
DATABASE_URL=postgresql://user:password@localhost:5432/wiki_impact
POSTGRES_DB=wiki_impact
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Redis configuration
REDIS_URL=redis://localhost:6379

# Security configuration
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Wikipedia API
WIKIPEDIA_API_URL=https://en.wikipedia.org/w/api.php
```

## Deployment

### Docker Deployment (Recommended)
```bash
docker-compose up -d
```

### Manual Deployment
```bash
# Build frontend
cd frontend
npm run build

# Start backend service
python run.py
```

## Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Contact

For questions or suggestions, please contact us through:
- Create an Issue
- Email the project maintainers

---

> **Research Background**: This system is an academic research tool developed to quantify and analyze the impact of contributors in the collaborative editing process of Wikipedia.

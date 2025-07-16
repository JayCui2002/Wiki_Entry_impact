# Wiki Entry Impact Assessment System

A comprehensive computational model for assessing the impact of various contributors on the collaborative process of wiki entry formation. This system provides data-driven metrics to quantify contributor actions based on Wikipedia platform data.

## Features

- **Contributor Impact Analysis**: Quantify contributor impact based on text volume, discussion influence, and contribution types
- **Additive vs Maintenance Classification**: Differentiate between content creation and maintenance contributions
- **Discussion Impact Metrics**: Measure influence on collaborative decision-making
- **GDPR Compliance**: Built-in data privacy and consumer rights protection
- **Real-time Analytics**: Live dashboard for contributor impact visualization

## System Architecture

### Frontend
- React.js with TypeScript
- Material-UI components
- Real-time data visualization with Chart.js
- Responsive design for multiple devices

### Backend
- Node.js with Express.js
- PostgreSQL database
- Redis for caching
- Wikipedia API integration
- JWT authentication

### API Design
- RESTful API endpoints
- GraphQL for complex queries
- Rate limiting and security measures
- Comprehensive error handling

## Installation

```bash
# Clone the repository
git clone https://gitlab.scss.tcd.ie/jucui/wiki_entry_impact.git
cd wiki_entry_impact

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Start development servers
npm run dev
```

## Project Structure

```
wiki_entry_impact/
├── frontend/                 # React frontend application
├── backend/                  # Node.js backend API
├── database/                 # Database schemas and migrations
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
└── tests/                    # Test suites
```

## GDPR Compliance

This system implements comprehensive data privacy measures:
- Data anonymization and pseudonymization
- Right to be forgotten implementation
- Data portability features
- Consent management system
- Audit logging for data access

## License

MIT License

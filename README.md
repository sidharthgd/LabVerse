# LabVerse

AI-powered data analysis platform that connects to your data sources and provides intelligent insights through natural language queries.

## Features

- **Multi-Agent Architecture**: Intelligent routing between RAG, Pandas, and SQL agents
- **Data Source Integration**: Connect to Google Drive, Box, and other cloud storage
- **Natural Language Queries**: Ask questions about your data in plain English
- **Real-time Analysis**: Generate charts, statistics, and insights on demand
- **Secure Execution**: Sandboxed code execution for safe data analysis

## Architecture

### Backend (FastAPI)
- **Agents**: RAG, Pandas, and SQL agents for different query types
- **Services**: Integration with cloud storage, embeddings, and ingestion
- **Models**: PostgreSQL database with SQLAlchemy ORM
- **API**: RESTful endpoints for queries, files, and ingestion

### Frontend (Next.js)
- **Chat Interface**: Interactive chat for data queries
- **File Explorer**: Browse and preview datasets
- **Dataset Viewer**: Schema and data preview
- **Authentication**: Firebase/Google OAuth integration

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Docker (optional)

### Backend Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:
```bash
python scripts/migrate.py upgrade
```

4. Start the backend:
```bash
uvicorn backend.app.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

### Docker Setup

Run the entire stack with Docker Compose:
```bash
docker-compose -f infra/docker-compose.yml up
```

## Configuration

### Environment Variables

Key environment variables to configure:

- `DATABASE_URL`: PostgreSQL connection string
- `PINECONE_API_KEY`: Pinecone vector database API key
- `OPENAI_API_KEY`: OpenAI API key for LLM features
- `GOOGLE_DRIVE_CREDENTIALS`: Google Drive API credentials
- `BOX_CLIENT_ID` / `BOX_CLIENT_SECRET`: Box API credentials

### Data Sources

Connect your data sources through the web interface or API:

- **Google Drive**: OAuth integration for file access
- **Box**: API integration for enterprise file sharing
- **Direct Upload**: Upload files directly to the platform

## API Documentation

Once running, visit:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Development

### Running Tests

Backend tests:
```bash
pytest backend/tests/
```

Frontend tests:
```bash
cd frontend
npm test
```

### Code Quality

Backend:
```bash
black backend/
flake8 backend/
mypy backend/
```

Frontend:
```bash
cd frontend
npm run lint
npm run type-check
```

## Deployment

### Infrastructure as Code

Terraform configurations are provided in `infra/terraform/` for cloud deployment.

### Docker

Production-ready Docker images:
- `infra/Dockerfile.backend`: FastAPI backend
- `infra/Dockerfile.frontend`: Next.js frontend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

****# DocFlow API

DocFlow API is a production-oriented backend service for managing document processing workflows. It allows users to upload documents, create processing requests, execute asynchronous processing jobs, extract structured data, and monitor the status of each workflow.

The project is designed to demonstrate production backend engineering concepts such as asynchronous job processing, state management, retries, database modeling, and RESTful API design.

## Features

* User authentication
* Document upload and management
* Asynchronous document processing with Celery
* Processing status tracking
* Structured data extraction
* RESTful API with automatic OpenAPI documentation
* PostgreSQL persistence
* Docker-based local development

## Architecture

```
Client
    │
    ▼
FastAPI API
    │
    ├── PostgreSQL
    ├── Redis
    │
    ▼
Celery Worker
    │
    ▼
Document Processing Pipeline
```

## Tech Stack

| Technology | Purpose                       |
| ---------- | ----------------------------- |
| Python     | Programming language          |
| FastAPI    | REST API framework            |
| SQLAlchemy | ORM                           |
| PostgreSQL | Primary database              |
| Alembic    | Database migrations           |
| Redis      | Message broker                |
| Celery     | Background job processing     |
| Docker     | Local development environment |
| Pytest     | Testing                       |

## Getting Started

### Clone the repository

```bash
git clone git@github.com:tuyishimehope/DOC-FLOW.git
cd DOC-FLOW
```

### Start the application

```bash
docker compose up --build
```

### Run database migrations

```bash
alembic upgrade head
```

The API will be available at:

* http://localhost:8000
* Swagger UI: `/docs`
* ReDoc: `/redoc`

## Project Structure

```
app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    workers/
tests/
alembic/
docker/
```

## Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a pull request.

## Roadmap

* Object storage integration
* OCR pipeline
* Webhook notifications
* Role-based access control
* Metrics and monitoring
* CI/CD pipeline

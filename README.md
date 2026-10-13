# LifeOS API

A RESTful task-management API built with Python and FastAPI, featuring JWT authentication, PostgreSQL persistence, database migrations, request validation, rate limiting, and Docker-based deployment.

## Features

- User registration and JWT-based authentication
- Password hashing with Argon2
- User-specific task CRUD operations
- Pagination and request validation
- PostgreSQL database with SQLAlchemy
- Version-controlled schema migrations using Alembic
- Login and registration rate limiting
- Structured JSON logging and safe error responses
- Health and database-readiness endpoints
- Docker Compose development environment
- Automated API tests with pytest

## Tech Stack

- **Language:** Python
- **API framework:** FastAPI
- **Validation:** Pydantic
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Authentication:** JWT and Argon2 password hashing
- **Rate limiting:** SlowAPI
- **Testing:** pytest and FastAPI TestClient
- **Containerization:** Docker and Docker Compose

## Getting Started

### Prerequisites

- Python 3.12 or compatible
- Docker and Docker Compose
- Git

### Run with Docker

1. Clone this repository.
2. Create a local `.env` file containing `JWT_SECRET_KEY` with a securely generated secret.
3. Start the services:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

4. Open `http://localhost:8000/docs`.

### Configuration

- `DATABASE_URL`: SQLAlchemy database connection URL.
- `JWT_SECRET_KEY`: secret used to sign authentication tokens.

Never commit `.env` or real credentials.

### Run Tests

```bash
pytest -q
```

## API Documentation

Interactive Swagger documentation is available at `/docs` while the API is running.

## Project Status

Personal portfolio project focused on backend API engineering and deployment fundamentals.


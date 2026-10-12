# ADR 001: Use FastAPI

- **Status:** Accepted

## Context

LifeOS needs a Python REST API with request validation, authentication, and interactive API documentation.

## Decision

Use FastAPI as the HTTP framework and Pydantic for request and response schemas.

## Consequences

- Automatic OpenAPI documentation
- Typed request validation
- Clear separation between API schemas and database models
- Additional framework conventions to learn and maintain
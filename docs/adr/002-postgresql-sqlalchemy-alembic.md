# ADR 002: PostgreSQL, SQLAlchemy, and Alembic

- **Status:** Accepted

## Context

LifeOS needs persistent relational storage and controlled database schema changes.

## Decision

Use PostgreSQL for storage, SQLAlchemy for database access, and Alembic for versioned migrations.

## Consequences

- Relational constraints and durable persistence
- Database operations are separated from API schemas
- Schema changes can be reviewed and applied incrementally
- Migrations must be maintained alongside model changes
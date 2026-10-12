# ADR 003: JWT-Based Authentication

- **Status:** Accepted

## Context

Users must authenticate and access only their own tasks.

## Decision

Use JWT bearer tokens for authentication and Argon2 password hashing for stored passwords.

## Consequences

- Clients can authenticate API requests using bearer tokens
- Passwords are not stored as plaintext
- Protected endpoints must verify identity and enforce ownership
- JWT signing secrets must be kept out of version control
- Token expiry and secret rotation require deliberate handling
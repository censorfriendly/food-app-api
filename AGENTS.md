# API Agent Instructions

This directory contains the Python backend.

Before writing code, review:

docs/api-guidelines.md

docs/database.md

Rules:

- Backend owns business logic.
- Mobile app is an untrusted client.
- Every endpoint requires validation.
- Use Pydantic models.
- Use dependency injection.
- Write tests for new functionality.
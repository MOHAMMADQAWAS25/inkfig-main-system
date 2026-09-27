# InkFig Main System Architecture

This service uses FastAPI and the same practical clean architecture as Shadow:

```text
src/
|-- entities/
|   |-- dto/             Request and response contracts
|   |-- enums/           Domain enumerations
|   |-- exceptions/      Domain and application errors
|   `-- repositories/    Persistence ports used by services
|-- app/
|   `-- services/        Business use cases and workflow decisions
|-- interface/
|   |-- api/
|   |   |-- controllers/ HTTP-to-application coordination
|   |   `-- routes/      FastAPI route declarations
|   |-- dependencies/    FastAPI dependency providers
|   `-- middleware/      HTTP middleware
`-- infrastructure/
    |-- config/          Runtime settings
    |-- db/postgres/     SQLAlchemy setup and models
    |-- integrations/    Storage, search, and external adapters
    `-- repositories/    PostgreSQL repository implementations
```

Tests live in `tests/`. PostgreSQL migrations will live in `migrations/` once the migration tool is selected. Every public API is versioned under `/api/v1`; `/health` is also exposed at the root for infrastructure checks.

## Dependency rules

- `entities` does not import FastAPI, SQLAlchemy, or infrastructure code.
- `app` depends on entity contracts and repository ports, never HTTP request objects or SQLAlchemy queries.
- `interface` validates HTTP input, applies authentication and permissions, invokes services, and translates errors.
- `infrastructure` implements persistence and external-service details.
- Controllers never return raw SQLAlchemy models.

## Service responsibility

The main system owns artwork, portfolios, discovery, likes, recommendations, search, events, submissions, moderation, reports, and other InkFig business workflows. Authentication and user administration belong to the user system.

# InkFig Main System Architecture

This InkFig service uses FastAPI and practical clean architecture. These are
technical layer boundaries, not another project's business rules:

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

Tests live in `tests/`. Versioned migrations already live in `migrations/` and
use the existing `python -m migrations.run` runner/schema_migrations ledger.
Running it manually requires explicit approval; see the migration README.
Public APIs are versioned under `/api/v1`; root `/health` is also an infrastructure check.

## Dependency rules

- `entities` does not import FastAPI, SQLAlchemy, or infrastructure code.
- `app` depends on entity contracts and repository ports, never HTTP request objects or SQLAlchemy queries.
- `interface` validates HTTP input, applies authentication and permissions, invokes services, and translates errors.
- `infrastructure` implements persistence and external-service details.
- Controllers never return raw SQLAlchemy models.

## Service responsibility

The main system owns works/feed/search/related images, likes/saves, artwork moderation,
exhibitions/submissions/withdrawals/blocks, exhibition ratings and leaderboards.
Identity, profiles/follows, user administration, reports, search history and notification
transport belong to the user system. Preference learning remains a proposal, not
implemented personalization. See docs/agent for current contracts.

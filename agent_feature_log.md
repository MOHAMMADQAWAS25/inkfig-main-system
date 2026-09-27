# Agent Feature Log

This file is the repository's running implementation history for agent-assisted work.

## Working rule

- Read this file before making any change in this repository.
- After completing work, add a dated entry describing what changed and how it was verified.
- State whether a database migration is required and name it when applicable.
- Keep entries concise, factual, and limited to this repository.

## Entries

### 2026-09-28 - Validate Supabase connectivity configuration

- Confirmed the ignored local environment contains all three required Supabase variables without exposing their values.
- Verified an authenticated request to the configured Supabase API succeeds.
- The read-only PostgreSQL `SELECT 1` check could not start because the configured `DATABASE_URL` is malformed with an empty port; the URL must be replaced with a complete single-line connection string.
- Verification: Supabase API passed; database URL parsing failed before any database connection was attempted.
- Migration required: No.

### 2026-09-28 - Make database configuration Supabase-only

- Removed the local `POSTGRES_*` fallback fields from application settings, `.env.example`, and the ignored local `.env` file.
- Made `DATABASE_URL` the single PostgreSQL connection setting alongside the Supabase project URL and backend secret key.
- Added a regression test confirming that no localhost/PostgreSQL-host fallback remains.
- Verification: 3 pytest tests passed; mypy reported no issues in 29 source files; Python byte-compilation and `git diff --check` passed.
- Migration required: No.

### 2026-09-28 - Add local Supabase configuration placeholders

- Added blank `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and `DATABASE_URL` placeholders to `.env.example`.
- Created the ignored local `.env` file with the same blank placeholders for developer-supplied secrets.
- Verification: confirmed `.env` exists locally, is ignored by Git, and contains no secret values; `git diff --check` passed.
- Migration required: No.

### 2026-09-28 - Establish the FastAPI architecture foundation

- Added the `entities -> app -> interface/infrastructure` package structure based on Shadow's practical clean architecture, adapted for the InkFig domain.
- Added a FastAPI application factory, configurable CORS and `/api/v1` prefix, root and versioned health endpoints, environment template, PostgreSQL-ready dependencies, test/type-check configuration, and architecture documentation.
- Reserved organized locations for DTOs, enums, exceptions, repository ports, services, routes, controllers, dependencies, middleware, SQLAlchemy models, repositories, integrations, and timestamped migrations.
- Verification: 2 pytest tests passed; mypy reported no issues in 29 source files; Python byte-compilation and `git diff --check` passed.
- Migration required: No. The migrations directory is structural only.

### 2026-09-28 - Document the InkFig product vision

- Added `README.md` with the project's university context, art-community purpose, planned discovery and interaction features, AI-assisted image search, teacher event moderation workflow, and access-control direction.
- Clarified that this repository owns InkFig's main business features and workflows.
- Verification: reviewed the rendered Markdown structure and ran Git's whitespace validation.
- Migration required: No.

### 2026-09-27 - Initialize agent feature log

- Added this repository-level feature log and established the read-before-work and update-after-work convention.
- Verification: confirmed the file exists in the repository.
- Migration required: No.

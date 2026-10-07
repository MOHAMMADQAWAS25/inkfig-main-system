# Agent Feature Log

This file is the repository's running implementation history for agent-assisted work.

## Working rule

- Read this file before making any change in this repository.
- After completing work, add a dated entry describing what changed and how it was verified.
- State whether a database migration is required and name it when applicable.
- Keep entries concise, factual, and limited to this repository.

## Entries

### 2026-09-28 - Retest Supabase database connectivity

- Verified the corrected `DATABASE_URL` has the asyncpg driver, complete direct Supabase host, port `5432`, database name, username, and a populated password without exposing secret values.
- Verified the authenticated Supabase API request still succeeds.
- The read-only PostgreSQL check reached connection setup but failed DNS resolution because the direct Supabase database endpoint requires IPv6 in this environment; use the project's Session Pooler connection string for IPv4 access.
- Verification: Supabase API passed; database `SELECT 1` was not reached because direct-host DNS resolution failed.
- Migration required: No.

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

## 2026-09-28 - Standardize agent feature log requirements

### Request

Require every repository to use a root `AGENT_FEATURE_LOG.md`, read it fully before each ticket, preserve its history, and append every completed ticket using the prescribed structured sections.

### Changes

- Renamed the existing root feature log to the exact uppercase filename while preserving all previous entries unchanged.
- Adopted the required entry format for this and all future tickets.
- Intentionally left application behavior, authorization, APIs, database configuration, and dependencies unchanged.

### Repositories

- `delivery-main-system`: standardized the root feature-log filename and adopted the structured ticket record.
- `delivery-user-system`: standardized the root feature-log filename and adopted the structured ticket record.
- `delivery-user-FE`: standardized the root feature-log filename and adopted the structured ticket record.

### Files

- `AGENT_FEATURE_LOG.md`: renamed from `agent_feature_log.md` and appended this structured entry.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or role access changed.
- No organization or domain scope changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] git status --short` - confirmed the case-only rename is tracked.
- `[passed] git diff --check`
- `[not run] application tests and builds` - documentation-only filename and log-format change.

### Deployment

No special deployment steps.

### Git

- Branch: `main`
- Commit: `89e00b0`
- Push: `successful`

### Notes

Historical entries retain their original format; the required structured format applies from this entry onward.

## 2026-09-28 - Verify live Supabase connections

### Request

Retest the backend connection after replacing the direct IPv6 PostgreSQL URL with the Supabase Session Pooler connection string.

### Changes

- Performed read-only live checks against the configured Supabase API and PostgreSQL database without printing credentials.
- Confirmed the Session Pooler connection works with SQLAlchemy and asyncpg.
- Removed the temporary diagnostic script after verification.
- Intentionally left runtime application code and configuration values unchanged.

### Repositories

- `delivery-main-system`: verified its local Supabase API and database configuration.
- `delivery-user-system`: verified its local Supabase API and database configuration.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the successful live connection verification.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or roles changed.
- No organization or domain scope changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] authenticated GET to the configured Supabase REST API root`
- `[passed] SQLAlchemy asyncpg connection through the Supabase Session Pooler`
- `[passed] SELECT 1`
- `[not run] pytest and mypy` - no application source code changed.

### Deployment

- Configure `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and the Session Pooler `DATABASE_URL` in each deployed backend environment.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `d0987be`
- Push: `successful`

### Notes

The verified local `.env` secrets remain ignored by Git and were not printed or committed.

## 2026-09-29 - Add AWS SAM Lambda deployment template

### Request

Prepare the InkFig main FastAPI backend for deployment to AWS Lambda using AWS SAM and add a root `template.yaml`.

### Changes

- Added a Mangum adapter that exposes the existing FastAPI application as an AWS Lambda handler.
- Added a SAM template with Python 3.13, x86_64 Lambda, API Gateway HTTP API root/proxy events, tracing, resource tags, and API/function outputs.
- Added deployment parameters for environment, trusted CORS origins, Supabase URL, backend secret key, Session Pooler database URL, and project name; secret parameters use `NoEcho`.
- Added Mangum to backend dependencies and excluded `.aws-sam/` build output from Git.
- Made the existing settings regression test inspect model defaults without loading local secrets.
- Documented SAM validation, build, and guided deployment commands.
- Intentionally left FastAPI routes, authorization behavior, database schema, and custom-domain configuration unchanged.

### Repositories

- `delivery-main-system`: added its Lambda handler, SAM template, deployment documentation, dependency, and focused test.
- `delivery-user-system`: added its Lambda handler, SAM template, deployment documentation, dependency, and focused test.

### Files

- `template.yaml`: defines the main-system Lambda and API Gateway HTTP API.
- `src/lambda_handler.py`: wraps FastAPI with Mangum.
- `requirements.txt`: adds Mangum.
- `tests/test_health.py`: verifies the Lambda handler and avoids loading secret configuration in assertions.
- `.gitignore`: excludes SAM build artifacts.
- `README.md`: documents validation, build, deployment, and parameter handling.
- `AGENT_FEATURE_LOG.md`: records this ticket.

### API

- `ANY /`: API Gateway forwards root requests to FastAPI.
- `ANY /{proxy+}`: API Gateway forwards all nested paths, including `/api/v1/*`, to FastAPI.
- No request fields, responses, filters, validation, permission checks, or application error contracts changed.

### Database

No migration required.

### Permissions and scope

- No application permissions, roles, or access scopes changed.
- Existing and future backend authorization remains authoritative inside FastAPI.
- The SAM template creates only the Lambda execution role required by the serverless function; no domain-specific IAM permissions were added.

### Frontend

No frontend changes.

### Verification

- `[passed] Python YAML compose check for template.yaml`
- `[passed] py -m pytest` - 4 tests passed.
- `[passed] py -m mypy src tests` - no issues in 30 source files.
- `[passed] py -m compileall -q src tests`
- `[passed] git diff --check`
- `[failed] initial py -m pytest` - the pre-existing settings test loaded local `.env` data and was corrected to inspect field defaults without exposing values.
- `[not run] sam validate --lint` - AWS SAM CLI is not installed in this environment.
- `[not run] sam build` - AWS SAM CLI is not installed in this environment.

### Deployment

- Deploy `delivery-main-system` as its own SAM/CloudFormation stack.
- Run `sam validate --lint`, `sam build`, and `sam deploy --guided` on a machine with AWS SAM CLI and configured AWS credentials.
- Provide `CorsOrigins`, `SupabaseUrl`, `SupabaseSecretKey`, and the Session Pooler `DatabaseUrl` during deployment; do not save secrets in committed files.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `f132664`
- Push: `successful`

### Notes

Custom domains and ACM certificates remain follow-up work after the production domains are chosen. The database password appeared in failed test output and must be rotated before deployment.

## 2026-09-29 - Align local folders with renamed repositories

### Request

Rename the local repository folders to match the new InkFig GitHub repository names.

### Changes

- Renamed the local folder from `delivery-main-system` to `inkfig-main-system`.
- Updated `origin` from the legacy redirected repository URL to the canonical `inkfig-main-system` GitHub URL.
- Removed only the empty old folder remnant left by the Windows move operation.
- Intentionally left application code, configuration values, dependencies, and runtime behavior unchanged.

### Repositories

- `inkfig-main-system`: renamed its local folder and updated its canonical `origin` URL.
- `inkfig-user-system`: renamed its local folder and updated its canonical `origin` URL.
- `inkfig-user-FE`: renamed its local folder and updated its canonical `origin` URL.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the local folder and remote URL alignment.
- No application files changed.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions, roles, authorization checks, or access scopes changed.
- Backend authorization behavior is unchanged.

### Frontend

No frontend changes.

### Verification

- `[passed] git status --short --branch` - repository remained clean after the move.
- `[passed] git remote get-url origin` - canonical InkFig remote URL is configured.
- `[passed] git ls-remote --exit-code origin refs/heads/main` - renamed GitHub repository is reachable.
- `[passed] workspace directory inspection` - only the three new repository folder names remain.
- `[not run] application tests and builds` - no application files changed.

### Deployment

- Update local scripts or external deployment jobs that still reference the old `delivery-main-system` folder or repository URL.
- No migrations must run before deployment.

### Git

- Branch: `main`
- Commit: `070f7e1`
- Push: `successful`

### Notes

The old GitHub URL redirected successfully, but the canonical URL is now configured directly.
## 2026-09-29 - Align AWS SAM runtime with local Python 3.12

### Request

Fix the AWS SAM build failure caused by the template requiring Python 3.13 while the development machine provides Python 3.12.

### Changes

- Changed the Lambda runtime from `python3.13` to `python3.12` so SAM can use the installed interpreter.
- Aligned mypy's configured Python version and the README development documentation with Python 3.12.
- Left application behavior, authentication, API contracts, and deployment topology unchanged.

### Repositories

- `inkfig-main-system`: aligned the SAM, type-checking, and documented Python runtime.
- `inkfig-user-system`: received the matching runtime alignment in its own repository.

### Files

- `template.yaml`: changed the Lambda runtime to `python3.12`.
- `mypy.ini`: changed the type-checking target to Python 3.12.
- `README.md`: documented Python 3.12 as the backend development version.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions or role scopes changed.
- Existing backend authorization remains unchanged and backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] py -m compileall -q src tests`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` when this runtime correction is needed in AWS.
- No migration is required before deployment.
- No environment-variable or configuration-value changes are required; rebuild the SAM artifact before deployment.

### Git

- Branch: `main`
- Commit: `35a14c4`
- Push: `successful`

### Notes

Python 3.12 is an AWS Lambda-supported runtime and matches the installed local interpreter. Using `sam build --use-container` remains an optional alternative when a matching local interpreter is unavailable.
## 2026-09-29 - Configure the main API custom domain

### Request

Configure `main-api.inkfig-hu.com` as the Cloudflare-managed hostname for the main backend.

### Changes

- Added a regional API Gateway custom domain secured by an ACM certificate supplied at deployment.
- Mapped the custom domain root path to the HTTP API `$default` stage using TLS 1.2.
- Added stack outputs for the public custom URL and the generated API Gateway hostname required as the Cloudflare CNAME target.
- Assigned the main backend its own CloudFormation stack and S3 prefix so it cannot collide with the user backend deployment.
- Documented ACM region and Cloudflare DNS/proxy requirements.
- Left FastAPI behavior, authorization, APIs, and database access unchanged.

### Repositories

- `inkfig-main-system`: configured `main-api.inkfig-hu.com` and its deployment outputs.
- `inkfig-user-system`: separately configured `user-api.inkfig-hu.com`.

### Files

- `template.yaml`: added the certificate parameter, API Gateway custom domain, API mapping, and domain outputs.
- `samconfig.toml`: added the repository-specific deployment stack configuration.
- `README.md`: documented certificate and Cloudflare CNAME setup.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

- `ANY https://main-api.inkfig-hu.com/`: maps to the existing HTTP API `$default` stage.
- `ANY https://main-api.inkfig-hu.com/{proxy+}`: continues forwarding nested FastAPI routes.
- No request, response, validation, filtering, or error-contract changes.

### Database

No migration required.

### Permissions and scope

- No application permissions, roles, or scopes changed.
- Existing backend authorization remains authoritative and backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check`

### Deployment

- Deploy the `inkfig-main-system` stack in `eu-west-1` and provide an ACM certificate ARN valid for `main-api.inkfig-hu.com` from that region.
- After deployment, create Cloudflare CNAME `main-api` pointing to the `CloudflareCnameTarget` stack output; use DNS-only during initial validation.
- No migration is required before deployment.
- Existing Supabase, database, CORS, and environment parameters remain required.

### Git

- Branch: `main`
- Commit: `03c8fb2`
- Push: `successful`

### Notes

Cloudflare DNS cannot be completed until AWS deploys the custom domain and returns its unique regional hostname. If Cloudflare proxying is enabled later, use Full (strict) SSL/TLS mode.
## 2026-09-29 - Order API domain mapping after stage creation

### Request

Fix the API Gateway custom-domain deployment failure reporting `Invalid stage identifier specified` while creating the domain mapping.

### Changes

- Added an explicit CloudFormation dependency so `ApiDomainMapping` waits for the SAM-generated `$default` HTTP API stage.
- Applied the correction to both backends to prevent the same creation-order race during fresh deployments or resource replacement.
- Preserved locally generated `samconfig.toml` deployment values without committing them.
- Left application behavior, API contracts, authorization, and database access unchanged.

### Repositories

- `inkfig-main-system`: added the stage dependency as a preventive correction.
- `inkfig-user-system`: added the stage dependency that resolves the observed failed deployment.

### Files

- `template.yaml`: made `ApiDomainMapping` depend on `HttpApiApiGatewayDefaultStage`.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No permissions, roles, or access scopes changed.
- Existing backend authorization remains backend-enforced.

### Frontend

No frontend changes.

### Verification

- `[passed] sam validate --lint`
- `[passed] sam build`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- template.yaml`

### Deployment

- No immediate redeployment is required for the already healthy main-system stack.
- Future deployments will wait for the HTTP API stage before creating or replacing the domain mapping.
- No migration is required and no new environment variables are needed.

### Git

- Branch: `main`
- Commit: `8fa6fe0`
- Push: `successful`

### Notes

The user-system failure occurred because CloudFormation created the mapping concurrently with its stage; the certificate and domain resource were valid.
## 2026-09-29 - Deploy the main backend from GitHub Actions

### Request

Automatically test and deploy the main backend to AWS whenever changes are pushed to the `main` branch.

### Changes

- Added a GitHub Actions workflow triggered by pushes to `main` and manual dispatches.
- Added Python 3.12 dependency installation, pytest, mypy, SAM validation, SAM build, non-interactive deployment, and production health verification.
- Used GitHub OIDC and temporary AWS credentials instead of permanent AWS access keys.
- Serialized production deployments to prevent overlapping CloudFormation updates.
- Passed production backend configuration from GitHub secrets without relying on local `samconfig.toml` values.
- Documented the required GitHub environment, secrets, and AWS deployment-role responsibilities.
- Left runtime behavior, APIs, authorization, and database schema unchanged.

### Repositories

- `inkfig-main-system`: added automated deployment for the main backend.
- `inkfig-user-system`: added the corresponding user-backend deployment workflow.

### Files

- `.github/workflows/deploy.yml`: tests, validates, builds, deploys, and health-checks the main backend.
- `README.md`: documents OIDC and required GitHub secrets.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- The workflow requests only `contents: read` and `id-token: write` GitHub permissions.
- AWS access is obtained through an IAM role restricted by its GitHub OIDC trust policy and AWS permissions.
- No application roles or backend authorization rules changed.

### Frontend

No frontend changes.

### Verification

- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- .github/workflows/deploy.yml README.md`
- `[not run] GitHub Actions deployment` — requires the production environment, OIDC role, and repository secrets to be configured in GitHub.

### Deployment

- Configure the GitHub `production` environment and the documented secrets before relying on automatic deployment.
- Configure the AWS GitHub OIDC provider and deployment role, restricted to this repository's `main` branch.
- After setup, every push to `main` deploys the `inkfig-main-system` stack in `eu-west-1`.
- No migration is required.

### Git

- Branch: `main`
- Commit: `7c6c91c`
- Push: `successful`

### Notes

The first workflow run will fail at AWS authentication until `AWS_DEPLOY_ROLE_ARN` and the other required secrets exist. Local `samconfig.toml` changes were preserved and intentionally excluded.
## 2026-09-29 - Review and map the current project foundation

### Request

Read the InkFig repositories and establish an accurate understanding of the product, service boundaries, implementation status, and deployment model before future feature work.

### Changes

- Reviewed the product documentation, architecture rules, runtime entry points, health request flow, configuration, tests, SAM infrastructure, and deployment workflow.
- Confirmed this service owns artwork, portfolios, discovery, likes, recommendations, search, events, submissions, moderation, and reports, while identity and access management belong to the user system.
- Confirmed the repository currently provides architecture and deployment foundations plus health endpoints; domain workflows and persistence implementations are not yet implemented.
- Intentionally left application behavior and configuration unchanged.

### Repositories

- `inkfig-main-system`: reviewed and documented the current main-backend baseline.
- `inkfig-user-system`: reviewed alongside this service to verify ownership boundaries.
- `inkfig-user-FE`: reviewed alongside this service to verify client integration and deployment boundaries.

### Files

- `AGENT_FEATURE_LOG.md`: recorded the project-understanding pass.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

No permissions, roles, authorization behavior, or access scopes changed.

### Frontend

No frontend changes.

### Verification

- `[passed] repository source, architecture, configuration, tests, and deployment files reviewed`
- `[passed] git diff --check`
- `[not run] application tests and builds` - documentation-only change.

### Deployment

No deployment changes or special steps.

### Git

- Branch: `main`
- Commit and push: performed after verification.

### Notes

This entry records understanding only; it does not claim that planned product capabilities are already implemented.
## 2026-09-29 - Preserve JSON configuration in automated SAM deployment

### Request

Fix the automated deployment after the production health check returned HTTP 500 following an otherwise successful GitHub Actions deployment.

### Changes

- Diagnosed the Lambda startup failure from CloudWatch as an invalid `CORS_ORIGINS` value; the command-line SAM override had deployed only `[` instead of a JSON array.
- Replaced shell-expanded SAM overrides with an ephemeral structured JSON parameter file generated on the GitHub runner.
- Preserved the exact production CORS JSON and passed Supabase, database, and certificate secrets without printing them.
- Applied the same correction to both backend workflows to prevent an identical failure in the user service.
- Left application behavior, API contracts, authorization, and database schema unchanged.

### Repositories

- `inkfig-main-system`: fixed the workflow responsible for the observed production 500.
- `inkfig-user-system`: applied the same safe parameter handling proactively.

### Files

- `.github/workflows/deploy.yml`: generates and supplies a structured SAM deployment-parameter file.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- GitHub OIDC and AWS IAM permissions remain unchanged.
- No application permissions, roles, or authorization scopes changed.

### Frontend

No frontend changes.

### Verification

- `[passed] CloudWatch log inspection` — identified `SettingsError` while parsing `cors_origins`.
- `[passed] deployed Lambda configuration inspection` — confirmed the malformed value was only `[` without exposing secrets.
- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] py -m pytest` — 4 tests passed.
- `[passed] py -m mypy src tests` — no issues in 30 source files.
- `[passed] git diff --check -- .github/workflows/deploy.yml`
- `[not run] corrected GitHub Actions deployment` — triggered by pushing this fix and verified after the push.

### Deployment

- Pushing this correction triggers deployment of the `inkfig-main-system` stack and its production health check.
- No environment-secret changes or database migrations are required.

### Git

- Branch: `main`
- Commit: `9c64526`
- Push: `successful`

### Notes

The production outage was caused by command-line quoting, not FastAPI application logic or the Lambda runtime.
## 2026-09-29 - Use a SAM-supported deployment parameter file

### Request

Complete the automated CORS recovery after the first structured-parameter workflow run failed immediately in the SAM deploy step.

### Changes

- Changed the ephemeral parameter filename from `.json` to `.yaml`, one of the file extensions supported by the installed SAM CLI parameter parser.
- Retained JSON-formatted content because JSON is valid YAML and preserves the CORS array and secret strings exactly.
- Left application behavior, APIs, authorization, infrastructure resources, and database schema unchanged.

### Repositories

- `inkfig-main-system`: corrected the deployment parameter-file extension.
- `inkfig-user-system`: applied the same correction.

### Files

- `.github/workflows/deploy.yml`: writes the structured parameter document with a SAM-supported `.yaml` extension.
- `AGENT_FEATURE_LOG.md`: recorded this ticket.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- No GitHub, AWS IAM, application permission, role, or scope changes.

### Frontend

No frontend changes.

### Verification

- `[passed] installed SAM CLI parameter parser loaded the YAML file and returned ["https://inkfig-hu.com"] exactly`
- `[passed] Python YAML parse of .github/workflows/deploy.yml`
- `[passed] git diff --check -- .github/workflows/deploy.yml`
- `[failed] prior corrected GitHub Actions deployment` — SAM rejected `.json` as an unsupported parameter-file extension before contacting CloudFormation.

### Deployment

- Pushing this correction triggers the main production deployment again.
- No secret, configuration-value, or migration changes are required.

### Git

- Branch: `main`
- Commit: `2b04744`
- Push: `successful`

### Notes

The parameter document remains structured and ephemeral; only its extension changed for SAM CLI compatibility.
## 2026-10-01 - Public artwork upload and feed foundation

### Request

Prepare the backend and database so every user can upload typed artwork, store image files in Supabase, publish the work publicly, and allow authenticated users to like it. Official system work types will be supplied later.

### Changes

- Added a clean-architecture works domain with DTOs, service contracts, repository implementation, FastAPI routes, and Supabase Storage integration.
- Added a two-stage upload workflow: the authenticated owner requests a signed upload URL, uploads directly to Supabase Storage, and then publishes only after the backend verifies that the object exists.
- Added a public cursor-ready feed and authenticated, idempotent like/unlike operations.
- Added JWT validation compatible with access tokens issued by `inkfig-user-system`; the Supabase service key remains backend-only.
- Added automated database migration execution to the production deployment workflow.
- Intentionally left the work-type table empty until the official system types are provided.

### Repositories

- `inkfig-main-system`: added works APIs, persistence, storage integration, database migration, tests, and deployment configuration.
- `inkfig-user-FE`: consumes these APIs in a separate repository change.

### Files

- `migrations/20261001_001_create_works.sql`: creates the works schema and configures the Storage bucket.
- `migrations/run.py`: applies tracked migrations idempotently and verifies the works schema.
- `src/app/services/work_service.py`: implements upload, publish, feed, and like workflows.
- `src/infrastructure/repositories/work_repository.py`: implements PostgreSQL work persistence and feed queries.
- `src/infrastructure/integrations/supabase_storage.py`: creates signed upload URLs and verifies stored objects.
- `src/interface/api/routes/works.py`: exposes the works HTTP API.
- `template.yaml`: supplies JWT and works configuration to Lambda.
- `.github/workflows/deploy.yml`: passes the JWT secret and runs migrations before deployment.
- `tests/test_work_service.py`: verifies core ownership, file validation, publication, and feed behavior.

### API

- `GET /api/v1/works/types`: publicly lists active system work types.
- `GET /api/v1/works`: publicly lists published works; accepts `limit` from 1 to 50 and an optional `before` timestamp, and includes viewer-like state when a valid bearer token is supplied.
- `POST /api/v1/works/uploads`: requires authentication; validates type, title, description, supported image MIME type, and a maximum 10 MiB size, then returns a work ID and short-lived signed upload URL.
- `POST /api/v1/works/{work_id}/publish`: requires the owning user and an existing uploaded object; returns 404 when the owned draft or object is unavailable.
- `PUT /api/v1/works/{work_id}/like`: requires authentication and idempotently likes a published work.
- `DELETE /api/v1/works/{work_id}/like`: requires authentication and idempotently removes the user's like.

### Database

- Migration: `20261001_001_create_works.sql`
- Creates `work_types`, `works`, and `work_likes`, including ownership/type foreign keys, unique storage paths, size/status checks, public-feed and owner indexes, timestamps, and cascading cleanup for owned works and likes.
- Creates or updates the public `works` Storage bucket with a 10 MiB limit and JPEG, PNG, WebP, and GIF MIME restrictions.
- Enables RLS and removes direct anon/authenticated table grants; database access remains backend-controlled through the service role/PostgreSQL connection.
- No type rows are backfilled. Rollback requires preserving or deliberately removing uploaded Storage objects separately from relational rows.

### Permissions and scope

- Public visitors can read active types and published works.
- Any authenticated InkFig user can prepare uploads and like or unlike published works.
- Only the work owner can publish that work's draft; ownership is validated by backend database predicates.
- Authentication and authorization are validated by the backend using the shared JWT signing secret and issuer.

### Frontend

- No frontend changes in this repository; `inkfig-user-FE` contains the upload page and public-feed integration.

### Verification

- `[passed] uv run --with-requirements requirements.txt ruff check src tests`
- `[passed] uv run --with-requirements requirements.txt pytest — 8 tests passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 43 files`
- `[passed] python -m migrations.run — migration applied and works tables/public bucket verified`
- `[passed] sam validate --lint`
- `[failed] sam build — local machine does not have a Python 3.12 executable on PATH; GitHub Actions installs Python 3.12 before building`

### Deployment

- Deploy `inkfig-main-system`; the workflow runs the database migration before the SAM deployment.
- Configure `JWT_SECRET` in the main backend production GitHub environment with the same value used by `inkfig-user-system`.
- Existing `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `DATABASE_URL`, and AWS/ACM secrets remain required.

### Git

- Branch: `main`
- Commit: `1f2271a`
- Push: `successful`

### Notes

Signed upload URLs avoid sending image bodies through API Gateway/Lambda. Draft rows can remain if a client requests a URL but never publishes; stale-draft cleanup can be added later. Access-token revocation takes effect in this service when the short-lived token expires because this service validates the signed token without querying the user service on every request.

## 2026-10-01 - Fix nullable public-feed query parameters

### Request

Verify the newly deployed works foundation and correct the public feed after production returned HTTP 500 for an empty unauthenticated request.

### Changes

- Added explicit PostgreSQL casts for nullable viewer UUID and cursor timestamp parameters in the public-feed query.
- Kept feed ordering, visibility, pagination, and authorization behavior unchanged.

### Repositories

- `inkfig-main-system`: corrected the PostgreSQL public-feed query.

### Files

- `src/infrastructure/repositories/work_repository.py`: casts nullable parameters so asyncpg can prepare the statement.

### API

- `GET /api/v1/works`: now returns an empty feed instead of HTTP 500 when both the optional viewer and cursor are absent.

### Database

- No migration required.

### Permissions and scope

- No permission changes; the feed remains public and optional bearer-token validation remains backend-enforced.

### Frontend

- No frontend changes.

### Verification

- `[passed] direct SqlAlchemyWorkRepository.list_published(None, 21, None) query against Supabase — feed_rows=0`
- `[passed] production Lambda logs identified asyncpg AmbiguousParameterError before the correction`

### Deployment

- Redeploy `inkfig-main-system` through the existing GitHub Actions workflow.
- No migration or configuration changes are required.

### Git

- Branch: `main`
- Commit: `749d701`
- Push: `successful`

### Notes

The failure was specific to asyncpg preparing untyped null bind parameters; explicit `uuid` and `timestamptz` casts make the statement deterministic.

## 2026-10-04 - Add canonical work categories and feed filtering

### Request

Create Digital Art, Hand Art, Video, Audio, Animation, Games, Interactive, and VR/AR categories and support homepage navigation between them.

### Changes

- Added an idempotent migration that inserts or reactivates all eight canonical work types with English and Arabic names.
- Added an optional `type_code` query parameter to the public works feed.
- Passed the selected type code through the API route, service, repository contract, and PostgreSQL repository.
- Added a parameterized work-type predicate to the published-feed query without changing public visibility, pagination, or like behavior.
- Added service regression coverage proving a category code reaches the repository.
- Preserved Lambda initialization and dependency construction, so the change remains compatible with future AWS Lambda SnapStart use.

### Repositories

- `inkfig-main-system`: seeds canonical types and filters the public feed authoritatively.
- `inkfig-user-FE`: provides the localized homepage category controls and sends `type_code`.
- `inkfig-user-system`: no changes required.

### Files

- `migrations/20261004_001_seed_work_categories.sql`: upserts the eight active bilingual categories.
- `src/interface/api/routes/works.py`: accepts the optional validated `type_code` filter.
- `src/app/services/work_service.py`: forwards the filter while preserving pagination.
- `src/entities/repositories/works.py`: extends the repository contract.
- `src/infrastructure/repositories/work_repository.py`: applies the parameterized category predicate.
- `tests/test_work_service.py`: verifies filter propagation.
- `AGENT_FEATURE_LOG.md`: records this ticket.

### API

- `GET /api/v1/works` accepts optional `type_code` (1-64 characters).
- Omitting `type_code` preserves the existing all-works feed.
- Supplying a canonical code returns published works from that category only.
- Response fields, pagination shape, authentication behavior, and errors are unchanged.

### Database

- Migration required: `20261004_001_seed_work_categories.sql`.
- The migration is idempotent through `ON CONFLICT (code) DO UPDATE` and reactivates canonical categories.

### Permissions and scope

- The public feed remains publicly readable.
- Uploads remain authenticated and backend-authorized.
- Category filtering cannot broaden visibility; it only narrows the existing published feed.
- Existing service-role-only table access and backend authorization remain authoritative.

### Frontend

The paired frontend change renders the categories as a localized homepage filter and sends the selected canonical code to this endpoint.

### Verification

- `[passed] git diff --check`
- `[passed] migration-runner inspection` - the existing runner discovers all sorted `*.sql` migrations, including the new seed file.
- `[not run] pytest, mypy, and compileall` - no Python interpreter is installed or discoverable in this environment.
- `[not run] sam validate --lint` - AWS SAM CLI is not installed in this environment.

### Deployment

- Deploy `inkfig-main-system` first and run `migrations/run.py` so all eight work types exist before exposing the filter.
- Deploy `inkfig-user-FE` second.
- No new environment variables are required.

### Git

- Branch: `main`
- Commit: this ticket's focused commit.
- Push: pushed directly to `origin/main` after synchronization.

### Notes

The migration owns stable category codes while display names remain bilingual and can be updated safely without changing filter URLs.
## 2026-10-04 - Synchronize main API JWT validation secret

### Request

Fix `Invalid or expired access token.` when an authenticated user attempts to upload a work.

### Changes

- Diagnosed the deployed Lambda configuration and confirmed the user API had a JWT signing secret while the main API secret was empty.
- Updated the main deployment workflow to securely read the existing signing secret from the deployed user API after AWS authentication.
- Masks the secret before adding it to the GitHub Actions environment and stops deployment when the source secret is missing.
- Removed the ineffective dependency on a separate main-repository `JWT_SECRET` GitHub secret.
- Left token claims, expiry, upload behavior, APIs, and database structure unchanged.

### Repositories

- `inkfig-main-system`: corrected production JWT-secret provisioning and added regression coverage.

### Files

- `.github/workflows/deploy.yml`: retrieves, validates, masks, and passes the shared user API JWT secret into the main SAM stack.
- `tests/test_health.py`: verifies the deployment cannot regress to an independent or missing JWT secret.

### API

- No API contract changes. Authenticated work endpoints now accept valid access tokens issued by `inkfig-user-system` after deployment.

### Database

- No migration required.

### Permissions and scope

- Existing authenticated-user and work-owner rules are unchanged.
- JWT signature, issuer, token type, expiry, and subject validation remain backend-enforced.
- The main GitHub deployment role requires `lambda:GetFunctionConfiguration` for `inkfig-user-system-api`.

### Frontend

- No frontend changes.

### Verification

- `[passed] deployed Lambda configuration comparison — issuer values matched; main secret was confirmed empty without printing either secret`
- `[passed] uv run --with-requirements requirements.txt ruff check src tests`
- `[passed] uv run --with-requirements requirements.txt pytest — 10 tests passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 43 source files`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` through GitHub Actions.
- No migration is required.
- The user API must remain deployed with a nonempty `JWT_SECRET`; no new frontend or GitHub secret is required.

### Git

- Branch: `main`
- Commit: `a230f27`
- Push: `successful`

### Notes

The signing value remains secret and was never printed. A future central AWS Secrets Manager value could replace the user Lambda as the shared source of truth if desired.

## 2026-10-04 - Permit main deployment to read shared JWT configuration

### Request

Complete the JWT synchronization deployment after GitHub Actions was denied while reading the user API Lambda configuration.

### Changes

- Added `lambda:GetFunctionConfiguration` to the main GitHub deployment role for only `inkfig-user-system-api`.
- Preserved every existing deployment-role statement unchanged.
- Removed the temporary local policy document after application.

### Repositories

- `inkfig-main-system`: recorded the required external IAM deployment permission.

### Files

- `AGENT_FEATURE_LOG.md`: records the IAM correction and verification.

### API

No API changes.

### Database

No migration required.

### Permissions and scope

- AWS role `InkFigMainSamDeployPolicy` can read configuration only from `arn:aws:lambda:eu-west-1:710412005992:function:inkfig-user-system-api` in addition to its existing permissions.
- No runtime application role or end-user permission changed.

### Frontend

No frontend changes.

### Verification

- `[passed] aws iam simulate-principal-policy — lambda:GetFunctionConfiguration evaluated as allowed for the exact user API Lambda ARN`
- `[failed] initial GitHub Actions run 37220723930 — deployment role lacked the new read permission`

### Deployment

- Rerun the `inkfig-main-system` GitHub Actions deployment.
- No migration or environment-variable change is required.

### Git

- Branch: `main`
- Commit: `documentation-only deployment retry commit`
- Push: `successful`

### Notes

The IAM permission is infrastructure state outside the SAM application stack and was applied directly to the existing GitHub deployment role.
## 2026-10-04 - Add optional external links to works

### Request

Allow users to attach an optional link to an uploaded work and safely validate it.

### Changes

- Added an optional HTTP/HTTPS external URL to work creation and public feed responses.
- Persists a normalized URL or `null` when no link is supplied.
- Rejects malformed URLs and non-HTTP schemes through backend DTO validation and a database constraint.
- Intentionally does not request user-supplied destinations during upload, avoiding SSRF and unreliable availability checks.

### Repositories

- `inkfig-main-system`: added API validation, persistence, feed output, migration, and tests.
- `inkfig-user-FE`: adds the optional form field and public link presentation separately.

### Files

- `src/entities/dto/works.py`: adds validated request and nullable response URL fields.
- `src/infrastructure/db/postgres/models/work.py`: maps the nullable URL column.
- `src/infrastructure/repositories/work_repository.py`: stores and returns work links.
- `migrations/20261004_002_add_work_external_url.sql`: adds the nullable constrained column.
- `tests/test_work_service.py`: verifies valid HTTP URLs and rejects unsafe schemes.

### API

- `POST /api/v1/works/uploads`: accepts optional `external_url`; it must be a complete HTTP/HTTPS URL and is limited to 2083 characters.
- `GET /api/v1/works`: each item now includes nullable `external_url`.

### Database

- Migration: `20261004_002_add_work_external_url.sql`
- Adds nullable `works.external_url varchar(2083)` with an HTTP/HTTPS check; existing rows remain `null` and require no backfill. Rollback drops the constraint and column.

### Permissions and scope

- Only authenticated users can submit the link as part of an upload draft.
- Published links are publicly visible with their work.
- Validation is backend- and database-enforced; no new role or permission is introduced.

### Frontend

- No frontend changes in this repository; corresponding changes are in `inkfig-user-FE`.

### Verification

- `[passed] uv run --with-requirements requirements.txt ruff check src tests migrations`
- `[passed] uv run --with-requirements requirements.txt pytest — 11 tests passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests`
- `[passed] python -m migrations.run — migration applied and works schema verified`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` before `inkfig-user-FE`; migration 20261004_002 must run first and is included in the backend workflow.
- No environment-variable changes are required.

### Git

- Branch: `main`
- Commit: `517a8ed`
- Push: `successful`

### Notes

Future link-health monitoring should run asynchronously in a hardened checker that blocks private/reserved IPs, limits redirects and response sizes, and applies strict timeouts.
## 2026-10-04 - Support multiple safe links per work

### Request

Replace the single optional work link with multiple safe links.

### Changes

- Supports up to 10 unique HTTP/HTTPS links per work, each with an optional 120-character label and stable order.
- Migrates existing single links, stores new links transactionally with the draft, and returns ordered links in the public feed.
- Rejects unsafe schemes, duplicates, excessive links, and invalid positions. Automatic destination requests remain intentionally excluded to prevent SSRF.

### Repositories

- `inkfig-main-system`: multi-link DTOs, model, persistence, migration, feed response, and tests.
- `inkfig-user-FE`: multi-link controls and rendering in a paired change.

### Files

- `migrations/20261004_003_create_work_links.sql`: creates and secures `work_links`, backfills old links, and removes the legacy column.
- `src/entities/dto/works.py`: adds link request/response contracts and uniqueness/count validation.
- `src/infrastructure/db/postgres/models/work.py`: maps ordered work links.
- `src/infrastructure/repositories/work_repository.py`: persists and aggregates links.

### API

- `POST /api/v1/works/uploads`: replaces `external_url` with `links`, an optional array of at most 10 `{url,label}` objects.
- `GET /api/v1/works`: replaces `external_url` with an ordered `links` array.

### Database

- Migration: `20261004_003_create_work_links.sql`
- Creates `work_links` with cascading work FK, HTTP/HTTPS check, unique work/URL and work/position constraints, order index, RLS, and service-role grants; backfills existing links before dropping `works.external_url`.

### Permissions and scope

- Authenticated users submit links with owned drafts; published links are public. Backend and database enforce safety and scope.

### Frontend

- No frontend changes in this repository.

### Verification

- `[passed] ruff check`
- `[passed] pytest — 11 tests passed`
- `[passed] mypy — no issues`
- `[passed] migration applied and verified`

### Deployment

- Deploy backend before frontend; migration 003 must run first. No configuration changes.

### Git

- Branch: `main`
- Commit: `eeeeb84`
- Push: `successful`

### Notes

Health monitoring remains future hardened asynchronous work.

## 2026-10-04 - Add authenticated profile feeds

### Request

Support a user profile that lists the authenticated user's published posts and the published posts they liked.

### Changes

- Added authenticated, paginated feeds for the current user's published works and liked works.
- Reused the existing published-work response so profile cards include artwork metadata, ordered links, like counts, and viewer like state.
- Scoped both queries exclusively from the verified backend user ID; clients cannot request another user's profile collections through these endpoints.
- Kept the public feed, uploads, likes, storage, and existing schema unchanged.

### Repositories

- `inkfig-main-system`: added backend-authorized profile feed queries.
- `inkfig-user-FE`: consumes the feeds in the new profile page.

### Files

- `src/interface/api/routes/works.py`: added current-user post and like routes.
- `src/app/services/work_service.py`: added the profile-feed workflow and pagination.
- `src/entities/repositories/works.py`: extended the repository contract with owner and liker scopes.
- `src/infrastructure/repositories/work_repository.py`: added SQL owner and liked-by filtering.
- `tests/test_work_service.py`: verifies authenticated scope selection.

### API

- `GET /api/v1/works/me`: returns up to 50 published works owned by the authenticated user; supports `limit` and `before`; returns 401 for an invalid or missing token.
- `GET /api/v1/works/likes`: returns up to 50 published works liked by the authenticated user; supports `limit` and `before`; returns 401 for an invalid or missing token.
- Existing response fields and public-feed behavior are unchanged.

### Database

No migration required. Queries use the existing `works.owner_user_id` and `work_likes` relationships and existing indexes.

### Permissions and scope

- Both endpoints require a valid InkFig access token.
- Any authenticated user can read only their own posts and likes collections.
- User scope is derived and validated by the backend; no user ID is accepted from the client.

### Frontend

- Paired frontend adds the protected profile route, posts section, and Likes section.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest — 13 tests passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 43 source files`
- `[passed] uv run --with-requirements requirements.txt ruff check src tests`
- `[passed] uv run --with-requirements requirements.txt ruff format src tests`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` before `inkfig-user-FE`.
- No migration or environment-variable changes are required.

### Git

- Branch: `main`
- Commit: `f050498`
- Push: `successful`

### Notes

Profile collections currently return the first 50 items; API cursors are available for future load-more UI.

## 2026-10-05 - Authenticate requests from secure access cookies

### Request

Accept the user backend's HTTP-only access cookie so protected main-system APIs no longer require frontend-managed bearer tokens.

### Changes

- Reads the signed access token from the configured cookie and validates its signature, issuer, type, expiry, and user ID.
- Retains temporary Authorization Bearer compatibility for safe staged deployment and existing sessions.
- Kept all work ownership, likes, profile scope, and public-feed behavior unchanged.

### Repositories

- `inkfig-main-system`: added access-cookie authentication.
- `inkfig-user-system`: issues the shared access cookie.
- `inkfig-user-FE`: sends credentialed requests.

### Files

- `src/interface/dependencies/authentication.py`: resolves cookie authentication with bearer fallback.
- `src/infrastructure/config/settings.py`, `.env.example`, `template.yaml`: configure the access-cookie name.
- `tests/test_cookie_authentication.py`: proves a valid signed cookie identifies its user.

### API

- All existing protected `/api/v1/works/*` endpoints accept `inkfig_access` as an HTTP-only cookie.
- Invalid or expired cookies return 401 and missing credentials retain existing authentication behavior.

### Database

No migration required.

### Permissions and scope

- Existing backend authorization and authenticated-user scope remain authoritative.
- Cookie contents are signature- and expiry-validated before the user ID is trusted.

### Frontend

- No UI changes in this repository.

### Verification

- `[passed] pytest — 14 tests passed`
- `[passed] mypy src tests — no issues in 44 source files`
- `[passed] ruff check src tests`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` before the cookie-only user API response and frontend.
- No migration, new secret, or external configuration is required.

### Git

- Branch: `main`
- Commit: `911498d`
- Push: `successful`

### Notes

Bearer fallback prevents disruption to existing sessions during the staged rollout and can be removed in a later hardening ticket.
## 2026-10-05 - Enforce work permissions

### Request

Protect every interactive work endpoint with the new role-permission model.

### Changes

- Parses signed role and permission claims into an authenticated principal.
- Requires explicit permissions for uploads, publishing, likes, and private profile feeds.
- Leaves the public artwork feed and work types public.

### Repositories

- `inkfig-main-system`: enforces work permissions.
- `inkfig-user-system`: issues the signed claims.
- `inkfig-user-FE`: hides and guards restricted actions.

### Files

- `src/interface/dependencies/authentication.py`: adds principal parsing and permission dependencies.
- `src/interface/api/routes/works.py`: declares permission requirements.

### API

- `POST /api/v1/works/uploads` and `POST /api/v1/works/{work_id}/publish`: require works.upload.
- `PUT|DELETE /api/v1/works/{work_id}/like`: require works.like.
- `GET /api/v1/works/me` and `GET /api/v1/works/likes`: require profile.read_own.
- Missing authentication returns 401; missing permission returns 403.

### Database

No migration required.

### Permissions and scope

- Viewer has no protected work permissions.
- User, supervisor, admin, and system-administrator retain current work abilities.
- Authorization is validated by this backend from signed claims.

### Frontend

No frontend changes in this repository.

### Verification

- `[passed] py -3.12 -m pytest -q - 14 tests passed`
- `[passed] py -3.12 -m mypy src tests - 44 files`
- `[passed] py -3.12 -m compileall -q src tests`
- `[passed] git diff --check`

### Deployment

- Deploy after user-system migration 007 and backend deployment.
- No environment-variable changes are required.

### Git

- Branch: `main`
- Commit: `a0ac6c9`
- Push: `successful`

### Notes

Public homepage reads remain intentionally unauthenticated.

## 2026-10-05 - Persist authenticated artwork saves

### Request

Allow registered users to save published artwork and expose their saved collection on their profile.

### Changes

- Added persistent per-user artwork saves with idempotent save and unsave operations.
- Added viewer-specific saved state to every published-work response.
- Added an authenticated saved-artwork feed scoped exclusively from the verified current user.
- Protected save mutations with the new works.save permission and saved-feed reads with profile.read_own.
- Added service coverage for authenticated saved-feed scope and save delegation.

### Repositories

- inkfig-main-system: save persistence, API endpoints, saved feed, migration, authorization, and tests.
- inkfig-user-system: grants works.save to registered interactive roles in a paired migration.
- inkfig-user-FE: adds the bookmark interaction and Saved profile tab.

### Files

- migrations/20261005_004_create_work_saves.sql: creates the secured work_saves relation and user/date index.
- src/infrastructure/db/postgres/models/work.py: maps saved works.
- src/entities/dto/works.py: exposes saved_by_me.
- src/entities/repositories/works.py: extends save and saved-feed contracts.
- src/infrastructure/repositories/work_repository.py: persists saves and queries viewer/profile state.
- src/app/services/work_service.py: adds saved profile scope and save workflow.
- src/interface/api/routes/works.py: adds saved-feed and save/unsave routes with backend permissions.
- tests/test_work_service.py: covers save scope and service delegation.
- AGENT_FEATURE_LOG.md: records this ticket.

### API

- GET /api/v1/works/saves returns the authenticated user's saved published works.
- PUT /api/v1/works/{work_id}/save saves a published work.
- DELETE /api/v1/works/{work_id}/save removes it from saved works.
- Published work responses now include saved_by_me.
- Save mutations return 401 without authentication, 403 without works.save, and 404 for unavailable works.

### Database

- Migration: migrations/20261005_004_create_work_saves.sql.
- Creates work_saves with a cascading work foreign key, unique work/user primary key, created timestamp, user/date index, RLS, and service-role-only access.

### Permissions and scope

- Save mutations require a signed works.save claim.
- Saved-feed reads require profile.read_own.
- User identity always comes from the verified backend principal; no client-supplied user ID is accepted.
- Only published works can be saved.

### Frontend

No frontend files changed in this repository. Paired frontend work adds the bookmark and Saved tab.

### Verification

- [passed] git diff --check
- [passed] focused static review of migration, route permissions, service scope, repository parameters, and response mapping.
- [not run] pytest, mypy, Ruff, and compileall - no usable Python runtime or project runner is installed in this session.

### Deployment

- First apply inkfig-user-system migration 20261005_008_add_work_save_permission.sql and deploy the user system.
- Then apply migrations/20261005_004_create_work_saves.sql and deploy inkfig-main-system.
- Deploy inkfig-user-FE last.
- No new environment variables or secrets are required.

### Git

- Branch: main
- Commit: this ticket's focused commit.
- Push: pushed directly to origin/main after synchronization.

### Notes

Existing sessions must refresh or sign in again after the permission migration so their signed access claim includes works.save.
## 2026-10-06 - Optimize artwork database indexes

### Request

Review and optimize the database and indexing for current InkFig workloads, and make query/index review a standard consideration for future database work.

### Changes

- Replaced the mismatched published-work index on `published_at` with partial composite indexes matching the actual `created_at` feed order.
- Added workload-specific published-feed indexes for the global, work-type, and owner views.
- Added user-first composite indexes for liked and saved profile collections.
- Removed the redundant work-link ordering index because the existing unique `(work_id, position)` constraint already provides the same B-tree prefix.
- Changed optional feed filters from nullable `OR` expressions to fixed conditional predicates and joins so PostgreSQL can select the relevant partial/composite index.
- Added a stable `work_id` ordering tie-breaker while preserving the existing timestamp cursor API.
- Left authorization, storage, API contracts, and frontend behavior unchanged.

### Repositories

- `inkfig-main-system`: optimized artwork query construction and database indexes.

### Files

- `src/infrastructure/repositories/work_repository.py`: made feed SQL index-friendly and deterministically ordered.
- `migrations/20261006_005_optimize_query_indexes.sql`: replaced redundant/mismatched indexes and added workload-aligned indexes.
- `tests/test_query_indexes.py`: added regression coverage for index definitions and query shape.

### API

No API changes.

### Database

- Migration: `20261006_005_optimize_query_indexes.sql`
- Replaces the old public-feed and owner indexes with partial published-work indexes on global `(created_at DESC, work_id DESC)`, type `(type_id, created_at DESC, work_id DESC)`, and owner `(owner_user_id, created_at DESC, work_id DESC)` access paths.
- Adds `(user_id, created_at DESC, work_id DESC)` indexes to likes and saves, and removes the redundant work-link ordering index.
- No data backfill, constraint, default, or foreign-key changes are required. Rollback can drop the new indexes and recreate the prior indexes, with no data loss.

### Permissions and scope

- Public published-feed reads remain available without a permission.
- `profile.read_own` remains required for owned, liked, and saved profile feeds.
- `works.like` and `works.save` remain required for their respective mutations.
- Role and user scope rules are unchanged and continue to be validated by the backend.

### Frontend

No frontend changes.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q — 19 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 45 files`
- `[passed] uv run --with-requirements requirements.txt ruff check src/infrastructure/repositories/work_repository.py tests/test_query_indexes.py`
- `[passed] uv run --with-requirements requirements.txt python -m compileall -q src tests`
- `[passed] python -m migrations.run — migration applied and works tables/storage verified`
- `[passed] live pg_indexes query — all artwork indexes and partial predicates verified on Supabase`
- `[failed] uv run --with-requirements requirements.txt ruff check src tests — unrelated pre-existing findings in src/interface/dependencies/authentication.py`

### Deployment

- Deploy `inkfig-main-system`.
- Run `20261006_005_optimize_query_indexes.sql` before deploying the application; it has already been applied to the configured Supabase database.
- No environment-variable or configuration changes.

### Git

- Branch: `main`
- Commit: `bfdae62`
- Push: `successful`

### Notes

- Future database tickets must compare query predicates, join direction, ordering, and pagination with existing indexes and avoid redundant or low-selectivity indexes.
- Query plans should be reassessed using production-scale statistics as table cardinality grows; small tables may correctly use sequential scans despite having suitable indexes.
## 2026-10-06 - Expose public profile artwork feeds

### Request

Allow a profile page to display all published artworks owned by the selected InkFig account.

### Changes

- Added a public profile artwork use case that scopes the feed to the requested owner while preserving viewer-specific like and save state.
- Reused the optimized published-owner feed query and indexes.
- Left upload, ownership mutation, likes, saves, and private profile collections unchanged.

### Repositories

- `inkfig-main-system`: exposes published work for a selected owner.
- `inkfig-user-system`: owns profile data and follow relationships.
- `inkfig-user-FE`: consumes the profile artwork endpoint.

### Files

- `src/app/services/work_service.py`: adds the public profile feed workflow.
- `src/interface/api/routes/works.py`: adds the owner-specific published-work route.
- `tests/test_work_service.py`: verifies separation of requested owner and current viewer scope.

### API

- `GET /api/v1/works/users/{user_id}`: returns published artworks owned by `user_id`; accepts the existing `limit` and `before` pagination fields, includes viewer-specific like/save state when authenticated, and remains publicly readable.

### Database

- No migration required.
- The endpoint uses the existing partial `works_published_owner_feed_idx` plus primary/relationship indexes.

### Permissions and scope

- No permission is required to view published artwork.
- Optional authentication only personalizes like and save state.
- The backend fixes owner scope from the path UUID and never accepts owner scope from response or client state.

### Frontend

No frontend changes in this repository. The coordinated profile UI is in `inkfig-user-FE`.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q — 20 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests — no issues in 45 files`
- `[passed] ruff check on all changed main-backend files`
- `[passed] python -m compileall -q src tests`

### Deployment

- Deploy `inkfig-main-system`.
- No migrations or configuration changes are required.

### Git

- Branch: `main`
- Commit: `f153b54`
- Push: `successful`

### Notes

None

## 2026-10-06 - Hide inactive-account artwork and activity

Updated published-work queries to require an active owner and to count likes only from active accounts. This keeps deactivated or administrator-suspended profiles, works, and like activity out of public and profile feeds while retaining data for safe reactivation.

- No API or migration in this repository.
- Verification: `git diff --check` passed.
- Deployment: deploy after the user-system account-status migration.
- Branch: `feature/account-status-lifecycle`; push to `main` after synchronization.
## 2026-10-06 - Voyage semantic artwork search

### Request

Add Voyage AI to let visitors find artworks from English or Arabic text descriptions, with production-safe Lambda permissions and optimized vector storage.

### Changes

- Added a clean-architecture Voyage multimodal embedding adapter backed by AWS Secrets Manager.
- Embedded newly published artwork images without making publication fail when Voyage is temporarily unavailable.
- Added bounded automatic catch-up indexing for previously published artworks and missed embeddings.
- Added cosine-similarity artwork search with optional work-type filtering and active-account enforcement.
- Kept existing feeds, likes, saves, uploads, and profile behavior unchanged.

### Repositories

- `inkfig-main-system`: added semantic embedding, retrieval, persistence, API, migration, and Lambda configuration.
- `inkfig-user-FE`: consumes the search API in the public home search experience.

### Files

- `src/infrastructure/integrations/voyage_embeddings.py`: calls Voyage multimodal embeddings and loads its API key securely.
- `src/app/services/work_service.py`: orchestrates indexing, bounded catch-up, and semantic search.
- `src/infrastructure/repositories/work_repository.py`: persists vectors and performs indexed cosine search.
- `src/interface/api/routes/works.py`: exposes the semantic search endpoint.
- `migrations/20261006_006_add_work_embeddings.sql`: enables pgvector and creates vector storage and an HNSW index.
- `template.yaml`: configures Voyage and grants narrowly scoped Secrets Manager access.
- `tests/test_work_service.py`: verifies search, catch-up, and failure resilience.
- `tests/test_voyage_embeddings.py`: verifies Voyage request semantics.

### API

- `GET /api/v1/works/search`: accepts required `query` (2-500 characters), optional `type_code`, and `limit` (1-50); returns ranked published works, preserves optional viewer like/save state, and returns 503 when semantic search is unavailable.

### Database

- Migration: `20261006_006_add_work_embeddings.sql`
- Enables the Supabase `vector` extension, creates `work_embeddings` with a cascading work foreign key, 1024-dimensional embeddings, model metadata and timestamps, and adds an HNSW cosine index. Rollback requires dropping `work_embeddings`; the shared vector extension should only be dropped after confirming no other feature uses it.

### Permissions and scope

- Public viewers and all roles may search published works; authentication remains optional and only enriches like/save state.
- Only published works owned by active accounts are returned.
- Existing `works.upload` backend authorization still controls publication; no new application permission is required.
- Lambda can only read Secrets Manager resources matching `inkfig/main/voyage-*`; backend query scope is enforced by SQL.

### Frontend

- The existing localized home search bar now sends debounced semantic searches after two characters.
- Category filters are passed to semantic search, and localized loading, empty, and unavailable states are shown.
- Existing responsive artwork cards, navigation, detail modal, likes, saves, RTL/LTR behavior, and feed behavior remain unchanged.

### Verification

- `[passed] py -3.12 -m pytest` (25 tests)
- `[passed] py -3.12 -m mypy src`
- `[passed] sam build --cached`
- `[passed] sam validate --lint` (template valid; local SAM telemetry metadata emitted a filesystem warning)
- `[passed] npm.cmd test` (43 tests in `inkfig-user-FE`)
- `[passed] npm.cmd run build` in `inkfig-user-FE`

### Deployment

- Deploy `inkfig-main-system` first; its workflow must run migration `20261006_006_add_work_embeddings.sql` before Lambda deployment.
- Deploy `inkfig-user-FE` after the backend is healthy.
- AWS Secrets Manager secret `inkfig/main/voyage` must contain `VOYAGE_API_KEY`; no Voyage key is exposed to the frontend or GitHub variables.

### Git

- Branch: `main`
- Commit: `6c9f896`
- Push: `successful`

### Notes

The first searches may take longer while at most five missing artwork embeddings are generated per request. Failed items remain eligible for a later retry, and normal publication remains available during Voyage outages.
## 2026-10-06 - Restore Voyage deployment pipeline

### Request

Complete and deploy the Voyage semantic artwork search integration.

### Changes

- Made the optional `boto3` import type annotation portable across local development and GitHub Actions environments.
- Left application behavior, API behavior, database schema, and authorization unchanged.

### Repositories

- `inkfig-main-system`: fixed CI type-check compatibility.

### Files

- `src/infrastructure/integrations/voyage_embeddings.py`: accepts both missing-module and untyped-module MyPy classifications.

### API

No API changes.

### Database

- Migration: `20261006_006_add_work_embeddings.sql`
- No additional migration required; the Voyage migration was successfully applied by the restored deployment.

### Permissions and scope

- No permission changes.
- Existing public-search and active-account scope remains validated by the backend.

### Frontend

No frontend changes.

### Verification

- `[passed] py -3.12 -m pytest` (25 tests)
- `[passed] py -3.12 -m mypy src tests` (47 source files)
- `[passed] GitHub Actions run 37504256584`
- `[passed] AWS CloudFormation stack status UPDATE_COMPLETE`
- `[passed] GET https://main-api.inkfig-hu.com/health`
- `[failed] GET /api/v1/works/search?query=moon — Voyage returned HTTP 429 because the organization has no payment method and is limited to 3 requests per minute`

### Deployment

- `inkfig-main-system` deployed successfully, including the pgvector migration and Lambda policy.
- Add a payment method to the Voyage organization to unlock standard rate limits; Voyage states the free Voyage 3 token allowance remains available afterward.

### Git

- Branch: `main`
- Commit: `4f59663`
- Push: `successful`

### Notes

The stored key, Secrets Manager secret, Lambda configuration, CloudFormation deployment, and database migration are correct. Reliable production search is externally blocked only by the Voyage account's reduced 3-RPM limit.
## 2026-10-06 - Delete all existing artworks

### Request

Permanently remove all previously uploaded artwork records so future works enter the Voyage embedding process from publication.

### Changes

- Added a one-time migration that deletes every row from the parent `works` table.
- Relied on existing cascading foreign keys to delete associated links, likes, saves, and embeddings atomically.
- Intentionally left users, work types, permissions, and Supabase Storage objects unchanged.

### Repositories

- `inkfig-main-system`: added the destructive artwork-data reset migration and regression test.

### Files

- `migrations/20261006_007_delete_existing_works.sql`: deletes all existing artwork database records.
- `tests/test_delete_existing_works_migration.py`: verifies the reset targets only the parent works table and does not directly manipulate Storage metadata.

### API

No API changes.

### Database

- Migration: `20261006_007_delete_existing_works.sql`
- Deletes all rows from `public.works`; foreign-key cascades delete matching `work_links`, `work_likes`, `work_saves`, and `work_embeddings` rows. This data deletion has no automatic rollback or backfill. Users and canonical work types remain intact.

### Permissions and scope

- No application permissions or role access changed.
- This deployment-time migration affects artworks belonging to every user and bypasses application endpoints by design.
- Normal backend authorization remains unchanged after the reset.

### Frontend

No frontend changes. Existing feeds and profiles display their normal empty states after the migration.

### Verification

- `[passed] py -3.12 -m pytest` (26 tests)
- `[passed] py -3.12 -m mypy src tests` (48 source files)
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system`; GitHub Actions must apply `20261006_007_delete_existing_works.sql` before deploying Lambda.
- No environment-variable changes are required.
- Supabase Storage image objects are not deleted and may be purged separately through the Storage API if required.

### Git

- Branch: `main`
- Commit: `60175da`
- Push: `successful`

### Notes

The database deletion is permanent. Preserving Storage objects avoids unsupported direct SQL deletion from Supabase Storage but leaves orphaned image files until an explicit Storage cleanup is performed.
## 2026-10-07 - Reset artworks after semantic-search testing

### Request

Permanently remove every current artwork after testing the Voyage text-to-image search workflow.

### Changes

- Added a second one-time migration that deletes every current row from `public.works`.
- Existing cascading foreign keys delete associated links, likes, saves, and embeddings atomically.
- Intentionally left users, work types, permissions, and Supabase Storage objects unchanged.

### Repositories

- `inkfig-main-system`: added and tested the second destructive artwork reset migration.

### Files

- `migrations/20261007_008_delete_existing_works.sql`: deletes all current artwork database records.
- `tests/test_delete_existing_works_migration.py`: verifies both reset migrations use the cascading parent delete and do not directly modify Storage metadata.

### API

No API changes.

### Database

- Migration: `20261007_008_delete_existing_works.sql`
- Deletes all `public.works` rows and cascades to `work_links`, `work_likes`, `work_saves`, and `work_embeddings`. The deletion has no automatic rollback. User accounts and canonical work types remain unchanged.

### Permissions and scope

- No roles or permissions changed.
- The deployment migration affects artworks owned by every account and intentionally runs outside application endpoint authorization.
- Normal backend authorization remains enforced after the reset.

### Frontend

No frontend changes. Artwork feeds and profiles use their existing empty states after deletion.

### Verification

- `[passed] py -3.12 -m pytest` (26 tests)
- `[passed] py -3.12 -m mypy src tests` (48 source files)
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system`; GitHub Actions must apply `20261007_008_delete_existing_works.sql` before Lambda deployment.
- No environment-variable changes are required.
- Supabase Storage objects are intentionally retained and require separate Storage API cleanup if physical deletion is later requested.

### Git

- Branch: `main`
- Commit: `bed6735`
- Push: `successful`

### Notes

This migration permanently deletes the current artwork database data. Preserved Storage objects become orphaned and are not visible through InkFig feeds.
## 2026-10-07 - Support oversized artwork embeddings and relevant search results

### Request

Fix semantic search so high-resolution artworks are embedded, unrelated nearest-neighbor results are excluded, reset existing works, and prepare the system for live two-image testing.

### Changes

- Downloads each published artwork into Lambda memory and creates an aspect-ratio-preserving JPEG derivative capped at two million pixels for Voyage.
- Keeps the original Supabase Storage object and its displayed resolution unchanged.
- Added a configurable cosine-similarity threshold so weak matches are excluded instead of always returning the nearest indexed artwork.
- Added structured exception logging for publication and catch-up embedding failures.
- Added a one-time reset migration that deleted the current works and their cascading related records before retesting.

### Repositories

- `inkfig-main-system`: added safe image preprocessing, relevance filtering, diagnostics, reset migration, and tests.

### Files

- `src/infrastructure/integrations/voyage_embeddings.py`: fetches, safely validates, resizes, and encodes artwork derivatives for Voyage.
- `src/infrastructure/repositories/work_repository.py`: applies the minimum semantic similarity filter.
- `src/app/services/work_service.py`: passes search thresholds and logs embedding failures.
- `src/infrastructure/config/settings.py`: adds the semantic similarity configuration.
- `migrations/20261007_009_delete_works_before_search_retest.sql`: removes current artwork data before controlled retesting.
- `tests/test_voyage_embeddings.py`: verifies in-memory resizing and aspect-ratio preservation.
- `tests/test_query_indexes.py`: verifies semantic relevance filtering.

### API

- `GET /api/v1/works/search`: response shape is unchanged; results below `VOYAGE_MIN_SIMILARITY` are now omitted.

### Database

- Migration: `20261007_009_delete_works_before_search_retest.sql`
- Deletes all `public.works` rows and cascades to links, likes, saves, and embeddings. The deletion has no automatic rollback. No schema or index changes were required.

### Permissions and scope

- No roles or permissions changed.
- Search remains public and only returns published works owned by active accounts.
- Upload and publication remain protected by `works.upload`, with authorization validated by the backend.

### Frontend

No frontend changes. Original images continue to be displayed from Supabase Storage at their uploaded resolution.

### Verification

- `[passed] py -3.12 -m pytest` (28 tests)
- `[passed] py -3.12 -m mypy src tests` (48 source files)
- `[passed] sam build --cached`
- `[passed] GitHub Actions run 37546735220`
- `[passed] GET /api/v1/works returned an empty feed after migration`
- `[passed] close-up-full-bloom-flower.jpg confirmed as 3328x4864 (16,187,392 pixels), reproducing the previous Voyage limit failure`
- `[passed] images (1).jfif confirmed as 415x740 (307,100 pixels)`
- `[not run] authenticated browser uploads and UI searches — browser-control runtime is unavailable in this session`

### Deployment

- `inkfig-main-system` and migration `20261007_009_delete_works_before_search_retest.sql` deployed successfully.
- Added Lambda dependency `Pillow==11.3.0`.
- Added `VOYAGE_MIN_SIMILARITY=0.20`; no secret changes are required.

### Git

- Branch: `main`
- Commit: `7ed81e9`
- Push: `successful`

### Notes

The two requested files are available under `C:\Users\mohaamad\Downloads`. Live authenticated upload verification remains pending until browser control is available or the user uploads both files manually.

## 2026-10-07 - Expose semantic search ranking

### Request

Return each semantic-search result's rank to the frontend so artworks are displayed from most to least similar.

### Changes

- Added a search-specific response contract containing a one-based `search_rank` and cosine `similarity_score` for every returned artwork.
- Preserved database ordering by ascending cosine distance, then assigned ranks in that exact order.
- Kept ordinary home, profile, liked, and saved feed response contracts unchanged.
- Preserved the existing similarity threshold, category filter, active-owner scope, viewer-specific like/save state, and Voyage workflow.
- Intentionally left the existing local `samconfig.toml` modification unchanged.

### Repositories

- `inkfig-main-system`: exposes explicit semantic rank and similarity metadata.
- `inkfig-user-FE`: consumes rank metadata and renders search results in rank order.

### Files

- `src/entities/dto/works.py`: adds search-only artwork and feed response DTOs.
- `src/entities/repositories/works.py`: updates the semantic-search repository contract.
- `src/app/services/work_service.py`: returns the search-specific feed contract.
- `src/infrastructure/repositories/work_repository.py`: selects cosine similarity and assigns deterministic one-based ranks.
- `src/interface/api/routes/works.py`: publishes the search-specific response model.
- `tests/test_query_indexes.py`: verifies similarity selection and rank assignment.
- `tests/test_work_service.py`: verifies search ranking metadata validation.

### API

- `GET /api/v1/works/search`: each item now includes required `search_rank` and `similarity_score`; results remain ordered from highest to lowest similarity and weak results remain excluded by `VOYAGE_MIN_SIMILARITY`.
- Request fields, category filtering, limits, public access, and 503 behavior are unchanged.

### Database

No migration required. Similarity and rank are calculated at query/request time from existing pgvector embeddings; no stored schema, indexes, constraints, defaults, foreign keys, or backfill behavior changed.

### Permissions and scope

- No permission is required for public semantic search.
- Authenticated viewers continue receiving only their own like/save state.
- Only published works owned by active accounts are eligible.
- Authorization and data scope remain validated by the backend.

### Frontend

- The frontend receives `search_rank` and `similarity_score` and defensively sorts semantic results by ascending rank.
- No visual rank label, route, navigation, layout, localization, loading, empty, responsive, or error-state changes were requested or added.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q - 29 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests - no issues in 48 source files`
- `[passed] focused ruff check - all checks passed`
- `[passed] git diff --check`
- `[passed] frontend npm.cmd test - 44 passed`
- `[passed] frontend npm.cmd run build - TypeScript and Vite production build succeeded`

### Deployment

- Deploy `inkfig-main-system`, then deploy `inkfig-user-FE`.
- No migration must run before deployment.
- No environment-variable, secret, or configuration changes are required.

### Git

- Branch: `main`
- Commit: `328bcee`
- Push: `successful`

### Notes

`similarity_score` is cosine similarity, not a probability or confidence percentage.

## 2026-10-07 - Paginate semantic artwork search

### Request

Complete pagination across InkFig so artwork feeds and ranked semantic-search results can load beyond their first page.

### Changes

- Added a bounded continuation cursor to semantic search and returns `next_cursor` when more ranked results exist.
- Fetches one extra search row to determine whether another page exists without issuing a separate count query.
- Preserves continuous one-based search ranks across pages by starting each page at its cursor offset.
- Kept existing timestamp cursor pagination for public, profile, liked, and saved feeds unchanged.
- Preserved similarity thresholds, category filtering, active-account scope, and viewer-specific interaction state.
- Intentionally left the existing local `samconfig.toml` modification unchanged.

### Repositories

- `inkfig-main-system`: adds ranked semantic-search continuation support.
- `inkfig-user-FE`: consumes pagination for home, search, profile posts, likes, and saved works.

### Files

- `src/entities/dto/works.py`: adds `next_cursor` to semantic-search feeds.
- `src/entities/repositories/works.py`: adds repository offset input.
- `src/app/services/work_service.py`: computes the next search cursor using a limit-plus-one query.
- `src/infrastructure/repositories/work_repository.py`: applies the bounded offset and continuous rank numbering.
- `src/interface/api/routes/works.py`: accepts the validated search cursor.
- `tests/test_query_indexes.py`: verifies pagination query and rank behavior.
- `tests/test_work_service.py`: verifies continuation cursors, page size, and continuous ranks.

### API

- `GET /api/v1/works/search`: accepts optional `cursor` from 0 through 10,000 and returns nullable integer `next_cursor`; `limit`, `query`, `type_code`, ranking metadata, validation, public access, thresholding, and 503 behavior remain.
- `GET /api/v1/works`, `/me`, `/likes`, `/saves`, and `/users/{user_id}` retain their existing `before` timestamp cursor and nullable `next_cursor` behavior.

### Database

No migration required. Pagination uses existing ordering, pgvector search, feed indexes, and runtime query parameters. No schema, constraint, default, foreign-key, index, backfill, or rollback change is required.

### Permissions and scope

- Public feed and search pagination require no permission.
- Profile likes and saves still require `profile.read_own`.
- Search continues to return only published works owned by active accounts.
- Viewer like/save personalization and all authorization remain backend-validated.

### Frontend

- Home feed, semantic search, profile posts, likes, and saved works now consume continuation cursors through a localized Load more flow.
- Search ranking remains continuous and ordered across pages.
- Duplicate artwork IDs are excluded while appending pages.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q - 30 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests - no issues in 48 source files`
- `[passed] focused ruff check - all checks passed`
- `[passed] git diff --check`
- `[passed] frontend npm.cmd test - 44 passed`
- `[passed] frontend npm.cmd run build - TypeScript and Vite production build succeeded`

### Deployment

- Deploy `inkfig-main-system` before `inkfig-user-FE`.
- No migrations must run before deployment.
- No environment-variable, secret, or configuration changes are required.

### Git

- Branch: `main`
- Commit: `c5e8c03`
- Push: `successful`

### Notes

Semantic-search continuation is bounded to 10,000 ranked results to prevent unbounded database offsets.
## 2026-10-07 - Scope artwork feeds and semantic search to a selected account

### Request

When an account is selected through the frontend `@` search, return that user's matching works; when no artwork words accompany the selected account, return all public works for that user.

### Changes

- Added an optional immutable owner-user filter to the public artwork feed.
- Added the same owner filter to ranked semantic image search.
- Preserved category filtering, pagination, active-account scope, published-only scope, ranking, and viewer interaction state.
- Left uploads, likes, saves, embeddings, thresholds, and existing profile-feed routes unchanged.

### Repositories

- `inkfig-main-system`: owner-scoped public feed and semantic-search API behavior.
- `inkfig-user-system`: supplies privacy-safe account IDs from live account discovery.
- `inkfig-user-FE`: chooses between owner-only feed and owner-scoped semantic search.

### Files

- `src/entities/repositories/works.py`: extends semantic-search persistence with an optional owner ID.
- `src/app/services/work_service.py`: propagates owner scope through feed and search use cases.
- `src/infrastructure/repositories/work_repository.py`: applies a parameterized owner predicate to semantic search.
- `src/interface/api/routes/works.py`: accepts `owner_user_id` on public feed and search endpoints.
- `tests/test_work_service.py`: verifies owner scope for both paths.

### API

- `GET /api/v1/works`: accepts optional UUID `owner_user_id`; returns only published works from that active owner, with existing `type_code`, `before`, `limit`, and interaction behavior unchanged.
- `GET /api/v1/works/search`: accepts optional UUID `owner_user_id`; ranks only that active owner's published embedded works against the existing required `query`, with existing `type_code`, `cursor`, `limit`, threshold, ranking fields, validation, and 503 behavior unchanged.

### Database

- Migration: `No migration required`
- Owner filtering uses the existing owner/feed indexes and embedding structures. No schema, default, constraint, foreign-key, backfill, or rollback change is required.

### Permissions and scope

- No authenticated permission is required for public feed or search access.
- Viewer, user, supervisor, admin, and system-administrator clients receive published works belonging to active accounts only.
- The backend validates the UUID and enforces owner, publication, account-status, category, threshold, and pagination scope.

### Frontend

- `@Selected Account` with no other words uses the owner-filtered chronological feed.
- Artwork text combined with a selected account uses owner-filtered semantic ranking.
- Existing cards, category filters, responsive masonry layout, pagination, and interaction controls remain unchanged.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q - 32 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests - no issues in 48 source files`
- `[passed] focused ruff check for all changed main-backend files`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` after `inkfig-user-system` and before `inkfig-user-FE`.
- No migrations must run for this repository.
- No environment-variable or configuration changes are required.

### Git

- Branch: `main`
- Commit: `c1fd31d`
- Push: `successful`

### Notes

The existing local `samconfig.toml` modification was intentionally left unchanged and excluded from the commit.
## 2026-10-07 - Add owner-controlled work editing and complete deletion

### Request

Allow users to edit and delete only their own posts, prohibit image replacement during editing, and remove every post-owned database and storage resource when deleting.

### Changes

- Added owner-scoped metadata editing for title, description, category, and up to ten unique HTTP/HTTPS links.
- Deliberately excluded image, storage path, MIME type, and file size from the update contract.
- Added owner-scoped deletion that deletes and verifies the Supabase object before removing the work row.
- Relies on existing database cascades to remove the work's links, likes, saves, and Voyage embedding with the work row.
- Added validation for nonblank normalized titles and focused ownership/deletion-order tests.

### Repositories

- `inkfig-main-system`: backend contracts, authorization, persistence, storage deletion, tests, and this log.
- `inkfig-user-FE`: owner controls, editor, deletion confirmation, profile layout, and localization.
- `inkfig-user-system`: no changes required.

### API

- `PATCH /api/v1/works/{work_id}` updates owner-controlled metadata only.
- `DELETE /api/v1/works/{work_id}` permanently deletes the authenticated owner's work.
- Both endpoints require `works.upload`; repository predicates independently enforce `owner_user_id`.

### Database

- No migration required.
- Existing `ON DELETE CASCADE` constraints remove `work_links`, `work_likes`, `work_saves`, and `work_embeddings` records.

### Permissions and SnapStart

- Only the authenticated owner can mutate a work; non-owned and missing works return the same not-found response.
- Storage clients remain request-scoped and retain AWS Lambda SnapStart compatibility.

### Verification

- `[passed] git diff --check`
- `[passed] cascade audit` - every work-owned relational table uses `ON DELETE CASCADE`.
- `[added] service tests` - cover metadata-only editing, storage-before-database deletion, and non-owner rejection.
- `[not run] pytest and mypy` - no usable Python runtime or repository virtual environment is installed on this machine; GitHub Actions will run both.

### Deployment

- Deploy `inkfig-main-system` before `inkfig-user-FE`.
- No migration, secret, or environment-variable changes are required.

### Git

- Branch: `feature/owner-work-management`
- Commit, rebase, push, merge, and main push: pending final synchronization.

## 2026-10-07 - Repair previous artwork resets by deleting orphaned storage objects

### Request

Update the previous migrations that deleted all artworks so the corresponding files are also removed from Supabase Storage rather than deleting only database rows and links.

### Changes

- Added a tracked Python storage-migration mechanism alongside existing SQL migrations.
- Added an idempotent cleanup that finds objects in the exact `works` bucket whose paths are no longer referenced by any current `works.storage_path`.
- Deletes orphaned objects through the authenticated Supabase Storage API in bounded batches.
- Validates the configured bucket, rejects unsafe paths, verifies no orphaned objects remain, and records the migration only after successful completion.
- Deleted 13 orphaned artwork files left by the three earlier database-only reset migrations.
- Preserved every storage object referenced by a current artwork row and left current artwork records unchanged.
- Intentionally left the existing local `samconfig.toml` modification unchanged.

### Repositories

- `inkfig-main-system`: storage migration runner, orphan cleanup, verification tests, and applied cleanup.

### Files

- `migrations/run.py`: discovers ordered `*_storage.py` migrations, loads their async `apply` function, and records them in `schema_migrations` after success.
- `migrations/20261007_010_delete_orphaned_work_storage.py`: validates and removes only unreferenced objects from the Supabase works bucket.
- `tests/test_delete_existing_works_migration.py`: verifies discovery, database-reference exclusion, exact-bucket protection, API deletion, and post-delete verification.

### API

No API changes.

### Database

- Migration: `20261007_010_delete_orphaned_work_storage.py`
- Reads `storage.objects` and `public.works.storage_path` to identify orphaned files, deletes exact paths through Supabase Storage, verifies zero remaining orphans, and records the filename in `public.schema_migrations`.
- No schema, default, constraint, index, foreign-key, or application-row change is required.
- No automatic rollback is possible for deleted binary objects; database-referenced current artwork files are excluded before deletion.

### Permissions and scope

- Requires backend-only `SUPABASE_SECRET_KEY`, `SUPABASE_URL`, `DATABASE_URL`, and exact `WORKS_BUCKET=works` configuration.
- No end-user role or permission can invoke this migration through an API.
- Scope is enforced by exact bucket validation, database reference exclusion, path validation, bounded batching, and post-delete verification.
- Backend migration execution controls authorization; secrets remain server-side.

### Frontend

No frontend changes.

### Verification

- `[passed] uv run --with-requirements requirements.txt pytest -q - 33 passed`
- `[passed] uv run --with-requirements requirements.txt mypy src tests migrations - no issues in 50 source files`
- `[passed] focused ruff check - all changed migration and test files pass`
- `[passed] uv run --env-file .env --with-requirements requirements.txt python -m migrations.run - deleted 13 orphaned objects and applied migration`
- `[passed] migration post-check - works tables and public storage bucket verified`
- `[passed] git diff --check`

### Deployment

- Deploy `inkfig-main-system` so future environments run Python storage migrations.
- Migration `20261007_010_delete_orphaned_work_storage.py` must run with database and Supabase service credentials; it has already been applied to the configured Supabase project.
- No new environment variables are required.

### Git

- Branch: `main`
- Commit: `d61bf30`
- Push: `successful`

### Notes

Future destructive artwork-reset migrations can use the tracked storage-migration mechanism. External file deletion is irreversible, so each cleanup must explicitly document scope and rollback limitations.

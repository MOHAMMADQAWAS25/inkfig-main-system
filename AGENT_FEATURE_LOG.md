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

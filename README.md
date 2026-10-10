# InkFig Main System

InkFig is a graduation project for Hebron University. It is a web platform where students can create accounts, publish their artwork, discover work created by other students, and interact with it.

This repository contains the main backend service for InkFig's business features and workflows.

See [the infinite image feed guide](docs/infinite-feed.md) for cursor pagination,
media preparation, migration/backfill, and deployment order.

## Product vision

InkFig is an art-focused community platform with some similarities to Pinterest, while remaining tailored to the university context. Each student has an account and a personal body of work. Students can upload and display different kinds of art, including digital artwork made with tools such as Photoshop, hand-created artwork, and other art forms.

The platform will support multiple ways of presenting and discovering artwork. The exact presentation modes will be designed later. Students will be able to view one another's work and interact with it through likes.

## Planned capabilities

- Student account creation, authentication, and profiles.
- Artwork uploads across multiple art types and media.
- Personal student portfolios and shared artwork discovery.
- Likes and other appropriate community interactions.
- Preference and recommendation algorithms for personalized discovery.
- Natural-language image search: a user enters a text description and a model returns artwork that matches it.
- Teacher-created events in which students can participate by submitting artwork.
- Event submission moderation: a submitted work remains pending until the teacher accepts or rejects it.
- Rejection feedback: when a teacher rejects an event submission, the teacher provides a reason.
- Multiple roles and granular permissions.
- Account administration, including activating and deactivating accounts.

## Event workflow

1. A teacher creates an event.
2. A student submits artwork to the event.
3. The submission remains pending and is not included in the event yet.
4. The teacher reviews the submission.
5. If accepted, the artwork becomes part of the event.
6. If rejected, the student receives the teacher's rejection reason.

## Project status

This document records the initial product direction, not a complete specification. Detailed requirements, artwork presentation modes, algorithms, roles, permissions, and additional workflows will be defined as the project develops.

## Development

This backend uses Python 3.12, FastAPI, PostgreSQL, and the practical clean architecture documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

```powershell
py -m pip install -r requirements.txt
uvicorn src.main:app --reload
```

The health endpoint is available at `/health` and `/api/v1/health`.

### Artwork foundation

Published artwork is publicly readable. Creating upload URLs, publishing a work,
and adding or removing likes require an InkFig access token. Images are uploaded
directly from the browser to the public Supabase Storage `works` bucket through a
short-lived signed upload URL; the Supabase service key remains backend-only.

Run database migrations before deploying a backend version that depends on them:

```powershell
python -m migrations.run
```

The initial migration creates `work_types`, `works`, and `work_likes`, and prepares
the Storage bucket. It intentionally does not seed work types; the official list
will be added in a later migration.

## AWS Lambda deployment

AWS SAM packages the FastAPI application through Mangum using [`template.yaml`](template.yaml). Validate and deploy with:

```powershell
sam validate --lint
sam build
sam deploy --guided
```

During guided deployment, provide the trusted frontend origins as a JSON array, the backend-only Supabase values, and an ACM `CertificateArn` valid for `main-api.inkfig-hu.com`. The certificate must be in the deployment region (`eu-west-1` by default). Use the Supabase Session Pooler connection for `DatabaseUrl`. Do not store secrets in `samconfig.toml` or commit them to Git.

After deployment, copy the `CloudflareCnameTarget` stack output into a Cloudflare CNAME record named `main-api`. Keep the record DNS-only while validating the setup; Cloudflare proxying can be enabled afterward with SSL/TLS mode set to Full (strict).

### Automatic GitHub deployment

Every push to `main` runs tests and mypy, validates and builds the SAM application, deploys the `inkfig-main-system` stack, and checks the production health endpoint. The workflow uses GitHub OIDC for temporary AWS credentials.

Create a protected GitHub environment named `production` and configure these repository or environment secrets:

- `AWS_DEPLOY_ROLE_ARN`: ARN of an AWS IAM role trusted only by this repository's `main` branch through GitHub OIDC.
- `SUPABASE_URL`: production Supabase project URL.
- `SUPABASE_SECRET_KEY`: production backend secret key.
- `DATABASE_URL`: production SQLAlchemy asyncpg Session Pooler URL.
- `ACM_CERTIFICATE_ARN`: ACM certificate ARN for the API custom domain in `eu-west-1`.
- `JWT_SECRET`: the same signing secret used by `inkfig-user-system` so this service can validate access tokens.

The deployment role must be authorized to upload SAM artifacts, manage this CloudFormation stack, pass the generated Lambda execution role, and manage the Lambda and API Gateway resources declared by the template. Do not store AWS access keys or backend secrets in the repository.

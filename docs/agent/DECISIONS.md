# Main-system decisions
Updated: 2026-11-15. Current source wins over old feature-log implementation notes.

- Purpose: university art community, not a delivery/accounting application.
- Python 3.12 FastAPI + async SQLAlchemy/asyncpg; domain/service/HTTP/infrastructure
  boundaries in [ARCHITECTURE](../ARCHITECTURE.md). Preserve SnapStart-safe request-time initialization.
- Supabase supplies PostgreSQL/storage, not authentication. User service owns JWT issuance.
  Main validates the shared HS256 issuer/key contract; exhibition/rating repositories add live eligibility.
- New work images: width >=200 AND height >=300 after EXIF; 200x300 accepted,
  300x200 rejected. Owner approved 2026-10-20; [rule](../../src/entities/work_image_rules.py).
  Existing artworks, banner/avatar limits and legacy backfills are separate.
- Original media retained; responsive WebP feed variants do not change original source dimensions.
- Text search: Voyage generates query embedding, PostgreSQL pgvector compares stored
  compatible vectors. [service](../../src/app/services/work_service.py).
- Related works: stored image-to-image cosine >=0.20, descending exact similarity,
  creation/ID tie-breakers; no Voyage call at open and no same-category fallback.
  2026-10-20 follow-up supersedes earlier category/score-band fallback.
- Tag generation, multi-interest personal preferences and collaborative filtering remain
  design proposals, not production features or approved weights.
- Supervisors/admin/system-admin manage ALL exhibitions, per owner clarification.
  Supervisor is not allowed exhibition deletion; administrator/system-administrator only.
- Submission ownership, open participation window, blocks, max ten active entries,
  approval/rejection reason and reviewed approved withdrawal are server rules.
  [Exhibitions](../exhibitions.md) is the detailed current contract.
- New event_ends_at supports Current/Upcoming/Past; default legacy duration 24h.
- Ratings: per exhibition/work/user integer1..5; live eligibility; no own/organizer vote.
  Public totals exclude ineligible voters; not frozen when exhibition ends.
  [Ratings](../exhibition-artwork-ratings.md), [leaderboard](../exhibition-leaderboard.md).
- Leaderboard excludes zero-count works, ranks unrounded average then vote count,
  competition ties, stable presentation tie-breakers; category filter precedes ranking/page.
- Original work deletion includes storage/variants and dependent data; exhibition deletion
  deletes membership/banner, NOT original works. Storage/SQL are not distributed transactions.
- 2026-11-15 owner workflow: independent checkouts, approved direct-main, bounded memory,
  issue/task claims, explicit manual operational approval. Supersedes full-log rereads,
  not append-only preservation. [Workflow](../collaboration/WORKFLOW.md).

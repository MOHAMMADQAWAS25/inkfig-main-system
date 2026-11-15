# Project state - inkfig-main-system
Updated: 2026-11-15. Evidence: synchronized source at 579effe plus this docs-only setup.
Start with [instructions](../../AGENTS.md) and [active handoff](../collaboration/tasks/INKFIG-COLLAB-001.md).

## Current objective and approved scope
Establish useful bounded project memory and three-person collaboration.
Owner's attached 2026-11-15 workflow authorizes documentation/instruction changes,
preserving application behavior and existing work. No runtime/config/data changes.
Status: setup complete; no next application-implementation task has been claimed.
Task: INKFIG-COLLAB-001; human: project owner; agent: owner-primary-2026-11-15 (/root).
Default integration decision-maker: owner, until explicitly delegated.
No partner workstreams or checkout/session assignments have been approved.

## Implemented in current source (not a live certification)
- Works/types, signed image uploads/publication, original + responsive variants, links,
  chronological cursor feed, likes/saves, own collections, moderator deletion.
- Voyage text/image embeddings and pgvector search; stored-vector related images.
- Exhibitions: schedule/participation, submission review, blocks, withdrawals,
  banner lifecycle, live decision invalidations, ratings and category-filtered leaderboards.
- Recent changes: 496524a ratings, 3162130 exhibition names, 765ffef leaderboards,
  579effe leaderboard category filtering. See feature docs rather than old chat snapshots.

## Git and preserved work
- Baseline branch main, origin/main synchronized at 579effe.
- Local samconfig.toml modification preserved, not read/copied/staged. No branch switch.
- Git authors evidence: MOHAMMADQAWAS25/mohammadqawas25, a7mad.ishaq, anasmazen;
  contributions do not establish exclusive ownership.
- Public GitHub issue queries returned no open issues on 2026-11-15.
  Other checkouts, private conversations and unpublished changes are not visible.
- Setup task issue URL unavailable: no authenticated issue-writing tool/gh here.
  Repository handoffs are publishable coordination, not locks.

## Verification / deployment distinction
- This setup passed documentation links, memory size bounds, selected secret/path
  patterns, staged Markdown-only review and whitespace checks; see handoff.
- Application suites NOT rerun for docs-only changes. Last recorded results:
  178 pytest passed + two opt-in PostgreSQL skips; mypy 92 files, per 2026-11-01 log. Historical reports are not a new verification claim.
- Configured workflow: [.github/workflows/deploy.yml](../../.github/workflows/deploy.yml).
- No manual migrations, deployment, production writes or live browser tests authorized/run.
- [skip ci] on setup commits avoids existing automatic production workflows.
- Setup commit 09faaaee5b330e34d7f74bc5fa134a8b0c02d197 pushed successfully to origin/main.
  Final checkpoint/log commit follows it in Git history; no production deployment claimed.

## Applicable verification commands (not run for this docs-only setup)
python -m pytest; python -m mypy src tests. For SAM changes: sam validate --lint; sam build.
Do not run manual migrations/deployments or production fixtures without explicit approval.

## Partial / pending / known limits
- Home preference learning and automatic tags are not implemented by the current related-image endpoint.
- Related matching is exact vector scoring; monitor real query plans before promising ANN performance.
- Live offset-based related/leaderboard pages can shift under concurrent updates; client dedup is not snapshot isolation.
- Existing ratings totals can change with moderation/account activity; not immutable winner results.
- Deployment versions, pending production migrations and live health are unverified.
- No authenticated Search Console access/browser bridge established in this session.
- Personalization/tags remain proposals, not approval to implement a trained recommender.
- Expired/used email-code cleanup was deferred by owner until later; user service owns it.
- Physical-device and real PostgreSQL concurrency/plan certification are not implied by tests.

## Exact next actions
1. Setup is documented/published; preserve existing local files, do not repeat it.
2. Owner/partners each establish independent clones and publish one bounded task claim.
3. Confirm human -> checkout/session mappings and integration owner for shared changes.
4. On next implementation, inspect current source and relevant memory; update its handoff.
5. Request explicit approval for manual migration/deploy/production mutation if needed.

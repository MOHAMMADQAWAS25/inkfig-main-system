# Main domain model
Updated: 2026-11-15. SQL migrations/DTOs/repositories remain authoritative.
See [migrations](../../migrations), [DTOs](../../src/entities/dto).

## Core relationships
- work_types: system catalog/category; one type per work. Current UI categories include
  Digital Art, Hand Art, Video, Audio, Animation, Games, Interactive, VR/AR, Other.
  Category existence is not proof its media publishing format is supported.
- works: UUID, owner -> user_accounts, type, title/description, storage path,
  MIME/status/time, media dimensions/variants and external links.
- work_links: multiple optional HTTP(S) links; existing validation/bounds retained.
- work_likes / work_saves: per-user/work state, active-user totals; save != notification.
- work_embeddings: stored model-compatible vectors; pgvector cosine similarity,
  not a replacement for original files or literal subject tags.
- work_deletion_audits: moderator actor/reason/target audit; preserve required reason.
- exhibitions: organizer, name/description, event start/end, participation window/banner.
- exhibition_submissions: exhibition/work/submitter, pending/approved/rejected decision
  and reason, optional approved-withdrawal request metadata.
- exhibition blocks: event/user restriction distinct from global account suspension.
- withdrawal audit: preserves manager decision context even when membership is removed.
- exhibition ratings: one score1..5 per event/work/voter; FK to submission and account.
- User tables, roles, report records and WebSocket connections are user-system-owned,
  not duplicate ORM entities to reinvent here. Services share the same database.

## Invariants
- Published works require owned uploaded image; decoded minimum width200/height300
  applies to new work publication, not old works/banners/avatars/backfills.
- Public work results require publication/active owner under their query scope.
- Same work cannot duplicate event membership; one upload operation creates one work;
  max ten active entries/user/exhibition; multiple owned works may be assigned.
- Only open/unblocked/eligible submissions; approved public gallery starts at event time.
- Managers review with reason for rejection; all supervisors may manage all events.
- Pending withdrawal removes membership; approved withdrawal requires reason/manager
  decision and does not delete original work. Blocks hide event entries.
- Rating requires live active/verified/permitted voter, current event, eligible membership;
  owner/organizer cannot vote. Edits/removals only while eligible.
- Counted public averages exclude ineligible voters, stay event-specific, and can change
  after closing because moderation/account state remains relevant.
- Leaderboard excludes zero counted votes; ties share competition rank; selected
  category filters complete eligible set before rank/count/pagination.
- Delete work: storage + dependent rows/vectors under existing workflow.
  Delete event: banner/membership/ratings, preserve artists' original work.
- DB transactions do not make external storage deletion transactional; retain retry/error semantics.
- API approval/withdrawal/reporter restriction/global ban are different concepts.

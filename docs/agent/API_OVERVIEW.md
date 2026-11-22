# Main API overview
Configured base: https://main-api.inkfig-hu.com/api/v1 (live availability not asserted).
Authoritative [routes](../../src/interface/api/routes), [DTOs](../../src/entities/dto),
[repositories](../../src/infrastructure/repositories). Consult them for full schemas.

## Authentication
User-system JWT issuer/key contract. Cookie inkfig_access; main also supports Bearer.
[Dependency](../../src/interface/dependencies/authentication.py) validates signature/
issuer/type/permissions; exhibition/rating paths additionally verify live DB eligibility.
Public read does not authorize any write. No browser Supabase service credentials.

## Artwork and discovery
- GET /feed: chronological cursor cards; optional type_code/owner_user_id.
- GET /works/types: published system art-type catalog.
- GET /works, /works/users/{id}: public work collections; GET /works/{id}: single work.
- GET /works/me, /works/likes, /works/saves: authorized own collections.
- GET /works/search: text query -> Voyage embedding -> pgvector similarity;
  rank/score and bounded pagination; owner/type filters.
- GET /works/{id}/related: stored-vector image similarity >=0.20 descending;
  snapshot/offset continuation; no provider call; no same-type fallback.
- POST /works/uploads: works.upload, draft metadata -> signed object upload.
- POST /works/{id}/publish: owned uploaded file inspected, dimensions >=200x300,
  media/publication;422 too small. Original storage and derived variants are distinct.
- PATCH /works/{id}, DELETE /works/{id}: owned edit/delete with backend guards.
- PUT/DELETE /works/{id}/like or /save: authorized idempotent state; saves do not notify.
- DELETE /works/{id}/moderation: works.delete_any, required reason; audited deletion.
- Public cards use lightweight has_exhibition/exhibition_rating; details hold full metadata.

## Exhibitions / ratings
[Full exhibition contract](../exhibitions.md), [ratings](../exhibition-artwork-ratings.md),
[leaderboard](../exhibition-leaderboard.md).
- GET/POST /exhibitions, GET/PUT/DELETE /exhibitions/{id}.
- GET /exhibitions/eligible: current participation, ownership, window/block/quota filters.
- GET /exhibitions/pending-counts: authorized management summary.
- POST/GET /exhibitions/{id}/submissions: owned submit or public/mine/manage page.
- PATCH /exhibitions/{id}/submissions/{submissionId}: review, reject requires reason.
- POST/PATCH .../submissions/{submissionId}/withdrawal: owner request/manager decision.
- PUT/DELETE/GET /exhibitions/{id}/blocks...: management participation restrictions.
- POST .../{id}/banner-uploads and /banner-uploads/complete: scoped storage lifecycle.
- GET /exhibitions/{id}/works/{workId}/rating: public-visible artwork only, session-scoped
  RatingState/eligibility; private no-store response, no mutation.
- PUT/DELETE /exhibitions/{id}/works/{workId}/rating: strict score1..5, actor from
  session, live eligibility, private my_rating; not a request-supplied user ID.
- GET /exhibitions/{id}/leaderboard: public counted-vote rank; type_id filter before page.

## Errors / integration
Keep401/403, scoped404, conflict409, validation422 and storage/provider503 distinct.
Do not replace backend errors with invented client schemas. JWT/WebSocket/notification
contracts are shared with user-system; REST remains canonical after invalidations.
- Root /health and prefixed /health are infrastructure checks, not DB-feature certification.

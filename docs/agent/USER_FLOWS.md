# Main-system end-to-end flows
Updated: 2026-11-15. [API](API_OVERVIEW.md), [exhibitions](../exhibitions.md).

## Browse and search
1. Anonymous or signed-in visitor requests chronological public feed/type/owner page.
2. Backend returns lightweight cards and bounded continuation; frontend paginates/deduplicates.
3. Text query -> Voyage query embedding -> stored-vector pgvector ranking -> ranked page.
4. Open work -> full detail + compatible stored-image similarity >=0.20; no new Voyage request.
5. Empty/missing vectors produce no related matches, not arbitrary category fallback.
   Provider/search failure keeps explicit retry/error; do not silently change ranking.

## Upload and publish
1. Signed-in permitted user selects type/title/image/optional description/links.
2. Frontend decodes/validates dimensions before draft creation.
3. Backend owns draft path/signed upload; browser writes file to scoped Supabase URL.
4. Publish verifies ownership/object, EXIF-aware dimensions/minimum, stores media and publishes.
5. Voyage image embedding may fail without undoing publication; existing backfill can retry.
6.422 small/invalid, missing object404 or storage503 keeps error/retry semantics.
   Backend-bypassing small originals may remain staged drafts; no new deletion policy invented.

## Artwork interactions and deletion
- Permitted like/unlike and save/unsave are distinct; only supported notification actions notify.
- Owner can edit metadata, not replace the work's original through that endpoint.
- Owned deletion respects approved exhibition memberships; manager deletion requires reason/audit.
- Storage cleanup and SQL may partially fail; preserve reported failure and recoverable retry.
  Do not report success merely after deleting one table/link.

## Exhibition lifecycle
1. Supervisor/admin/system-admin creates schedule/details/banner, manages all exhibitions.
2. User chooses eligible event from owned work or uploads a new work in event context.
3. Backend checks active user, open participation, not started/blocked, duplicate and quota.
4. Submission pending -> manager approves or rejects with reason; invalidations refresh UI.
5. Public exhibition work list remains gated until start; active owners/approved/unblocked only.
6. Pending withdrawal removes membership; approved requires reason + manager approval.
   Rejected request leaves approved membership; original work remains.
7. Managers may block/unblock event participants; only admin/system-admin deletes exhibition.

## Ratings and leaderboard
1. During active event, eligible signed-in visitor opens gallery rating controls.
2. Server authorizes actor, score/window/membership/no self or organizer vote; atomic upsert.
3. Change/remove while eligible; late/ineligible actions fail and recover by refetch.
4. Public leaderboard counts valid votes, filters category before rank/page and omits zero votes.
5. After end, results read-only for voting but moderation/account status can change totals.

## Cross-service recovery
User JWT/refresh/notification tickets belong to user-system. Main emits signals after
commits; socket delivery failure must not undo saved decisions. REST/open/reconnect recovers.

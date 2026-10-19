# Artwork detail page backend: implementation and rollback record

Ticket branch: `feature/artwork-detail-page` in both affected repositories.

- Main backend pre-ticket baseline: `b11e077f0e60abb25a6a044ce5f63df3de1fb58c`.
- Frontend pre-ticket baseline: `c925263f8ec2bdc74a911c52bff1e9dc62c22c08`.
- Main and frontend worktrees were clean, with main pulled before edits.

## Backend changes

Adds `GET /api/v1/works/{work_id}/related` through a dedicated DTO, repository protocol, SQL repository, service and dependency. Uses existing stored embeddings and tables; no provider calls or database migrations. Only published artworks from active owners qualify; current work excluded. Model-compatible visual matches above 0.20 rank first. Similarity bands of 0.02 prefer the same category among close matches, then exact score and stable creation/ID ordering. Same-category candidates fill remaining results, including when embeddings are absent. Responses contain existing lightweight card/interaction fields, private/no-store cache headers and bounded source-scoped snapshot/offset cursors. New uploads cannot jump ahead of an established snapshot; deletions, category edits or embedding backfills can still alter live ranked offsets. Client deduplicates results.

## Safe rollback

Exact ticket commit hashes are reported in the final handoff. Backend commit subject: `Add stored-vector related artwork feed`. Frontend subject: `Add routed artwork details and related masonry feed`.

If the user requests reversal, revert only this ticket's commits with new commits, preserving unrelated work. Restore/redeploy frontend first, then remove/redeploy the optional backend endpoint. No migration, data restoration, image deletion, bucket change or secret rotation is needed. Do not reset main to the baseline or force-push. Resolve any later overlapping changes deliberately, append rollback logs, rerun tests/types/builds, and follow the established Git workflow. Retain historical feature-log entries.

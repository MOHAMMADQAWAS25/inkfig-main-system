# INKFIG-LEADERBOARD-VOTE-001

Human/integration owner a7mad.ishaq; agent /root a7mad-leaderboard-vote-2026-11-22.
Branch feature/leaderboard-popup-rating in independent frontend/backend checkouts.
Objective: rate from leaderboard artwork popup using existing eligibility and mutations.
Acceptance: load viewer-specific rating safely; submit/change/remove votes; refresh
rankings; preserve closed/owner/organizer/blocked restrictions and page filters.
Scope: rating read endpoint/contracts/tests; popup/leaderboard/cache/tests; memory/log.
GET /exhibitions/{exhibition_id}/works/{work_id}/rating returns existing RatingState.
No migration required. Backend deploy first, then frontend. Integration owner above.
Issue URL unavailable (no authenticated issue writer). Public frontend issues empty.
No known active overlapping task; previous popup fit completed.
Status: backend read implemented with shared eligibility SQL and public artwork visibility.
Added tests for actor isolation/private caching, hidden scope and no writes.
Local pytest/mypy unavailable: python absent; existing venv points to missing Python312.
Source15f56a3651ea970654640f2b2a1ba8b27e7600b0 pushed to main, no conflicts.
Workflow45029353802 succeeded: pytest/mypy/SAM validate/build, automatic migration
runner/deployment/health/media backfill. No new migration or manual operation.
Live read-only anonymous smoke test on requested exhibition returned HTTP200,
private no-store, can_rate=false and signed_out; no vote/data write performed.
Frontend87e3f8f published only after backend success; frontend deployment pending.
Next: frontend pipeline/owner interaction review. Authenticated live voting not tested.
Standing verified main publication authorized; no manual deployment/data writes.

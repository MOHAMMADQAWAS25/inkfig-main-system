# InkFig collaboration workflow
Current policy, 2026-11-15. Applies to the owner and two partners, each with an agent.
See [repository map](RELATED_REPOS.md), root AGENTS.md and docs/agent/PROJECT_STATE.md.

## Three independent work areas

1. Each human uses their own clone of every repository they need; each agent/session
   operates only in its assigned checkout. Never switch branches, stage, stash,
   reset or clean someone else's checkout. Never share one directory concurrently.
2. No permanent partner module assignment has been approved. Record bounded claims,
   not assumed ownership. A claim is coordination information, never a lock.
3. Project owner is the default integration decision-maker until explicitly delegated.
   For a cross-service task, name one integration owner and deployment order in its handoff.
4. Agents cannot see each other's private conversations. Publish checkpoints in Git
   and GitHub Issues; unpublished files or a private stash are not adequate handoffs.

## Startup and recovery

- Read root AGENTS.md, PROJECT_STATE.md, active task handoff and relevant memory.
- Inspect branch/status, staged/unstaged/untracked files, recent commits and open issues.
- Fetch origin, safely fast-forward main before starting. A dirty checkout is not
  permission to stash/discard someone else's files; stop if synchronization overlaps.
- Read active task claims and related repos before cross-service investigation.
- Review relevant feature-log entries for history. The old complete-log reread rule
  is superseded by the owner's bounded-memory workflow; the log itself stays append-only.
- If compaction is actually known, say:
  "COMPACTION DETECTED - last confirmed state: ...; next step: ..."
  Do not claim detection or perfect memory without evidence.

## Claim a bounded task

Prefer an existing GitHub Issue. Create/update one only with authenticated authorized
access. Record issue URL, task ID, responsible human, agent/session, objective,
acceptance criteria, intended files, contracts/dependencies, integration owner,
status, checkpoint, checks, approvals and exact next step.
Use docs/collaboration/tasks/<task-id>.md for each task; do not combine all work in one log.
If GitHub access is missing, use a stable temporary task ID, publish the handoff,
and explicitly record the missing issue link. Do not claim an issue was created.
Check issues/claims and upstream again before editing an overlapping area.
No task registry can rule out unpublished partner work; ask when overlap is consequential.

## Investigation and implementation

Trace actual routes -> permission checks -> services -> repositories -> DTO/schema.
Source and executable contracts beat old prose or mock fixtures; flag contradictions.
Use bounded changes, existing components/helpers, and actual pages for requested previews.
Clearly label fixtures/prototypes and distinguish them from production integration.
Coordinate shared auth, schema, migrations, API shapes/cursors, WebSocket events,
routing, global tokens and configuration before parallel edits.
Do not add libraries, refactor unrelated code or weaken tests to hide failures.
Retain future Lambda SnapStart compatibility: no new import-time live clients,
connections, temporary credentials or invocation-specific clock/random state.

## Owner-approved Git policy

Routine authorized and verified changes may commit/push directly to main.
Do not introduce mandatory PR/review gates; respect server protection if encountered.
Fetch and integrate upstream before push. Rebase only local UNPUBLISHED commits.
Never rewrite published history, force-push, reset --hard, clean or routinely delete branches.
Preserve existing staged/unstaged/untracked files; stage only the task's explicit files.
Review the full diff, run applicable checks, commit accurately, fetch again,
integrate without overwriting intent, and rerun checks affected by upstream changes.
If publication awaits owner approval, leave work local and say so.
Never auto-resolve conflicts by taking an entire side; preserve both intended changes.

## Verification and operational authority

Keep separate: implemented; checks; committed; pushed; deployed; live verified.
Check commands and known gaps are in PROJECT_STATE.md; source-only/SQLite tests do
not certify PostgreSQL query plans, concurrency, physical devices or production.
Do not declare a failure pre-existing without an unchanged-baseline comparison.
For docs-only changes, check links, size bounds, diff/whitespace and preserved history;
application suites can be explicitly not run because runtime did not change.

Every main push normally runs .github/workflows/deploy.yml:
- User: tests, mypy, SAM validate/build, migrations, AWS deployment, health check.
- Main: same plus user JWT/WebSocket dependency lookup and media backfill.
- Frontend: tests, TypeScript/Vite/SEO build, Cloudflare publish and health check.
Explain these effects before a relevant push; do not add triggers without approval.
This documentation-only setup uses [skip ci] commits to avoid deploying/migrating
or backfilling production. Do not use skip markers to conceal failing application checks.
See https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs .
Manual deployment, release, DB migration, destructive operation and production-data
write require separate explicit owner authorization. Do not run a migration just
because a setup, pull, test or health check was requested.
If stopped/revoked, stop dependent work and verify any dispatched operation's actual state.

## Memory and handoff

Update the active handoff and current PROJECT_STATE after meaningful progress.
Maintain DECISIONS, SCREENS, API_OVERVIEW, DOMAIN_MODEL and USER_FLOWS when facts change;
target <=150 lines each, not repeated question/command transcripts.
Append AGENT_FEATURE_LOG.md only for actual changes, using its required ticket sections.
Never rewrite/delete old feature-log entries. Current memory supersedes stale history.
Archive verbose detail under docs/agent/history/YYYY-MM-DD-<topic>.md only when useful;
retain accessible references to every unresolved requirement, approval and blocker.
Before interruption/known compaction, checkpoint scope/acceptance, latest approvals,
files/branch/commit, verified contracts, checks/gaps, blockers and the exact next step.
Do not store credentials, tokens, private account records, secrets or screenshots of them.

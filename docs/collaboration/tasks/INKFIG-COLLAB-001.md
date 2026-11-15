# INKFIG-COLLAB-001 - Establish shared project memory
Updated: 2026-11-15. Status: implementation documented; validation/publication pending.
Responsible human: project owner (user of this session).
Agent/session: /root, existing InkFig session; no private cross-agent awareness.
Integration owner: project owner until explicitly delegated.
Issue: not created; no authenticated issue-writing tool/gh in this environment.
Public issue-list queries returned no open issues on 2026-11-15.

## Objective / acceptance
- Useful current AGENTS + WORKFLOW + RELATED_REPOS in each of three repos.
- Six concise source-backed memory files in each; no runtime behavior changes.
- Document direct-main policy, independent checkouts, claims/shared-contract coordination,
  verification, operational approval and context-recovery procedures.
- Correct discovered stale auth/migration/palette/service ownership prose, retain useful docs.
- Preserve all pre-existing local files and historical feature-log bytes.
- Workspace index links tracked repo copies; no sole unpublished handoff.
- Record deployment vs push vs live verification separately.

## Scope and intended files
This repo: main-backend instructions/memory, migration/architecture docs.
Files: AGENTS.md; docs/collaboration/{WORKFLOW,RELATED_REPOS}.md; this task;
docs/agent/{PROJECT_STATE,DECISIONS,SCREENS,API_OVERVIEW,DOMAIN_MODEL,USER_FLOWS}.md;
README.md, docs/ARCHITECTURE.md, migration README where stale; AGENT_FEATURE_LOG.md append.
Workspace convenience AGENTS/map are not a fourth repo; tracked bootstrap is frontend map.

## Dependencies / overlap
Shared auth/cookies/JWT, DB/migrations, RBAC, API/cursors, WebSocket events, global
routing/CSS and deployment configuration require coordination, NOT modification here.
Recent partner work on exhibition ratings/leaderboard, responsive detail discovery,
mobile navigation and report pagination was pulled and is preserved.
Other humans' local/unpushed tasks cannot be inspected; no claim of an exclusive lock.
Do not stage backend samconfig.toml edits or user-system untracked aws.

## Current checkpoint
- Read current source/routes/DTOs/workflows and relevant docs/logs; all repos main ff-pulled.
- Baselines: main579effe, user396a54c, frontend5dd4ec9.
- Supabase Auth/runner/old orange theme documentation drift identified.
- Source implemented ratings/leaderboards and integrated discovery, not just initial vision.
- Browser/Search Console diagnosis and preference/tag algorithms not certified complete.
- No runtime/tests/CI/migrations/env changes; no production writes.

## Checks and limits
Pending docs link/line-bound/secret-pattern/Git diff and historical-prefix checks.
Runtime suites/builds intentionally not run: Markdown-only setup.
No authenticated issue creation, manual deployment, migration, live Google access or
physical-device verification claimed. Final validation/commit/push evidence belongs below.

## Approvals / publication
Owner requested this setup and previously approved routine direct-main pushes.
New manual production/migration/destructive/release actions require separate explicit approval.
Existing main push workflows deploy and backend workflows migrate/main backfill.
Use docs-only [skip ci] commits for this setup; do not bypass application failures.
No new workflow triggers or PR gates. Preserve protected-branch errors if encountered.

## Exact next step
Validate Markdown links/bounds/diff, append required feature-log entries, stage only
documentation, commit, fetch/integrate only unpublished history and push without force.
Then record actual hashes/status in handoff or final report and request only the
missing partner-to-checkout/task ownership mapping before shared implementation.

## Integration pointer
[Related repositories and handoffs](../RELATED_REPOS.md).
This repo owns its own facts; frontend handoff is the task's tracked bootstrap pointer.

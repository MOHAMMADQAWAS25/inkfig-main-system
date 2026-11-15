# Related InkFig repositories
Updated: 2026-11-15. This is an index, not a duplicate service specification.

| Repository | Responsibility and authoritative contracts | Dependencies |
| --- | --- | --- |
| [inkfig-user-system](../../../inkfig-user-system/README.md) | Identity, sessions, profiles/follows, settings, roles, reports, notification tickets/connections. Routes and DTOs in src/interface/api and src/entities/dto. | Supabase PostgreSQL/storage, Brevo, API Gateway WebSocket |
| [inkfig-main-system](../../../inkfig-main-system/README.md) | Works/feed/search/related images, exhibitions/submissions/ratings/leaderboards. Routes in src/interface/api/routes; DTOs in src/entities/dto; SQL in src/infrastructure/repositories. | User identity/permissions/shared JWT contract, shared PostgreSQL, Supabase storage, Voyage, user WebSocket API |
| [inkfig-user-FE](../../../inkfig-user-FE/README.md) | React UI, routes, localization, responsive layouts. AppRouter.tsx and feature API clients consume the two backend contracts. | User API and main API; Cloudflare Worker static assets |

## Recovery indexes

- [User instructions](../../../inkfig-user-system/AGENTS.md), [state](../../../inkfig-user-system/docs/agent/PROJECT_STATE.md).
- [Main instructions](../../../inkfig-main-system/AGENTS.md), [state](../../../inkfig-main-system/docs/agent/PROJECT_STATE.md).
- [Frontend instructions](../../../inkfig-user-FE/AGENTS.md), [state](../../../inkfig-user-FE/docs/agent/PROJECT_STATE.md).
- Each repo owns its six docs/agent files, workflow and task records. Read only relevant detail.
- The workspace copy of this map links these records; it is not the source of service detail.
- Sibling links assume independent clones next to each other; use the URLs below if absent.
- The frontend copy of this map is the tracked bootstrap index for a fresh workspace.

## Origins / configured public hosts

- https://github.com/MOHAMMADQAWAS25/inkfig-user-system
- https://github.com/MOHAMMADQAWAS25/inkfig-main-system
- https://github.com/MOHAMMADQAWAS25/inkfig-user-FE
- Frontend: https://inkfig-hu.com ; user API: https://user-api.inkfig-hu.com/api/v1
- Main API: https://main-api.inkfig-hu.com/api/v1
- Hosts are code/documentation configuration, not proof of deployment health.

## Shared boundaries to coordinate

- User owns identity issuance, account tables and notification transport; main validates
  shared JWTs and owns artwork/exhibition tables. Both access one Supabase database.
- User migrations must precede main features that require user tables/notifications.
  Additive API/migration deployment normally precedes its consumer frontend.
- Shared schema_migrations tracks filenames: use globally distinct timestamped names.
- API version is /api/v1. Do not invent endpoints from a frontend mock.
- Coordinate cookie/JWT fields, permissions, response/cursor shapes, rating eligibility,
  WebSocket event types, routing, design tokens and deployment parameters before overlap.

## Ownership and claims

- Project owner: the user of this session; integration decisions remain theirs unless delegated.
- Observed Git authors include MOHAMMADQAWAS25/mohammadqawas25, a7mad.ishaq and anasmazen.
  These are evidence of contributions, not permanent module ownership or exclusive locks.
- No open issues were returned by the three public GitHub issue queries on 2026-11-15.
  This does not inspect private chats, other checkouts or unpushed work.
- Current setup claim: INKFIG-COLLAB-001, owner plus this agent session (/root).
- [Integration handoff](../../../inkfig-user-FE/docs/collaboration/tasks/INKFIG-COLLAB-001.md).
- Partner-to-checkout/session mapping and permanent workstreams remain unassigned.

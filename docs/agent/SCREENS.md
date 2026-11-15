# Screens supported by the main backend
No UI is rendered by this repository. Implementation is in
[frontend router](../../../inkfig-user-FE/src/app/AppRouter.tsx) and
[frontend screen inventory](../../../inkfig-user-FE/docs/agent/SCREENS.md).

- Home/profile collections: feed, semantic search, work types, likes/saves and public cards.
- Opened artwork: work detail, related images, exhibition flags/rating summary.
- Upload: signed upload -> storage -> inspected publication; error422 for small images.
- Exhibition listing/detail: Current/Upcoming/Past, banners, timing/eligibility.
- My submissions: paginated pending/approved/rejected; withdrawal/request states.
- Review: manager decisions/reasons/blocks and deletion-request review.
- Exhibition popup: public details plus permission/window-scoped rating state.
- Leaderboard: counted-vote ranking, category filtering, pages and no-vote empty state.
- Error/empty/loading/localization/responsive rendering belongs to frontend, not API mocks.
- Reports/admin-user UI depends on user-system, not a main-system reports endpoint.

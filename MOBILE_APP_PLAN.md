# Mobile App Replacement Plan

## Objective

Replace the Django server-rendered front end with a mobile-first application that consumes the existing REST API as the source of truth. The backend already contains the business logic for auth, meals, deposits, expenses, complaints, bills, settings, and manager workflows. The mobile app should be a thin client that presents those functions in a better mobile experience without duplicating server-side rules.

## Recommended architecture

### Stack choice

- Client: React Native + Expo
- Language: TypeScript
- Navigation: React Navigation
- State/data: Zustand (auth/UI state) + React Query (server state)
- Forms: React Hook Form + Zod
- Token storage: expo-secure-store
- Media uploads: Expo Image Picker + multipart upload handling
- UI: React Native Paper
- Testing: Jest + React Native Testing Library + Detox for device smoke tests
- Date handling: dayjs (backend TIME_ZONE = Asia/Dhaka, all date logic must align to this)
- Image compression: expo-image-manipulator (compress receipt image before multipart upload)
- Env config: app.config.ts + EAS build profiles (dev/prod API base URL switch)

### Why this is the right fit

- The Django app already exposes a mature API contract under `/api/*`.
- JWT auth is already in place and is compatible with a mobile client.
- The existing backend handles validation, role rules, bill generation, and account approvals.
- The replacement is a front-end migration, not a domain rewrite.
- React Native is the shortest route to a modern Android UX while keeping the business logic centralized on the server.

## Scope and non-goals

### In scope

- Authentication and onboarding
- Meal logging for active members
- Manager meal summaries and dashboard views
- Deposit claims and approval workflow
- Expense entry with receipt uploads
- Personal bill details and manager billing operations
- Complaint creation and tracking
- Manager assignment and member approval flows
- Settings and permission-aware navigation


### Out of scope

- Rebuilding Django models or business logic in the mobile client
- Creating a second version of server-side validation rules
- Replacing the existing API with a separate backend service during the initial migration
- Supporting all future features before the mobile MVP is validated
- API versioning (staying on current /api/* — not adding /api/v1/)
- iOS build/test (Android-only for this project)
- Client/server-side pagination handling (backend returns full list, no DRF pagination — rely on month-based filtering already in place; add FlatList windowing only if a month's data list grows large)

## Current API mapping

The mobile app should map directly to the existing Django endpoints, using the current user roles and permission checks as the authoritative rules.

### Auth and user identity

- `POST /api/auth/register/` -> registration screen
- `POST /api/auth/login/` -> login screen; store `access` and `refresh` tokens
- `GET /api/users/me/` -> app bootstrap / authenticated user profile
- `GET /api/users/pending-approval/` -> super-manager approval queue
- `POST /api/users/<id>/approve/` -> member approval action

### Meal domain

- `GET /api/meals/my-meals/?month=YYYY-MM` -> member meal calendar screen
- `POST /api/meals/toggle/` -> toggle breakfast/lunch/dinner for a specific date
- `GET /api/meals/summary/?month=YYYY-MM` -> manager monthly member summary
- `GET /api/meals/daily-summary/?month=YYYY-MM` -> manager daily meal totals
- `GET /api/meals/fixed/` -> fixed meal configuration if exposed in mobile UI

### Deposit domain

- `POST /api/deposits/claim/` -> claim deposit entry form
- `GET /api/deposits/my-deposits/?month=YYYY-MM` -> member deposit history
- `GET /api/deposits/pending/` -> manager review queue
- `POST /api/deposits/<id>/approve/` -> manager approval action
- `POST /api/deposits/<id>/reject/` -> manager rejection action

### Expense domain

- `GET /api/expenses/bazar/?month=YYYY-MM` -> expense dashboard
- `POST /api/expenses/bazar/` -> add bazar expense with receipt upload

### Bill domain

- `GET /api/bills/my-bill/?month=YYYY-MM` -> member bill details
- `POST /api/bills/set-house-rent/` -> super-manager configuration
- `POST /api/bills/set-electricity/` -> super-manager configuration
- `POST /api/bills/generate/` -> manager bill generation

### Complaints and settings

- `POST /api/complaints/` -> create complaint
- `GET /api/complaints/my-complaints/` -> member complaint history
- `GET /api/complaints/all/` -> manager complaint queue
- `PATCH /api/complaints/<id>/status/` -> update complaint status
- `GET /api/settings/` -> app settings
- `PATCH /api/settings/` -> manager settings updates
- `GET /api/manager/assign/` -> active manager and assignment history
- `POST /api/manager/assign/` -> assign manager for a month

## Mobile app screen map

### Member screens

1. Splash / auth gate
2. Login screen
3. Registration screen
4. Home dashboard
   - current month status
   - quick actions for meals, deposits, bills, complaints
   - user name and role summary
5. Meal tracking screen
   - month selector
   - daily meal grid
   - toggle breakfast/lunch/dinner
6. Deposit history and claim screen
   - list by month
   - add new deposit claim
7. Bill overview screen
   - bill summary
   - generated cycle metadata
   - current balance and due values
8. Complaint screen
   - create complaint
   - list existing complaints and statuses
9. Profile / settings screen

### Manager screens

1. Manager dashboard
   - active manager assignment status
   - pending approval count
   - monthly metrics summary
2. Meal summary screen
   - monthly member totals
   - daily summary breakdown
3. Deposit approval queue
   - pending deposit list
   - approve/reject actions
4. Expense dashboard
   - list of expenses by month
   - meal rate and totals
   - add new expense with receipt
5. Bill management screen
   - month selection
   - set house rent and electricity values
   - generate bills
6. User approval queue
   - list pending members
   - approve users
7. Complaint management screen
   - all complaints list
   - update status
8. Manager assignment screen
   - active manager history and reassignment actions

## Phase breakdown

### Phase 0: API and product contract validation

- Review all current API views and serializer payloads.
- Validate expected auth flow, date formats, query params, and status codes.
- Map each endpoint to a screen and user role.
- Lock the MVP scope and reject non-essential features.

Deliverables:
- endpoint inventory and role matrix
- app screen map
- data contract document for mobile development
- receipt upload constraints confirmed (max size, accepted formats: jpg/png/pdf)
- role-change / manager-assignment refresh strategy defined

### Role-permission matrix (locked)

| Action                          | General User | Monthly Manager | Super Manager |
|----------------------------------|:---:|:---:|:---:|
| Meal toggle (own)                | ✅ | ✅ | ✅ |
| Meal summary (monthly/daily)     | ❌ | ✅ | ✅ |
| Deposit claim (own)              | ✅ | ✅ | ✅ |
| Deposit approve/reject           | ❌ | ✅ | ✅ |
| Complaint create                 | ✅ | ✅ | ✅ |
| Complaint status update          | ❌ | ✅ | ✅ |
| Bazar expense add                | ❌ | ✅ | ✅ |
| Bill generate                    | ❌ | ✅ | ✅ |
| House rent / electricity set     | ❌ | ❌ | ✅ |
| User approval                    | ❌ | ❌ | ✅ |
| Manager assignment               | ❌ | ❌ | ✅ |

### Phase 1: Foundation and app shell

- Initialize Expo app and TypeScript project.
- Set up navigation, theme, and shared design system.
- Implement secure token storage and API client base layer.
- Add global loading, error banners, toasts, and empty states.
- Establish protected route guards and role-aware navigation.
- Implement token refresh interceptor: queue concurrent requests during refresh, single refresh call, force logout + redirect on refresh failure.
- Note: SIMPLE_JWT has no ROTATE_REFRESH_TOKENS — refresh token stays valid for its full 7-day lifetime; only store a new refresh token if backend explicitly returns one, otherwise reuse the stored one across access-token refreshes.
- Configure ALLOWED_HOSTS on Django dev server to accept LAN IP requests from physical Android device (no tunnel/ngrok needed)

Deliverables:
- working app environment
- auth gate and bootstrapping flow
- shared UI primitives

### Phase 2: Authentication and profile

- Implement login and registration flows.
- Pull `GET /api/users/me/` during app startup.
- Display pending approval state and session persistence.
- Support token refresh and logout handling.
- Re-fetch GET /api/users/me/ after manager-assignment events so role-based navigation stays correct mid-session.

Deliverables:
- sign-in and session stability
- authenticated profile state available across the app

### Phase 3: Meal management

- Build month selector and meal calendar layout.
- Implement fetch for `my-meals` and toggle action for meal entries.
- Add optimistic updates and mutation invalidation.
- Build manager summary screens for monthly and daily meal data.

Deliverables:
- active members can log meals
- managers can review meal totals accurately
- Smoke test (unit/manual) covering this phase's core flow before moving to next phase

### Phase 4: Deposits and complaints

- Implement deposit claim form with validation.
- Add member deposit history screen.
- Build manager pending deposit review with approve/reject actions.
- Implement complaint creation and list views.
- Add manager complaint status change flow.


Deliverables:
- complete deposit and complaint workflows
- Pull-to-refresh + unread/status badge indicator on deposit and complaint status changes (MVP substitute for push notifications).
- Smoke test (unit/manual) covering this phase's core flow before moving to next phase


### Phase 5: Expenses and bills

- Build expense list and add expense form with optional receipt image.
- Support multipart upload to `/api/expenses/bazar/`.
- Create personal bill details screen.
- Add manager actions for bill generation, house rent, and electricity values.

Deliverables:
- complete expense + bill domain coverage
- Smoke test (unit/manual) covering this phase's core flow before moving to next phase

### Phase 6: Manager operations and settings

- Add approval queue for user activation.
- Build manager assignment screen and reassignment logic.
- Add settings screen for manager configurations.
- Add permission guard patterns to block manager-only actions for non-managers.

Deliverables:
- complete admin/manager functionality available in mobile app
- Smoke test (unit/manual) covering this phase's core flow before moving to next phase

### Phase 7: Hardening and release readiness

- Network error and retry UX
- Token expiry handling and secure session cleanup
- Accessibility, keyboard handling, and responsive layout polish
- Device testing on Android
- Production environment configuration and deployment checklist
- Distribute via Expo Go / internal development build (EAS dev build or `expo run`) for personal/demo use — no store release for now.

Deliverables:
- stable MVP release candidate
- QA pass and release gate approval

## Development tasks

### Shared app tasks

- Create project scaffold and environment config
- Configure ESLint, Prettier, and TypeScript strictness
- Define color tokens, typography, and layout primitives
- Build shared `ApiClient`, auth store, route guards, and cache layer
- Write reusable form components for date selectors, number inputs, and modals

### API integration tasks

- Create typed API modules for auth, meals, deposits, complaints, expenses, bills, settings, and manager actions
- Implement React Query hooks and invalidation rules
- Define shared request/response interfaces for each API contract
- Add error normalization for `400`, `401`, `403`, `404`, and `429` (throttle) responses — login endpoint has a 10/minute rate limit, show retry-after messaging on 429
- Handle 403 from IsActiveMember permission class distinctly (pending-approval user state) vs role-based 403
- Add Zod schema validation on API *responses* too (not just forms) — catches contract drift early since this is an agentic build with limited manual review
- Support `FormData` for receipt uploads and other multipart operations

### UI tasks

- Home dashboard cards and summary widgets
- Tab navigation and role-based screens
- Calendar and list views for meal tracking
- Form flows for claims, complaints, and expense entry
- Manager review screens with approval buttons and status badges

### Quality tasks

- Unit tests for API mapping and form validation
- End-to-end smoke tests for login, meal logging, deposit claim, and approval flows
- Manual QA on representative Android devices
- Performance review for large lists and image uploads

## Dependency map

### Core dependencies

- Django API must remain online and stable during mobile rollout.
- Access tokens and refresh tokens must be preserved as-is.
- File upload support must be operational for expense receipts.
- Existing role permissions must be reflected in the app UX.

### External dependencies

- HTTPS API base URL for production builds
- Real-device testing for Android
- Admin sign-off on manager workflows and user approval states

## Risks and mitigation

### Risk: API contract drift

The mobile app depends on the API being stable. If the backend changes without updating the mobile client, the app will break.

Mitigation:
- keep the API as the source of truth
- add contract smoke tests for each major endpoint
- version the API client and validate schemas centrally

### Risk: JWT/session handling issues

Mobile sessions can fail when access tokens expire or refresh flows are not handled correctly.

Mitigation:
- store tokens in secure storage
- centralize refresh logic in the API client
- force logout and prompt user re-authentication on invalid sessions

### Risk: Receipt upload failure

Large receipt images or unsupported file types can cause failed uploads.

Mitigation:
- compress images before upload
- validate format and size client-side and server-side
- provide retry and progress feedback

### Risk: Manager-only actions exposed incorrectly

If non-manager users see admin actions, the app may allow unauthorized behavior even if the backend blocks it.

Mitigation:
- gate UI by role at every screen
- enforce backend permission checks in every protected action
- test manager-only flows in both role states

### Risk: stale data after mutation

Users may see outdated values after creating a meal, deposit, or complaint.

Mitigation:
- invalidate and refetch affected queries on success
- refresh dashboard widgets after write operations
- keep mutation UX optimistic but consistent with server response

## Verification strategy

### Functional verification

- User can register and sign in successfully.
- Meal toggles persist and are visible in monthly summaries.
- Deposit claim and approval flows work for both member and manager roles.
- Complaint creation and status updates behave correctly.
- Bill generation and summaries reflect backend data accurately.
- Expense upload works with receipt images.

### UX verification

- App navigation works smoothly on mobile screens.
- Loading, empty states, and error states are understandable.
- Forms validate input before submission.
- Buttons and actions are accessible and readable on small screens.

### Release verification

- Run smoke tests against the Django API in a development environment.
- Validate production API URL and token handling.
- Test approval and billing workflows on real devices.
- Verify no manager-only route is accessible to regular members through the client.

## Acceptance criteria for MVP

1. Members can log in, view their profile, and track meals.
2. Members can claim deposits and view their deposit history.
3. Members can view bills and complaint history.
4. Managers can review pending deposits and complaints.
5. Managers can view monthly summaries and generate bills.
6. Managers can add bazar expenses with optional receipts.
7. The app handles authentication errors, stale sessions, and network failures gracefully.

## Recommended roadmap

### MVP release

- Auth
- Meals
- Bills
- Deposits
- Complaints
- Manager review and summary screens

### Post-MVP enhancements

- Push notifications for approvals and status changes
- Offline-first synchronization
- Charts and richer dashboard analytics
- Language support for Bengali and English
- Advanced manager exports and reporting

## Final recommendation

The best replacement path is to keep the Django server as the system of record and build a React Native mobile application on top of the existing API. This minimizes risk, avoids duplicate business logic, and lets the team focus on a mobile-first UX while preserving the backend’s validated rules and permissions. The app should be built incrementally, starting with auth and meal flows, then deposits, bills, complaints, and manager operations.

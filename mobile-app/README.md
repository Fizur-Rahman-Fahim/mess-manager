# Mess Manager — Mobile App (React Native + Expo + TypeScript)

Android-only client for the Django Mess Management API. Navigation: React Navigation.

## Run (development)
1. Backend: `python manage.py runserver 0.0.0.0:8000` (dev settings already allow all hosts).
2. Copy `.env.example` to `.env` and set your PC's LAN IP, e.g.
   `EXPO_PUBLIC_API_BASE_URL=http://192.168.0.10:8000/api` (phone and PC on the same Wi-Fi).
3. `npm install` then `npx expo start` and open in Expo Go (Android).

## Structure
- `index.js` entry -> `src/App.tsx` (providers) -> `src/navigation/RootNavigator.tsx`
- Auth flow: Login <-> Register, Pending Approval, session bootstrap with retry on network failure
- Tabs: Home, Meals, Deposits, Bills, Settings. Stack: Complaints; Expenses and Operations (managers only)
- `src/api` typed modules + Zod response validation, token refresh queue; `src/hooks/queries.ts` React Query hooks

## Checks
`npm run typecheck` and `npx expo lint`

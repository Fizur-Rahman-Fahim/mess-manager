# Mess Manager (Mess Management System)

Single-mess web application for meal tracking, deposits, bazar expenses, and monthly bill management.

## Tech stack

- Python 3.12+, Django 5, Django REST Framework
- SQLite (local dev), PostgreSQL (Render production)
- Tailwind CSS, bilingual UI (Bengali + English)

## Local setup

```bash
# Clone and enter project directory
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy .env.example .env          # Windows (use cp on Unix)

npm install
npm run build:css

python manage.py migrate
python manage.py createsuperuser
# After createsuperuser, set is_super_manager=True in Django admin or shell

python manage.py runserver
```

Open http://127.0.0.1:8000/

## Create Super Manager

After `createsuperuser`, enable manager flags:

```bash
python manage.py shell -c "from accounts.models import User; u=User.objects.get(mobile_number='YOUR_MOBILE'); u.is_super_manager=True; u.is_active_member=True; u.save()"
```

## API endpoints

### Auth (Phase 1)

| Method | Endpoint | Access |
|--------|----------|--------|
| POST | `/api/auth/register/` | Public |
| POST | `/api/auth/login/` | Public |
| GET | `/api/users/me/` | Active member |
| GET | `/api/users/pending-approval/` | Super Manager |
| POST | `/api/users/<id>/approve/` | Super Manager |

### Meals (Phase 2)

| Method | Endpoint | Access |
|--------|----------|--------|
| GET | `/api/meals/my-meals/?month=2026-08` | Active member |
| POST | `/api/meals/toggle/` | Active member — body: `{date, breakfast, lunch, dinner}` |
| GET | `/api/meals/summary/?month=2026-08` | Monthly Manager+ |

Web UI: `/meals/` (my meals), `/meals/summary/` (manager summary).

Management command: `python manage.py create_default_meals --days 30`

### Deposits (Phase 3)

| Method | Endpoint | Access |
|--------|----------|--------|
| POST | `/api/deposits/claim/` | Active member — body: `{amount, date_claimed, note?}` |
| GET | `/api/deposits/my-deposits/?month=2026-08` | Active member |
| GET | `/api/deposits/pending/` | Monthly Manager+ |
| POST | `/api/deposits/<id>/approve/` | Monthly Manager+ |
| POST | `/api/deposits/<id>/reject/` | Monthly Manager+ |

Web UI: `/deposits/` (my deposits), `/deposits/claim/`, `/deposits/pending/` (manager queue).

### Expenses (Phase 4)

| Method | Endpoint | Access |
|--------|----------|--------|
| GET | `/api/expenses/bazar/?month=2026-08` | Monthly Manager+ — includes totals and meal rate |
| POST | `/api/expenses/bazar/` | Monthly Manager+ — multipart for receipt |

Web UI: `/expenses/bazar/` (list + meal rate), `/expenses/bazar/add/` (manager entry).

### Bills (Phase 5)

| Method | Endpoint | Access |
|--------|----------|--------|
| GET | `/api/bills/my-bill/?month=2026-08` | Active member |
| POST | `/api/bills/set-house-rent/` | Super Manager — `{month, total, paid?}` |
| POST | `/api/bills/set-electricity/` | Super Manager — `{month, total, paid?}` |
| POST | `/api/bills/generate/` | Monthly Manager+ — `{month}` |

`Total due = meal cost + seat bill + current bill share + house rent share + electricity share`. Shares split equally among active members. `Balance = approved deposits − total due`.

Web UI: `/bills/` (my bill), `/bills/summary/` (manager), `/bills/manage/` (super: rent, electricity, generate).

Login returns JWT `access` and `refresh` tokens plus user profile.

## Development

- Settings module: `config.settings.dev` (default in `manage.py`)
- Tailwind watch: `npm run watch:css`
- Database file: `db.sqlite3` (gitignored)

## Production (Render)

- Set `DJANGO_SETTINGS_MODULE=config.settings.prod`
- Render injects `DATABASE_URL` for PostgreSQL
- Set `SECRET_KEY`, `ALLOWED_HOSTS`
- Build: `pip install -r requirements.txt && npm ci && npm run build:css && python manage.py collectstatic --noinput && python manage.py migrate`

## Completed workflows

The application includes complaints, dashboard summaries, Super Manager settings, global Monthly Manager reassignment, and global monthly fixed meal minimums. Fixed meals use `max(global_fixed_meal_count, member_actual_meal_count)` during bill generation. Reassigning a manager closes the previous active assignment while preserving its history.

PWA metadata, an application-shell service worker, upload validation, and production secret checks are also included.

## Project phases

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the full specification. Phases 1–8 core implementation is complete; production hosting provisioning, browser-level QA, and V2 features remain operational follow-up work.

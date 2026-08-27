# New Oniru Primary Health Centre

Full-stack starter for a primary health centre in Oniru, Victoria Island, Lagos.

## Stack

- Frontend: React 19 + Vite
- Backend: Django 4.2 + Django REST Framework
- Development database: SQLite
- Local API integration: Vite proxies `/api` to Django

## Start the backend

```sh
cd backend
source .venv/bin/activate
python manage.py runserver
```

The API health check is available at `http://127.0.0.1:8000/api/health/`.

## Start the frontend

In a second terminal:

```sh
cd frontend
PATH="../.tools/bin:$PATH" npm run dev
```

Open the URL Vite prints, usually `http://localhost:5173`.

## Verify the setup

```sh
cd backend
.venv/bin/python manage.py test
.venv/bin/python manage.py check

cd ../frontend
PATH="../.tools/bin:$PATH" npm run lint
PATH="../.tools/bin:$PATH" npm run build
```

The repository includes a project-local Node.js runtime in `.tools` because Node.js was not installed on the machine during setup. It is ignored by Git. For a normal team setup, install Node.js 22 LTS globally or through a version manager and use `npm` directly.

## Suggested next foundations

1. Add environment-based Django settings and a production secret key.
2. Create health-centre models for services, staff, appointments, and patient enquiries.
3. Add authentication and role-based access before storing patient data.
4. Replace SQLite with PostgreSQL before deployment.
5. Add privacy, consent, audit logging, backups, and HTTPS for patient information.
# oniruphc

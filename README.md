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

## Online appointments

The homepage includes an online booking form. Requests are saved as **Appointments** in Django Admin, where staff can search bookings and change their status from pending to confirmed or cancelled. The homepage shows upcoming service, date, time, and status; patient names, phone numbers, email addresses, and notes remain private.

## Patient records GUI

Django Admin provides the first backend GUI for clinic staff. Create an administrator account once:

```sh
cd backend
.venv/bin/python manage.py createsuperuser
```

After starting Django, open `http://127.0.0.1:8000/admin/` and sign in. The **Patients** section lets you add and edit records, search by patient number, name, phone, or email, and filter by sex, blood group, or registration date. Staff profiles are also visible under **Staff profiles**.

Use a strong private password and do not expose the development admin to the public internet.

## Default development staff

Create or verify the three staff accounts with:

```sh
cd backend
.venv/bin/python manage.py seed_staff
```

For local development, the default password is `ChangeMe123!`:

- Doctor: `doctor`
- Nurse: `nurse`
- Front desk: `frontdesk`

Set `STAFF_DEFAULT_PASSWORD` before running `seed_staff` to use a different password. Change these credentials before any shared or production deployment.

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
3. Add role-based dashboards and password reset before storing patient data.
4. Replace SQLite with PostgreSQL before deployment.
5. Add privacy, consent, audit logging, backups, and HTTPS for patient information.

## Deploy on Render

The repository includes `render.yaml` for the Django API, Vite frontend, and PostgreSQL database.

1. Push the repository to GitHub.
2. In Render, choose **New > Blueprint**, connect the GitHub repository, and apply `render.yaml`.
3. After the API service is created, copy its public URL, for example `https://oniru-phc-api.onrender.com`.
4. In the frontend service environment, set `VITE_API_URL` to that URL followed by `/api`.
5. In the API service environment, set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to the frontend URL, for example `https://oniru-phc-frontend.onrender.com`.
6. Redeploy the frontend after saving its environment variable.
7. Open the API service Shell and run `python manage.py createsuperuser`, then use `/admin/` to manage staff and patient records.

Do not use the development staff password in production. Set `STAFF_DEFAULT_PASSWORD` before running `python manage.py seed_staff`, or create staff accounts through Django Admin.
# oniruphc

# Healthcare Backend (Django + DRF + PostgreSQL)

A robust and secure backend service for a healthcare application built with **Django**, **Django REST Framework (DRF)**, and **PostgreSQL**. The system provides JWT-authenticated access for healthcare professionals to manage patient records, maintain a doctor directory, and establish patient-doctor mapping relationships.

## Stack

- **Django** + **Django REST Framework**
- **PostgreSQL** (configurable via `DATABASE_URL` or individual `DB_*` variables; SQLite fallback for local test runs)
- **JWT** via `djangorestframework-simplejwt`
- **django-cors-headers** for cross-origin frontend support
- **python-dotenv** for environment-based configuration

## Setup

1. **Clone and create virtual environment**

   ```bash
   python -m venv venv
   # Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # Windows Command Prompt:
   .\venv\Scripts\activate.bat
   # Linux / macOS:
   source venv/bin/activate
   ```

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**

   Copy `.env.example` to `.env` and set:

   - `SECRET_KEY` – Django secret (required in production)
   - `DATABASE_URL` – e.g. `postgres://user:password@localhost:5432/healthcare_db` (or set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)
   - `DEBUG` & `ALLOWED_HOSTS`

   If `.env` is missing, the app falls back to defaults for local development.

3. **Database**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser   # optional, for admin
   ```

4. **Run Development Server**

   ```bash
   python manage.py runserver
   ```

   API Root available at: `http://localhost:8000/`

## API Overview

Base URL: `http://localhost:8000/api/`

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST   | `/api/auth/register/` | Register (`name`, `email`, `password`, `password_confirm` [opt]) | No |
| POST   | `/api/auth/login/`    | Login (`email`, `password`) → returns `access`, `refresh`, `user` | No |
| POST   | `/api/auth/token/refresh/` | Obtain fresh access token using `refresh` token | No |
| GET    | `/api/auth/me/`       | Retrieve authenticated user profile | Yes (Bearer) |

Include the access token in the header for authenticated requests:  
`Authorization: Bearer <access_token>`

### Patients (Authenticated; Users See Only Their Own)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/patients/`      | Create patient |
| GET    | `/api/patients/`      | List current user's patients (paginated) |
| GET    | `/api/patients/<id>/` | Get details of a specific patient |
| PUT    | `/api/patients/<id>/` | Update patient details (treated as partial-safe) |
| PATCH  | `/api/patients/<id>/` | Partially update patient details |
| DELETE | `/api/patients/<id>/` | Delete a patient record |

- **Patient payload**: `name` (or `first_name`, `last_name`), `age`, `gender` (`male`/`female`/`other`, case-insensitive), `address` (optional), `contact_number` (optional), `medical_history` (optional).

### Doctors

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET    | `/api/doctors/`       | List all registered doctors (paginated) | No (Public) |
| GET    | `/api/doctors/<id>/`  | Get details of a specific doctor | No (Public) |
| POST   | `/api/doctors/`       | Create new doctor | Yes (Bearer) |
| PUT    | `/api/doctors/<id>/`  | Update doctor details (partial-safe) | Yes (Bearer) |
| PATCH  | `/api/doctors/<id>/`  | Partially update doctor details | Yes (Bearer) |
| DELETE | `/api/doctors/<id>/`  | Delete a doctor record | Yes (Bearer) |

- **Doctor payload**: `name` (or `first_name`, `last_name`), `specialization`, `experience_years` (or `years_of_experience`), `email` (optional, unique), `phone_number` (optional).

### Patient–Doctor Mappings (Authenticated; Scoped to Current User's Patients)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/mappings/`              | Assign doctor to patient (`patient_id`, `doctor_id`, `notes` [opt]) |
| GET    | `/api/mappings/`              | List all mappings for current user's patients |
| GET    | `/api/mappings/<patient_id>/` | Get doctors assigned to a specific patient |
| GET    | `/api/mappings/patient/<patient_id>/` | Alias endpoint to get doctors assigned to a patient |
| DELETE | `/api/mappings/<id>/`        | Remove mapping (`id` = mapping pk) |

- **Integrity**: Enforced `unique_together` constraint prevents duplicate doctor assignments to the same patient.

## Tests

Run the full test suite:

```bash
python manage.py test
```

This will execute unit tests for:

- `authentication` – registration, duplicate email rejection, and JWT login flows
- `patients` – authenticated CRUD, per-user scoping, and validation checks
- `doctors` – public list/retrieve, authenticated write operations, and uniqueness checks
- `mappings` – assigning/removing doctors to/from patients with permission checks

## Production Notes

- Set `SECRET_KEY` and `DATABASE_URL` in the environment; do not rely on defaults.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Use a production WSGI/ASGI server (e.g. `gunicorn config.wsgi:application` or `uvicorn config.asgi:application`) and run `python manage.py collectstatic`.

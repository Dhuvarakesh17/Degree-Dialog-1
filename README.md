# Degree Dialog

A student-facing information & Q&A portal for colleges — built as a **monorepo** with a React frontend and a Django backend. The goal is simple: let students search, chat, and discover college info (programs, fees, departments, FAQs, announcements, etc.) through a clean web UI backed by a robust API.

> Live site: https://degree-dialog-1.vercel.app/

---

## 🧭 Repository Structure

```
.
├─ frontend/           # React app (SPA) served separately (deployed to Vercel)
├─ myproject/          # Django project (settings, urls, wsgi/asgi)
├─ myapp/              # Django app (models, views, serializers, admin, etc.)
├─ manage.py           # Django entrypoint
├─ requirements.txt    # Python dependencies
└─ db.sqlite3          # Local dev DB (do NOT use in production)
```

> Heads up: **db.sqlite3** is committed for local dev/testing convenience but should be excluded for production. Use Postgres/MySQL in prod and environment variables for secrets.

---

## ✨ Features (current & planned)

- 🔎 **Searchable college info**: programs, departments, FAQs, and more
- 💬 **Q&A / dialog UI** (frontend) for quick answers
- 🔐 **Auth-ready design** (can integrate Clerk/Auth0/Django auth)
- ⚡ **Django REST-style API** powering the frontend
- 🌐 **CORS-enabled** local dev flow
- 🚀 **CI/CD-friendly** (frontend deployable to Vercel; backend to Render/Railway/Azure)

> This README gives a working local setup; fine-tune per your exact models/endpoints.

---

## 🛠 Tech Stack

- **Frontend:** React (Vite or CRA), JavaScript/TypeScript, CSS/Tailwind (optional)
- **Backend:** Django, Django REST Framework (assumed), SQLite (dev), Postgres/MySQL (prod)
- **Infra:** Vercel (frontend), Render/Railway/Azure App Service (backend)
- **Tooling:** Node.js, Python 3.10+, pip/venv

---

## ⚙️ Local Development

### 1) Backend (Django)

```bash
# from repo root
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# (optional) set your env vars for local
# On PowerShell:
# $env:DJANGO_SECRET_KEY="dev-secret"
# $env:DJANGO_DEBUG="1"
# $env:ALLOWED_HOSTS="*"
# $env:CORS_ALLOWED_ORIGINS="http://localhost:5173,http://localhost:3000"

python manage.py migrate
python manage.py createsuperuser  # optional, for admin access
python manage.py runserver 0.0.0.0:8000
```

Django should now be running at **http://localhost:8000**.

> If you’re using **django-cors-headers**, ensure `CORS_ALLOWED_ORIGINS` (or `CORS_ALLOW_ALL_ORIGINS=True` for quick dev) is set to allow your frontend origin.

---

### 2) Frontend (React)

```bash
cd frontend

# If you're using npm
npm install
npm run dev

# If you're using pnpm
# pnpm install
# pnpm dev

# If you're using yarn
# yarn
# yarn dev
```

The dev server typically runs at **http://localhost:5173** (Vite) or **http://localhost:3000** (CRA/Next).

Create a `.env` (or `.env.local`) with your API base URL:

```
# Vite-style
VITE_API_URL=http://localhost:8000

# CRA-style
REACT_APP_API_URL=http://localhost:8000
```

In your frontend API client, read from the env (e.g., `import.meta.env.VITE_API_URL`).

---

## 🔌 Wiring Frontend ↔ Backend

A minimal fetch example (Vite + plain JS):

```js
const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function getPrograms() {
  const res = await fetch(`${API}/api/programs/`);
  if (!res.ok) throw new Error("Failed to fetch programs");
  return res.json();
}
```

Be sure your Django `urls.py` exposes a predictable prefix like `/api/` and that CORS is configured.

---

## 📦 Production Setup (Recommended)

- **Frontend (Vercel):**
  - Framework preset: React/Vite
  - Build command: `npm run build`
  - Output directory: `dist` (for Vite) or `build` (for CRA)
  - Environment variables: `VITE_API_URL` = your backend URL

- **Backend (Render / Railway / Azure App Service):**
  - Use **Postgres** in production.
  - Set environment variables:
    - `DJANGO_SECRET_KEY` (a long random string)
    - `DJANGO_DEBUG=0`
    - `ALLOWED_HOSTS=your-domain.com`
    - `DATABASE_URL=postgres://...`
    - `CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app`
  - Run migrations on deploy:
    - `python manage.py migrate`
  - Collect static files (if needed):
    - `python manage.py collectstatic --noinput`

> Tip: Keep `db.sqlite3` out of production and rotate secrets if any were ever committed.

---

## 🗂 Suggested Django Settings Snippet (example)

```python
# myproject/settings.py (snippets)
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = bool(int(os.getenv("DJANGO_DEBUG", "1")))
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    # ...
    "django.contrib.staticfiles",
    # "rest_framework",
    # "corsheaders",
    "myapp",
]

MIDDLEWARE = [
    # "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    # ...
]

# CORS (if using django-cors-headers)
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
```

Uncomment DRF/CORS if added to `requirements.txt`.

---

## 🧪 API Endpoints (fill in)

Document your endpoints here once stable:

```
GET  /api/programs/           -> list programs
GET  /api/programs/{id}/      -> program detail
GET  /api/faqs/               -> list FAQs
POST /api/query/              -> ask a question (if you add Q&A)
```

> Add serializers, permissions and pagination notes as needed.

---

## 📸 Screenshots (optional)

Add a few UI shots here for quick context (Home, Search, Details, Admin).

---

## 🗺 Roadmap

- [ ] Finalize data models (Programs, Departments, Fees, FAQs)
- [ ] Publish stable API docs (OpenAPI/Swagger)
- [ ] Add auth (Clerk/Auth0/Django)
- [ ] Add search & filters
- [ ] Role-based admin panel
- [ ] Deploy backend (Render/Railway/Azure)
- [ ] Custom domain + HTTPS + SEO

---

## 🤝 Contributing

PRs welcome! Please open an issue to discuss major changes first. Keep commits small and focused.

---

## 🛡 License

Add a license file (e.g., MIT) or clarify usage restrictions. (Currently **unspecified**.)

---

## 🙋 FAQ

**Why a monorepo?** Easier local dev and atomic changes across frontend & backend.

**Where do I change the API base URL?** In frontend `.env` (e.g., `VITE_API_URL`) and Django CORS settings.

**Can I deploy both on one host?** Yes: serve the built frontend from Django (collectstatic + whitenoise) or keep split (Vercel + managed Django).

---

## Credits

Built by **Team Degree Dialog**. Shout-out to everyone contributing to better, clearer college info for students.

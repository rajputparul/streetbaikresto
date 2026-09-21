# Street Baik Resto Cafe

Production-ready Django website for Street Baik Resto Cafe, with menu browsing, cart checkout, order tracking, reservations, gallery photos/videos, staff order management, and WhatsApp-based customer support.

## Features

- Responsive dark restaurant UI with red Street Baik accents
- Database-backed menu items with categories, images, descriptions and prices
- Cart with quantity increase/decrease, remove, totals and local persistence
- Checkout for Delivery, Takeaway and Dine-in
- Backend and frontend 10-digit phone validation
- Delivery address collection with clear "within 4 km only" messaging
- Unique customer order IDs such as `SBK-20260921-1001`
- Customer order tracking by Order ID
- Staff dashboard for orders, reservations, reviews and messages
- Django admin for managing menu, orders and site data
- Photo and video gallery using existing static media
- WhatsApp support links and safe Twilio WhatsApp notification hooks
- Production settings for env vars, HTTPS cookies and static files

## Tech Stack

- Python 3
- Django 5
- SQLite for local development
- PostgreSQL via `DATABASE_URL` for production
- WhiteNoise for static files
- Gunicorn for production serving
- HTML, CSS and vanilla JavaScript

## Local Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_menu
python manage.py createsuperuser
python manage.py runserver
```

Open:

- Customer website: `http://127.0.0.1:8000/`
- Staff dashboard: `http://127.0.0.1:8000/staff/`
- Django admin: `http://127.0.0.1:8000/admin/`
- Order tracking: `http://127.0.0.1:8000/track/`

## Environment Variables

Copy `.env.example` to `.env` locally. Never commit `.env`.

```env
DJANGO_SECRET_KEY=change-this
DEBUG=1
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
SITE_URL=
DATABASE_URL=
DELIVERY_RADIUS_KM=4
CLIENT_WHATSAPP=8129935964
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

## WhatsApp

Customer support uses normal WhatsApp links configured by `CLIENT_WHATSAPP`.

Automatic WhatsApp order notifications are wired for Twilio WhatsApp, but real delivery requires a WhatsApp-enabled Twilio sender plus `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_WHATSAPP_FROM`. If credentials are missing, the app logs the notification as not configured instead of pretending it was sent.

## Delivery Radius

The site clearly communicates "Delivery available within 4 km only" and collects a delivery address. It does not perform real distance validation yet. Reliable distance validation requires a maps/geocoding provider such as Google Maps Distance Matrix or a delivery-zone workflow, with API keys stored in environment variables.

## Database

SQLite is acceptable for local development and very small single-instance deployments when backups are handled. For the real client deployment, PostgreSQL is recommended because orders are operational business data and should survive deploys/restarts reliably. The app automatically uses PostgreSQL when `DATABASE_URL` is set.

## GitHub Preparation

Before pushing, confirm `.env`, SQLite databases, venvs, caches and collected static files are ignored.

```powershell
git status --short
git init
git add .
git commit -m "Initial production-ready website"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Do not push until secrets have been checked and `.env` is untracked.

## Recommended Deployment: Render

Render is a good fit because it supports Django, env vars, HTTPS, custom domains, build commands, static collection and managed PostgreSQL.

1. Push the repository to GitHub.
2. In Render, create a PostgreSQL database.
3. In Render, create a new Web Service from the GitHub repo.
4. Use:
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start command: `gunicorn streetbaik.wsgi:application`
5. Set environment variables:
   - `DEBUG=0`
   - `DJANGO_SECRET_KEY=<strong-generated-secret>`
   - `ALLOWED_HOSTS=<your-render-host>,streetbaik.com,www.streetbaik.com`
   - `CSRF_TRUSTED_ORIGINS=https://<your-render-host>,https://streetbaik.com,https://www.streetbaik.com`
   - `SITE_URL=https://streetbaik.com`
   - `DATABASE_URL=<Render PostgreSQL internal database URL>`
   - `CLIENT_WHATSAPP=8129935964`
   - Optional Twilio WhatsApp variables
6. Deploy.
7. Seed the menu once from Render Shell if the database is empty:

```bash
python manage.py seed_menu
```

8. Create a Django superuser from Render Shell:

```bash
python manage.py createsuperuser
```

## Custom Domain, DNS and HTTPS

- Hosting: Render runs the Django application.
- GitHub: stores the source code and triggers deployments.
- Domain: the public address, for example `streetbaik.com`.
- DNS: points the domain to Render.
- HTTPS/SSL: Render provisions certificates after DNS is connected.

Typical DNS setup in your domain registrar:

- `www` CNAME -> Render hostname
- Apex/root domain (`streetbaik.com`) -> Render-provided A/ALIAS/ANAME record, depending on registrar support

After DNS is verified in Render, add both `streetbaik.com` and `www.streetbaik.com` to `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.

## Future Improvements

- Real distance validation with a maps API
- PostgreSQL migration for heavier production use
- Payment gateway integration
- Image/video optimization pipeline
- Automated browser tests in CI

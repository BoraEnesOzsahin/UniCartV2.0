# UniCart — University Marketplace

A Django web app for university students to buy and sell secondhand items.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Apps
- `listings/` — items for sale (CRUD)
- `users/`    — auth, profiles, dashboard

## Environment
Create a `.env` file from `.env.example` and fill in your values.

For email verification, set SMTP credentials so real verification emails can be sent:

```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-smtp-username@example.com
EMAIL_HOST_PASSWORD=your-smtp-password
DEFAULT_FROM_EMAIL=noreply@unicart.local
```

If SMTP credentials are missing, the app will fall back to the console email backend and emails will only appear in the server terminal.

## Key URLs
| URL | Page |
|-----|------|
| / | Home |
| /listings/ | Browse all |
| /listings/create/ | Post item |
| /users/register/ | Sign up |
| /users/login/ | Login |
| /users/dashboard/ | My items |
| /admin/ | Admin panel |

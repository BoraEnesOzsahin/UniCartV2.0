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

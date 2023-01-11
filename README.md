# Library-API
API online management system for book borrowings written on DRF.

## Features
- JWT authentication
- Admin panel `/admin/`
- Documentation is located at `/schema/swagger/`
- Managing books and borrowings
- Filtering borrowing by active borrowing (`is_active`)
and `user_id` (admin only)

## Installing using GitHub

```bash
git https://github.com/AndriyKy/library-api.git
cd library-api
python -m venv venv
sourve venv/bin/activate
pip install -r requirements.txt
````
- Copy **.env.sample** -> **.env** and populate with all required data

### Run locally

```bash
python manage.py migrate
python manage.py runserver
```

## Getting access

- create a user via `/users/create/`
- get access token via `/users/token/`
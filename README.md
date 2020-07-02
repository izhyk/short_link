# Short Link Service

## Installation
1. Setup database: 
```
sudo -u postgres psql 
create user user_name with password 'password';
create database link_db owner user_name;
grant all privileges on database link_db to user_name;
\q
```
  - change user_name, password and db_name in DATABASES  in settings.py
2. Create virtual environment
3. Activate virtual environment
4. Install all requirements `pip install -r requirements.txt`
5. Run migrations `python manage.py migrate`
6. Create superuser `python manage.py createsuperuser`
7. Run server `python manage.py runserver`
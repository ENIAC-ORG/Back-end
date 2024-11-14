#!/bin/sh

echo "Waiting for postgresql to start..."
./wait-for.sh db:5432 
echo "delete cache files *******************************************" 
# rmdir /s /q accounts\migrations reservation\migrations telegrambot\migrations Profile\migrations counseling\migrations TherapyTests\migrations Doctorpanel\migrations Rating\migrations
rm -rf accounts/__pycache__ reservation/__pycache__ telegrambot/__pycache__ GoogleMeet/__pycache__ Profile/__pycache__ counseling/__pycache__ TherapyTests/__pycache__ Doctorpanel/__pycache__ Rating/__pycache__ recomendationSys/__pycache__
rm -rf accounts/migrations reservation/migrations telegrambot/migrations Profile/migrations counseling/migrations TherapyTests/migrations Doctorpanel/migrations Rating/migrations recomendationSys/migrations 
# rmdir /s /q accounts\__pycache__ reservation\__pycache__ telegrambot\__pycache__ GoogleMeet\__pycache__ Profile\__pycache__ counseling\__pycache__ TherapyTests\__pycache__ Doctorpanel\__pycache__ Rating\__pycache__ recomendationSys\__pycache__   GoogleMeet/migrations
echo "Migrating the databse...################################################################"
python manage.py makemigrations accounts counseling Profile reservation TherapyTests Rating Doctorpanel

# python manage.py sqlmigrate accounts 0001 > data.sql
# python manage.py sqlmigrate telegrambot 0001 >> data.sql
# python manage.py sqlmigrate counseling 0001 >> data.sql
# python manage.py sqlmigrate Profile 0001 >> data.sql
# python manage.py sqlmigrate reservation 0001 >> data.sql
# python manage.py sqlmigrate TherapyTests 0001 > data.sql
# python manage.py sqlmigrate Rating 0001 >> data.sql
# python manage.py sqlmigrate Doctorpanel 0001 >> data.sql

python manage.py migrate
# python manage.py migrate --noinput

echo "set admin *******************************************"
DJANGO_SUPERUSER_PASSWORD=eniac@1403 python manage.py createsuperuser --no-input --email=eniakgroupiust@gmail.com

echo "Starting the server...******************************************************************"
python -u manage.py runserver 0.0.0.0:8000

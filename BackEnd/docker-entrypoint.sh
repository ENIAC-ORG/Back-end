#!/bin/bash


echo "Waiting for postgresql to start..."
./wait-for.sh db:5432
apps=(
    "accounts"
    "Profile"
    "counseling"
    "django.contrib.sites"
    "reservation"
    "TherapyTests"
    "Doctorpanel"
    "Rating"
    "channels"
    "chat"
    "depression_chat"
    "recomendationSys"
)

echo "--------------------------- Migrating the databse ---------------------------"
for app in "${apps[@]}"; do
    echo "Running makemigrations for app: $app"
    python manage.py makemigrations "$app"
done
python manage.py migrate
# python manage.py migrate --noinput

echo "--------------------------- Set Admin ---------------------------"
DJANGO_SUPERUSER_PASSWORD=eniac@1403 python manage.py createsuperuser --no-input  --email=eniakgroupiust@gmail.com

echo "--------------------------- Starting the Server ---------------------------"
# python -u manage.py runserver 0.0.0.0:8000
uvicorn BackEnd.asgi:application --host 0.0.0.0 --port 8000



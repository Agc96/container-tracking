@echo off

rem TODO: Cambiar "key" por la clave brindada por Google Maps
set GOOGLE_MAPS_KEY=key

rem Iniciar el servidor de Django
python manage.py runserver

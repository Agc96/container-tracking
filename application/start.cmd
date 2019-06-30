@echo off

rem TODO: Cambiar "key" por la clave brindada por Google Maps
set TRACKING_MAPS_KEY=key

rem TODO: Cambiar "localhost" por la base de datos en AWS
set TRACKING_DB_HOST=localhost
set TRACKING_DB_NAME=tracking
rem TODO: Cambiar "username" por el nombre de usuario de la base de datos
set TRACKING_DB_USERNAME=username
rem TODO: Cambiar "password" por la contraseña de la base de datos
set TRACKING_DB_PASSWORD=password

rem Iniciar el servidor de Django
python manage.py runserver

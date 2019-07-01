@echo off

rem Tener cuidado con los caracteres especiales de los batch scripts.
rem Ver https://www.robvanderwoude.com/escapechars.php para más información.

rem TODO: Colocar un random string de 32 caracteres que no haya sido autogenerado por Django
set TRACKING_SECRET_KEY=
rem TODO: Para el pase a producción, cambiar este flag a False
set TRACKING_DEBUG=True
rem TODO: Colocar la clave brindada por Google Maps
set TRACKING_MAPS_KEY=
rem TODO: Cambiar "localhost" por la base de datos en AWS
set TRACKING_DB_HOST=localhost
rem TODO: Verificar que "tracking" será efectivamente el nombre del esquema de base de datos
set TRACKING_DB_NAME=tracking
rem TODO: Verificar que "webapp" por el nombre de usuario de la base de datos
set TRACKING_DB_USERNAME=webapp
rem TODO: Cambiar "password" por la contraseña de la base de datos
set TRACKING_DB_PASSWORD=

rem Iniciar el servidor de Django
python manage.py runserver

@echo off

rem Tener cuidado con los caracteres especiales de los batch scripts.
rem Ver https://www.robvanderwoude.com/escapechars.php para más información.

rem TODO: Cambiar "localhost" por la base de datos en AWS
set TRACKING_DB_HOST=localhost
rem TODO: Verificar que "tracking" será efectivamente el nombre del esquema de base de datos
set TRACKING_DB_NAME=tracking
rem TODO: Verificar que "webapp" por el nombre de usuario de la base de datos
set TRACKING_DB_USERNAME=webapp
rem TODO: Cambiar "password" por la contraseña de la base de datos
set TRACKING_DB_PASSWORD=

rem TODO: Colocar el correo electrónico que usará el scraper
set EMAIL_FROM_USER=
rem TODO: Colocar la contraseña del correo electrónico que usará el scraper
set EMAIL_FROM_PASS=
rem TODO: Colocar el correo electrónico del webmaster
set EMAIL_TO_USER=

rem Iniciar el Web Scraper
python wrapper.py

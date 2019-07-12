@echo off

rem Tener cuidado con los caracteres especiales de los batch scripts.
rem Ver https://www.robvanderwoude.com/escapechars.php para más información.

rem TODO: Cambiar "localhost" por la base de datos en AWS
set TRACKING_DB_HOST=localhost
rem TODO: Verificar que "tracking" será efectivamente el nombre del esquema de base de datos
set TRACKING_DB_NAME=tracking
rem TODO: Verificar que "webapp" por el nombre de usuario de la base de datos
set TRACKING_DB_USERNAME=webapp
rem TODO: Colocar la contraseña de la base de datos
set TRACKING_DB_PASSWORD=

rem TODO: Colocar el correo electrónico que usará el scraper
set EMAIL_FROM_USER=
rem TODO: Colocar la contraseña del correo electrónico que usará el scraper
set EMAIL_FROM_PASS=
rem TODO: Colocar el correo electrónico del webmaster
set EMAIL_TO_USER=

rem Ir al directorio del paquete del Web Scraper
cd final

if %1%==mail (
    rem Iniciar los tests del servidor de correo electrónico
    python mail.py
) else if %1%==tests (
    rem Iniciar los tests del Web Scraper
    python tests.py
) else (
    rem Iniciar el Web Scraper
    python wrapper.py
)

# TODO: Cambiar "localhost" por la base de datos en AWS
export TRACKING_DB_HOST="localhost"
# TODO: Verificar que "tracking" será efectivamente el nombre del esquema de base de datos
export TRACKING_DB_NAME="tracking"
# TODO: Verificar que "webapp" por el nombre de usuario de la base de datos
export TRACKING_DB_USERNAME="scraper"
# TODO: Colocar la contraseña de la base de datos
export TRACKING_DB_PASSWORD=

# TODO: Colocar el correo electrónico que usará el scraper
export EMAIL_FROM_USER=
# TODO: Colocar la contraseña del correo electrónico que usará el scraper
export EMAIL_FROM_PASS=
# TODO: Colocar el correo electrónico del webmaster
export EMAIL_TO_USER=

cd final

# Iniciar los tests del servidor de correo electrónico
if [ "$1" = "mail" ]; then
    python3 mail.py
# Iniciar los tests del Web Scraper
elif [ "$1" = "tests" ]; then
    python3 tests.py
# Iniciar el Web Scraper
else
    python3 wrapper.py
fi

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

# Iniciar el Web Scraper
cd final

if [ "$1" = "mail" ]; then
    # Iniciar los tests del servidor de correo electrónico
    python3 mail.py
elif [ "$1" = "tests" ]; then
    # Iniciar los tests del Web Scraper
    python3 tests.py
else
    # Iniciar el Web Scraper
    python3 wrapper.py
fi

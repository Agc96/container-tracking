# TODO: Colocar un random string de 32 caracteres que no haya sido autogenerado por Django
export TRACKING_SECRET_KEY=
# TODO: Para el pase a producción, cambiar este flag a False
export TRACKING_DEBUG="True"
# TODO: Colocar la clave brindada por Google Maps
export TRACKING_MAPS_KEY=
# TODO: Cambiar "localhost" por la base de datos en AWS
export TRACKING_DB_HOST="localhost"
# TODO: Verificar que "tracking" será efectivamente el nombre del esquema de base de datos
export TRACKING_DB_NAME="tracking"
# TODO: Verificar que "webapp" por el nombre de usuario de la base de datos
export TRACKING_DB_USERNAME="webapp"
# TODO: Cambiar "password" por la contraseña de la base de datos
export TRACKING_DB_PASSWORD=

# Iniciar el servidor de Django
python3 manage.py runserver

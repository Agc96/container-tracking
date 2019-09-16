# Ir al directorio del paquete del Web Scraper
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

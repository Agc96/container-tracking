@echo off

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

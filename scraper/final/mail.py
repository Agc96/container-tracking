from env import *

from datetime import datetime

import smtplib
import ssl

class TrackingScraperEmail:
    TEST_MESSAGE = """Subject: Mensaje de prueba

Hola {user},
Este es un mensaje de prueba, para visualizar si el servicio de correo electronico esta funcionando correctamente.
Saludos,
El equipo de Tracking Scraper"""
    FINISH_MESSAGE = """Subject: Ha finalizado el scraper

Hola {user},
Te informamos que la aplicacion ha terminado de ejecutarse el {date}.
No se sabe si ha terminado su ejecucion correctamente o ha ocurrido algun error, por lo que es mejor revisar el log.
Saludos,
El equipo de Tracking Scraper"""
    ERRORS_MESSAGE = """Subject: Muchos errores

Hola {user},
Te informamos que la aplicacion lleva {extra} errores y es posible que no este ejecutandose correctamente.
Saludos,
El equipo de Tracking Scraper"""
    CARRIER_MESSAGE = """Subject: {extra} tuvo un error

Hola {user},
Te informamos que la aplicacion no ha podido conectarse con {extra}.
Seria bueno revisar la posible causa de esto en los logs, la captura del error y/o el HTML generado.
Saludos,
El equipo de TrackingScraper"""
    
    def __init__(self, extra = None):
        self.date  = datetime.now().strftime("%d/%m/%Y a las %H:%M")
        self.extra = extra
    
    def send(self, message):
        """Sends an email to the administrator."""
        message = message.format(date = self.date, user = EMAIL_TO["name"], extra = self.extra)
        with smtplib.SMTP_SSL(EMAIL_SMTP, EMAIL_PORT) as server:
            server.login(EMAIL_FROM["email"], EMAIL_FROM["pass"])
            server.sendmail(EMAIL_FROM["email"], EMAIL_TO["email"], message)

if __name__ == "__main__":
    TrackingScraperEmail().send(TrackingScraperEmail.TEST_MESSAGE)

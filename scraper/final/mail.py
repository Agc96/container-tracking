from env import *

from datetime import datetime

import smtplib
import ssl

class TrackingScraperEmail:
    FINISH_MESSAGE = """Subject: Ha finalizado el scraper

Hola {user},
Te informamos que la aplicacion ha terminado de ejecutarse el {date}.
No sabemos si ha terminado su ejecucion o ha ocurrido algun error, pero es mejor que revises el log.
Saludos,
El equipo de Tracking Scraper"""
    ERRORS_MESSAGE = """Subject: Muchos errores

Hola {user},
Te informamos que la aplicacion lleva {counter} errores y es posible que no este ejecutandose correctamente.
Saludos,
El equipo de Tracking Scraper"""
    def __init__(self, counter = None):
        self.date    = datetime.now().strftime("%d/%m/%Y a las %H:%M")
        self.counter = counter
    def send(self, message):
        message = message.format(date = self.date, user = EMAIL_TO["name"], counter = self.counter)
        with smtplib.SMTP_SSL(EMAIL_SMTP, EMAIL_PORT) as server:
            server.login(EMAIL_FROM["email"], EMAIL_FROM["pass"])
            server.sendmail(EMAIL_FROM["email"], EMAIL_TO["email"], message)

if __name__ == "__main__":
    TrackingScraperEmail().send(TrackingScraperEmail.FINISH_MESSAGE)

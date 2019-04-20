from env import *

from datetime import datetime
from email.mime.text import MIMEText

import smtplib
import ssl

class TrackingScraperEmail:
    """Mail service for the Tracking Scraper."""
    TEST_MESSAGE = {
        "subject" : "Mensaje de prueba",
        "content" : "Este es un mensaje de prueba enviado el {date}, para verificar si el servicio de correo está funcionando correctamente."
    }
    FINISH_MESSAGE = {
        "subject" : "Ha finalizado el scraper",
        "content" : "Te informamos que la aplicación ha terminado de ejecutarse el {date} y ha extraído {counter} contenedores."
    }
    ERRORS_MESSAGE = {
        "subject" : "Muchos errores",
        "content" : "Te informamos que la aplicación lleva {counter} errores y es posible que no esté ejecutándose correctamente."
    }
    CARRIER_MESSAGE = {
        "subject" : "{carrier} tuvo un error",
        "content" : "Te informamos que la aplicación no ha podido conectarse con {carrier}. Este es el intento número {counter}."
    }
    
    def __init__(self, **kwargs):
        self.data = kwargs
        self.data["user"] = EMAIL_TO["name"]
        self.data["date"] = datetime.now().strftime("%d/%m/%Y a las %H:%M")
    
    def send_message(self, content, subject):
        """Sends an email to the administrator."""
        # Parse message
        content = ("Hola {user},\n" + content + "\nSaludos,\nEl equipo de Tracking Scraper").format(**self.data)
        # Parse subject
        message = MIMEText(content, "plain", "UTF-8")
        message["Subject"] = subject.format(**self.data)
        # Send message through Gmail SMTP server
        with smtplib.SMTP_SSL(EMAIL_SMTP, EMAIL_PORT) as server:
            server.login(EMAIL_FROM["email"], EMAIL_FROM["pass"])
            server.sendmail(EMAIL_FROM["email"], EMAIL_TO["email"], message.as_string())
    
    def send(self, msg_info):
        """Wrapper for :meth:`send_message`, passing a :class:`dict` as message information."""
        self.send_message(msg_info["content"], msg_info["subject"])

if __name__ == "__main__":
    TrackingScraperEmail().send(TrackingScraperEmail.TEST_MESSAGE)

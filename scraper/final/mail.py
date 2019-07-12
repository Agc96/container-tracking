from config import ScraperConfig

from datetime import datetime
from email.mime.text import MIMEText

import os
import smtplib
import ssl

class ScraperEmail:
    """Mail service for the Tracking Scraper."""
    TEST_MESSAGE = {
        "subject" : "Mensaje de prueba",
        "content" : "Mensaje de prueba enviado el {date}, para verificar que el servicio de correo funcione correctamente."
    }
    ERROR_MESSAGE = {
        "subject" : "{carrier} tuvo un error",
        "content" : "La aplicación no ha podido conectarse con {carrier}. Este es el intento número {counter}."
    }
    FINISH_MESSAGE = {
        "subject" : "{carrier} ha finalizado",
        "content" : "Se ha terminado la ejecución de la naviera {carrier} el {date}, con {counter} contenedores."
    }
    
    def __init__(self, **kwargs):
        self.data = kwargs
        self.data["user"] = ScraperConfig.EMAIL_TO_NAME
        self.data["date"] = datetime.now().strftime("%d/%m/%Y a las %H:%M")
    
    def send_message(self, content, subject):
        """Sends an email to the administrator."""
        # Parse message
        self.data["content"] = content.format(**self.data)
        content = ("Hola {user},\n{content}\nSaludos,\nEl equipo de Tracking Scraper").format(**self.data)
        # Parse subject
        message = MIMEText(content, "plain", "UTF-8")
        message["Subject"] = subject.format(**self.data)
        # Send message through Gmail SMTP server
        with smtplib.SMTP_SSL(ScraperConfig.EMAIL_SMTP, ScraperConfig.EMAIL_PORT) as server:
            server.login(ScraperConfig.EMAIL_FROM_USER, ScraperConfig.EMAIL_FROM_PASS)
            server.sendmail(ScraperConfig.EMAIL_FROM_USER, ScraperConfig.EMAIL_TO_USER, message.as_string())
    
    def send(self, msg_info):
        """Wrapper for `send_message`, passing a `dict` as message information."""
        self.send_message(msg_info["content"], msg_info["subject"])

if __name__ == "__main__":
    ScraperEmail().send(ScraperEmail.TEST_MESSAGE)

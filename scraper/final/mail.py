import datetime
import os
import smtplib
import ssl
from email.mime.text import MIMEText

from dotenv import load_dotenv

from config import ScraperConfig

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
        self.login_user   = os.getenv("MAIL_LOGIN_USER")
        self.login_pass   = os.getenv("MAIL_LOGIN_PASS")
        self.send_name    = os.getenv("MAIL_SEND_NAME")
        self.send_user    = os.getenv("MAIL_SEND_USER")
        self.data         = kwargs
        self.data["user"] = self.send_name
        self.data["date"] = datetime.datetime.now().strftime("%d/%m/%Y a las %H:%M")

    def send_message(self, content, subject):
        """Sends an email to the administrator."""
        # Parse message
        self.data["content"] = content.format(**self.data)
        content = "Hola {user},\n{content}\nSaludos,\nEl equipo de Tracking Scraper".format(**self.data)
        # Parse subject
        message = MIMEText(content, "plain", "UTF-8")
        message["Subject"] = subject.format(**self.data)
        message["From"]    = self.login_user
        message["To"]      = self.send_user
        # Send message through Gmail SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.login_user, self.login_pass)
            server.sendmail(self.login_user, self.send_user, message.as_string())
            server.quit()

    def send(self, msg_info):
        """Wrapper for `send_message`, passing a `dict` as message information."""
        self.send_message(msg_info["content"], msg_info["subject"])

if __name__ == "__main__":
    load_dotenv()
    ScraperEmail().send(ScraperEmail.TEST_MESSAGE)

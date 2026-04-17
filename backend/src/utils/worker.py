from celery import Celery
import smtplib
from email.message import EmailMessage
from config import REDIS_URL_FORGOTPASS,SMTP_USER,SMTP_PASS,SMTP_HOST,SMTP_PORT

celery = Celery(
    "utils.worker",
    broker=REDIS_URL_FORGOTPASS,
    backend=REDIS_URL_FORGOTPASS
)

@celery.task(name="utils.worker.send_reset_code_email")
def send_reset_code_email(email:str,code:str):

    smtp_host = SMTP_HOST
    smtp_port = SMTP_PORT
    sender_email = SMTP_USER
    sender_password = SMTP_PASS

    msg = EmailMessage()
    msg["Subject"] = "Восстановление пароля Mocky"
    msg["From"] = sender_email
    msg["To"] = email
    msg.set_content(f"Твой код для сброса пароля: {code}\nОн действует 15 минут.")

    with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    
    return "Успешно отправлено"
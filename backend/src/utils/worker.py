from celery import Celery
import smtplib
from email.message import EmailMessage
from config import REDIS_URL_FORGOTPASS,SMTP_USER,SMTP_PASS,SMTP_HOST,SMTP_PORT
from database.database import async_session_maker
from datetime import datetime,timezone
from sqlalchemy import update,select
from models.models import User
import asyncio
from celery.schedules import crontab

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


async def _downgrade_expired_subs():
    async with async_session_maker() as session:
        now = datetime.now(timezone.utc)
        
        # массовое обновление: ищем тех, у кого кончился срок, и сбрасываем
        stmt = (
            update(User)
            .where(User.subscription_tier != "free")
            .where(User.subscription_expires_at < now)
            .values(
                subscription_tier="free",
                subscription_expires_at=None,
                sprint_voice_used=0
            )
        )
        await session.execute(stmt)
        await session.commit()


@celery.task(name='utils.worker.check_expired_subscriptions')
def check_expired_subscriptions():
    asyncio.run(_downgrade_expired_subs())


celery.conf.beat_schedule = {
    'check-expired-subscriptions-every-hour': {
        'task': 'utils.worker.check_expired_subscriptions',
        'schedule': crontab(minute=0), 
    },
}
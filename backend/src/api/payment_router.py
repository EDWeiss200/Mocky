from fastapi import APIRouter, Depends, Request
from yookassa import Configuration, Payment
import uuid
from auth.auth import current_user
from models.models import User
from api.dependencies import user_service
from services.user_services import UserServices
#from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, 
from config import TEST_YOOKASSA_SECRET_KEY,TEST_YOOKASSA_SHOP_ID
from models.enum import PaymentTariffEnum


Configuration.account_id = TEST_YOOKASSA_SHOP_ID
Configuration.secret_key = TEST_YOOKASSA_SECRET_KEY

router = APIRouter(
    tags=['payments'],
    prefix='/payments'
)

@router.post("/tgbot/create_link")
async def create_payment_link_tg_bot(
    amount: int, 
    tariff: PaymentTariffEnum, 
    user: User = Depends(current_user)
):
    # генерируем уникальный ключ идемпотентности, чтобы банк не списал деньги дважды при сбое сети
    idempotence_key = str(uuid.uuid4())
    
    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/mocky0_bot"
        },
        "capture": True,
        "description": f"Оплата тарифа {tariff} для пользователя {user.id}",
        "metadata": {
            "user_id": str(user.id),
            "tariff": tariff
        }
    }, idempotence_key)


    return {"payment_url": payment.confirmation.confirmation_url}


@router.post("/webhook")
async def yookassa_webhook(
    request: Request,
    user_service: UserServices = Depends(user_service)
):

    event_json = await request.json()
    
    if event_json.get("event") == "payment.succeeded":
        payment_obj = event_json.get("object")
        

        user_id = payment_obj["metadata"]["user_id"]
        tariff = payment_obj["metadata"]["tariff"]
        amount = int(float(payment_obj["amount"]["value"]))


        await user_service.process_successful_payment(user_id, tariff, amount)

    return {"status": "ok"}
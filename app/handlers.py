from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, api_client):
    telegram_id = message.from_user.id
    username = message.from_user.username or f"user_{telegram_id}"
    response = await api_client.login(telegram_id, username)
    if response:
        print(f"Успешный вход: {response}")
        await message.answer(
        "Привет! Я готов к работе. Выбери нужное действие:",
        reply_markup=builder.as_markup()
    )
    else:
        await message.answer("Ошибка авторизации.")

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🚀 Начать интервью", callback_data="start_interview")
    )
    
    

# Обработка любых сообщений и вывод в терминал
@router.message()
async def any_message(message: types.message):
    print(f"Получено сообщение от пользователя: {message.text}")
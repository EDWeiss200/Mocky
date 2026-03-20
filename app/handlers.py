from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🚀 Начать интервью", callback_data="start_interview")
    )
    
    await message.answer(
        "Привет! Я готов к работе. Выбери нужное действие:",
        reply_markup=builder.as_markup()
    )

# Обработка любых сообщений и вывод в терминал
@router.message()
async def any_message(message: types.message):
    print(f"Получено сообщение от пользователя: {message.text}")
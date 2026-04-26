import logging
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import InterviewProcess, get_main_menu
from .resumes import list_resumes_with_buttons

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, command: CommandObject, api, state: FSMContext):
    await state.clear() 
    telegram_id = message.from_user.id
    username = message.from_user.username or f"user_{telegram_id}"
    first_name = message.from_user.first_name

    if command.args:
        await api.confirm_link(telegram_id, command.args)

    try:
        is_logged_in = await api.login(telegram_id, username)
    except Exception as e:
        logging.error(f"Ошибка API при логине юзера {telegram_id}: {e}")
        is_logged_in = False

    if is_logged_in:
        await list_resumes_with_buttons(message, api, first_name)
    else:
        await message.answer(
            "<b>Упс! Ошибка авторизации.</b> 🤖\nСервер временно недоступен. Пожалуйста, попробуйте чуть позже.", 
            parse_mode="HTML"
        )

@router.message(InterviewProcess.interviewing, F.text == "⏸ Поставить на паузу")
async def pause_active_interview(message: types.Message, state: FSMContext):
    await state.set_state(None) 
    
    await message.answer(
        "⏸ <b>Интервью приостановлено.</b>\n\n"
        "Вы вернулись в главное меню. Чтобы продолжить, выберите эту сессию в разделе «📊 Активные сессии».",
        parse_mode="HTML",
        reply_markup=get_main_menu(is_interviewing=False)
    )

@router.message(Command("pay"))
async def cmd_pay(message: types.Message):
    await show_main_pay_screen(message)

async def show_main_pay_screen(message_or_callback):
    text = (
        "💎 <b>Mocky — готовься к интервью эффективно!</b>\n\n"
        "Открой полный доступ к возможностями нашего сервиса и увеличь свои шансы на оффер:\n\n"
        "✅ <b>Безлимитные интервью</b> — тренируйся сколько угодно\n"
        "✅ <b>AI-анализ ответов</b> — подробный разбор каждой ошибки\n"
        "✅ <b>Все роли интервьюеров</b> — от HR до CTO\n"
        "✅ <b>Приоритетная поддержка</b> — отвечаем сразу\n\n"
        "💳 <b>Выберите действие:</b>"
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🔥 Купить доступ", callback_data="buy_premium"),
                types.InlineKeyboardButton(text="💬 Техподдержка", url="https://t.me/mocky_support")
            ],
            [
                types.InlineKeyboardButton(text="🤖 О сервисе", callback_data="about_service")
            ]
        ]
    )

    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(text, parse_mode="HTML", reply_markup=kb)
    else:
        await message_or_callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(F.data == "buy_premium")
async def process_buy_premium(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🏃 Подписка SPRINT (250₽)", callback_data="buy_item_sprint")],
            [types.InlineKeyboardButton(text="🔥 Подписка PRO (700₽)", callback_data="buy_item_pro")],
            [types.InlineKeyboardButton(text="🪙 100 токенов (100₽)", callback_data="buy_item_t100")],
            [types.InlineKeyboardButton(text="🪙 300 токенов (300₽)", callback_data="buy_item_t300")],
            [types.InlineKeyboardButton(text="🪙 500 токенов (500₽)", callback_data="buy_item_t500")],
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_pay")]
        ]
    )
    await callback.message.edit_text(
        "✨ <b>Выберите тариф или пакет токенов:</b>\n\n"
        "Подписки дают безлимит на время, а токены позволяют оплачивать каждое интервью отдельно.",
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("buy_item_"))
async def show_product_card(callback: types.CallbackQuery):
    item_id = callback.data.replace("buy_item_", "")
    
    products = {
        "sprint": ("🏃 Тариф Sprint", "250", "Доступ ко всем функциям на 7 дней.\nИдеально для быстрой подготовки к конкретному собесу."),
        "pro": ("🔥 Тариф PRO", "700", "Доступ ко всем функциям на 30 дней.\nПолное погружение и отработка всех навыков без ограничений."),
        "t100": ("🪙 Пакет 100 токенов", "100", "Хватит примерно на 2-3 полных интервью с AI-анализом."),
        "t300": ("🪙 Пакет 300 токенов", "300", "Хватит на 7-10 интервью. Оптимальный выбор для практики."),
        "t500": ("🪙 Пакет 500 токенов", "500", "Запас на долгое время. Самый выгодный курс за токен."),
    }
    
    name, price, desc = products.get(item_id, ("Товар", "0", ""))
    
    text = (
        f"🌟 <b>{name}</b>\n\n"
        f"{desc}\n\n"
        f"💰 <b>К оплате: {price} ₽</b>\n"
        "────────────────────\n"
        "🚀 <i>После оплаты доступ откроется мгновенно!</i>"
    )
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f"💳 Оплатить {price} ₽", callback_data=f"final_pay_{item_id}")],
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="buy_premium")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("final_pay_"))
async def process_final_payment(callback: types.CallbackQuery):
    await callback.answer("⏳ Модуль оплаты подключается...", show_alert=True)

@router.callback_query(F.data == "about_service")
async def process_about_service(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🚀 <b>Mocky</b> — это ваш персональный AI-тренажер для прохождения технических и HR-интервью.\n\n"
        "Мы помогаем разработчикам преодолеть страх перед собеседованиями и подготовить качественные ответы на сложные вопросы.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_pay")]]
        ),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "back_to_pay")
async def process_back_to_pay(callback: types.CallbackQuery):
    await show_main_pay_screen(callback)
    await callback.answer()

@router.message()
async def any_message(message: types.Message):
    print(f"Получено сообщение: {message.text}")
    await message.answer("Я не понимаю эту команду. Воспользуйтесь меню.", reply_markup=get_main_menu())
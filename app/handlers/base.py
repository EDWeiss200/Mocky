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

    is_logged_in = await api.login(telegram_id, username)
    if is_logged_in:
        await list_resumes_with_buttons(message, api, first_name)
    else:
        await message.answer("Ошибка авторизации. Попробуйте позже.")

@router.message(F.text == "⏸ Поставить на паузу")
@router.message(Command("pause"))
async def cmd_pause(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == InterviewProcess.interviewing:
        await state.set_state(None) 
        await message.answer(
            "⏸ **Интервью приостановлено.**\n"
            "Вы вернулись в главное меню. Чтобы продолжить, выберите эту сессию в разделе '📊 Активные сессии'.",
            parse_mode="Markdown",
            reply_markup=get_main_menu(is_interviewing=False)
        )
    else:
        await state.set_state(None)
        await message.answer(
            "У вас сейчас нет активного интервью, но я на всякий случай сбросил текущие действия. 🫡",
            reply_markup=get_main_menu(is_interviewing=False)
        )

@router.message(Command("pay"))
async def cmd_pay(message: types.Message):
    await show_main_pay_screen(message)

async def show_main_pay_screen(message_or_callback):
    text = (
        "💎 **Mocky — готовься к интервью эффективно!**\n\n"
        "Открой полный доступ к возможностями нашего сервиса и увеличь свои шансы на оффер:\n\n"
        "✅ **Безлимитные интервью** — тренируйся сколько угодно\n"
        "✅ **AI-анализ ответов** — подробный разбор каждой ошибки\n"
        "✅ **Все роли интервьюеров** — от HR до CTO\n"
        "✅ **Приоритетная поддержка** — отвечаем сразу\n\n"
        "💳 **Выберите действие:**"
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
        await message_or_callback.answer(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await message_or_callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)

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
        "✨ **Выберите тариф или пакет токенов:**\n\n"
        "Подписки дают безлимит на время, а токены позволяют оплачивать каждое интервью отдельно.",
        reply_markup=kb,
        parse_mode="Markdown"
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
        f"🌟 **{name}**\n\n"
        f"{desc}\n\n"
        f"💰 **К оплате: {price} ₽**\n"
        "────────────────────\n"
        "🚀 *После оплаты доступ откроется мгновенно!*"
    )
    
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=f"💳 Оплатить {price} ₽", callback_data=f"final_pay_{item_id}")],
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="buy_premium")]
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data.startswith("final_pay_"))
async def process_final_payment(callback: types.CallbackQuery):
    await callback.answer("⏳ Модуль оплаты подключается...", show_alert=True)

@router.callback_query(F.data == "about_service")
async def process_about_service(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🚀 Mocky — это ваш персональный AI-тренажер для прохождения технических и HR-интервью.\n\n"
        "Мы помогаем разработчикам преодолеть страх перед собеседованиями и подготовить качественные ответы на сложные вопросы.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_pay")]]
        )
    )

@router.callback_query(F.data == "back_to_pay")
async def process_back_to_pay(callback: types.CallbackQuery):
    await show_main_pay_screen(callback)
    await callback.answer()

@router.message()
async def any_message(message: types.Message):
    print(f"Получено сообщение: {message.text}")
    await message.answer("Я не понимаю эту команду. Воспользуйтесь меню.", reply_markup=get_main_menu())

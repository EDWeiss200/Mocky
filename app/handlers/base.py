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

@router.message()
async def any_message(message: types.Message):
    print(f"Получено сообщение: {message.text}")
    await message.answer("Я не понимаю эту команду. Воспользуйтесь меню.", reply_markup=get_main_menu())

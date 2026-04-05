from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class InterviewProcess(StatesGroup):
    waiting_for_resume = State() 
    ready_to_start = State()    
    interviewing = State()

router = Router()

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать интервью")],
            [KeyboardButton(text="ℹ️ Мой профиль"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard

@router.message(Command("start"))
async def cmd_start(message: types.Message, api, state: FSMContext):
    telegram_id = message.from_user.id
    username = message.from_user.username or f"user_{telegram_id}"
    
    response = await api.login(telegram_id, username)

    if response:
        await state.set_state(InterviewProcess.waiting_for_resume)
        await message.answer(
            "Привет! Ты успешно авторизован. 📄 Пришли мне свое резюме в формате PDF.",
            reply_markup=get_main_menu() # Показываем меню с кнопками внизу
        )
    else:
        await message.answer("Ошибка авторизации на сервере.")


@router.callback_query(F.data == "start_interview")
async def start_interview_handler(callback: types.CallbackQuery, state: FSMContext, api):
    await callback.answer()
    user_data = await state.get_data()
    
    if not user_data.get("resume_id"):
        return await callback.message.answer("Сначала пришли файл! 📄")

    interview_data = await api.start_interview(callback.from_user.id, user_data.get("resume_id"))
    
    if interview_data:
        await state.update_data(interview_id=interview_data.get("id"))
        await state.set_state(InterviewProcess.interviewing)
        
        await callback.message.answer(f"Вопрос №1:\n{interview_data.get('text')}")


@router.message(F.document)
async def handle_resume_upload(message: types.Message, bot: Bot, api, state: FSMContext):
    if not message.document.file_name.endswith('.pdf'):
        return await message.answer("Пожалуйста, отправьте резюме в формате PDF 📄")

    status_msg = await message.answer("Загружаю резюме на сервер... ⏳")
    
    file = await bot.get_file(message.document.file_id)
    file_bytes = await bot.download_file(file.file_path)
    
    resume_id = await api.resume_upload(
        user_id=message.from_user.id,
        file_bytes=file_bytes.read(),
        file_name=message.document.file_name
    )

    if resume_id:
        await state.update_data(resume_id=resume_id)
        
        # Сразу предлагаем нажать кнопку после загрузки
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="🔥 Начать интервью сейчас", callback_data="start_interview"))
        
        await status_msg.edit_text(
            "✅ Резюме загружено и обработано! Можем начинать.",
            reply_markup=builder.as_markup()
        )
    else:
        await status_msg.edit_text("❌ Ошибка при загрузке. Проверь файл или нажми /start.")


@router.message(F.text == "🚀 Начать интервью")
async def cmd_start_interview(message: types.Message, state: FSMContext, api):
    # Просто вызываем ту же логику, что и в callback
    user_data = await state.get_data()
    resume_id = user_data.get("resume_id")

    if not resume_id:
        return await message.answer("Сначала загрузи резюме (PDF файл) 📄")

    interview_data = await api.start_interview(message.from_user.id, resume_id)
    if interview_data:
        await state.update_data(interview_id=interview_data.get("id"))
        await state.set_state(InterviewProcess.interviewing)
        await message.answer(f"Интервью началось!\n\nВопрос №1:\n{interview_data.get('text')}")


@router.message(InterviewProcess.interviewing)
async def handle_interview_answer(message: types.Message, state: FSMContext, api):
    user_data = await state.get_data()
    interview_id = user_data.get("interview_id")
    
    next_question = await api.send_message(
        user_id=message.from_user.id,
        answerText=message.text,
        interview_id=interview_id
    )
    
    await message.answer(next_question)

# Обработка любых сообщений и вывод в терминал
@router.message()
async def any_message(message: types.message):
    print(f"Получено сообщение от пользователя: {message.text}")
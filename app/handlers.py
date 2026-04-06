import datetime
from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatAction
from aiogram.utils.chat_action import ChatActionSender  

class InterviewProcess(StatesGroup):
    waiting_for_resume = State() 
    ready_to_start = State()    
    interviewing = State()
    choosing_interview = State()
    choosing_questions_count = State()

router = Router()

def get_main_menu(is_interviewing: bool = False):
    if is_interviewing:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⏸ Поставить на паузу")],
                [KeyboardButton(text="🏁 Завершить интервью")]
            ],
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 Начать интервью")],
            [KeyboardButton(text="📂 Мои резюме"), KeyboardButton(text="📊 Мои интервью")],
            [KeyboardButton(text="📊 Активные сессии"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

def format_date(iso_string):
    """Превращает системную дату бэкенда в красивый формат для пользователя"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return "Дата не указана"



async def list_resumes_with_buttons(message: types.Message, api, user_name: str):
    resumes = await api.get_resumes(message.from_user.id)
    
    if not resumes:
        return await message.answer(
            f"Привет, {user_name}! 👋\nУ вас пока нет загруженных резюме. Пришлите PDF файл!",
            reply_markup=get_main_menu()
        )

    builder = InlineKeyboardBuilder()
    text = f"Привет, {user_name}! 👋\n\n📂 **Ваши резюме:**\n\n"
    
    for i, res in enumerate(resumes, 1):
        res_name = res.get('filename') or res.get('name') or f"Файл №{i}"
        res_id = res.get('id')
        text += f"{i}. 📄 {res_name}\n"
        builder.button(text=f"Выбрать {i}", callback_data=f"set_active_res:{res_id}")
    
    builder.adjust(2)
    await message.answer(
        text + "\nНажмите на кнопку с номером, чтобы выбрать резюме для интервью или пришлите новое в формате PDF.",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )



@router.message(F.text == "📂 Мои резюме")
@router.message(Command("resumes"))
async def show_my_resumes(message: types.Message, api, state: FSMContext):
    await state.set_state(None)
    
    resumes = await api.get_resumes(message.from_user.id)
    
    if not resumes:
        return await message.answer(
            "Вы еще не загрузили ни одного резюме. 📄 Пришлите PDF файл!",
            reply_markup=get_main_menu()
        )

    builder = InlineKeyboardBuilder()
    text = "📂 **Ваши загруженные резюме:**\n\n"
    
    for i, res in enumerate(resumes, 1):
        res_name = res.get('filename') or res.get('name') or f"Файл №{i}"
        res_id = res.get('id')
        
        text += f"{i}. 📄 {res_name}\n"
        builder.button(text=f"Выбрать {i}", callback_data=f"set_active_res:{res_id}")
    
    builder.adjust(2)
    
    await message.answer(
        text + "\nНажмите на кнопку с номером, чтобы выбрать резюме для интервью или загрузите новое в формате PDF",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )



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


@router.callback_query(F.data.startswith("set_active_res:"))
async def handle_set_active_resume(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Резюме выбрано! ✅")
    resume_id = callback.data.split(":")[1]
    
    await state.update_data(resume_id=resume_id)
    
    await callback.message.edit_text(
        "✅ **Резюме успешно выбрано и активировано!**\n\n"
        "Теперь нажмите кнопку **'🚀 Начать интервью'** в меню ниже, чтобы приступить.",
        parse_mode="Markdown"
    )



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


@router.message(F.text == "🏁 Завершить интервью")
async def cmd_finish_interview(message: types.Message, api, state: FSMContext):
    user_data = await state.get_data()
    interview_id = user_data.get("interview_id")
    telegram_id = message.from_user.id
    
    if not interview_id:
        await state.clear()
        return await message.answer("❌ Активное интервью не найдено.", reply_markup=get_main_menu())


    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            result = await api.finish_interview(telegram_id, interview_id)

            
        except Exception as e:
            print(f"Ошибка при остановке: {e}")
            return await message.answer("⚠️ Произошла ошибка при сохранении результатов.")

    await state.clear()

    if result:
        score = result.get("totalScore", 0)
        feedback = result.get("feedback", "Анализ не доступен")
        
        text = (
            f"🏁 **Интервью завершено!**\n\n"
            f"📊 **Ваш итоговый результат:** `{score}` баллов\n\n"
            f"📝 **Подробный разбор:**\n{feedback}"
        )
        
        await message.answer(text, parse_mode="Markdown", reply_markup=get_main_menu(False))
        await state.clear()
    else:
        await message.answer("❌ Ошибка: Возможно, сессия уже закрыта или сервер недоступен.")


@router.callback_query(F.data.startswith("finish_"))
async def callback_finish_interview(callback: types.CallbackQuery, api, state: FSMContext):
    interview_id = callback.data.split("_")[1]
    result = await api.finish_interview(callback.from_user.id, interview_id)
    
    if result:
        score = result.get("totalScore", 0)
        feedback = result.get("feedback", "Анализ не доступен")
        text = f"🏁 **Итоги сессии:**\n\n⭐ Баллы: {score}\n\n{feedback}"
        await callback.message.answer(text, parse_mode="Markdown")
    
    await callback.answer()



@router.message(F.text == "📊 Активные сессии")
@router.message(Command("active"))
async def show_active_interviews(message: types.Message, api, state: FSMContext):
    await state.set_state(None) 
    
    interviews = await api.get_active_interviews(message.from_user.id)
    if not interviews:
        return await message.answer("У вас нет активных сессий. 🚀")

    builder = InlineKeyboardBuilder()
    text = "⚡️ **Ваши активные сессии:**\n\n"
    
    for i, inter in enumerate(interviews, 1):
        i_id = inter.get('id')
        raw_date = inter.get('created_at') or inter.get('start_time')
        date_label = format_date(raw_date) if raw_date else f"ID: {i_id[:8]}"
        
        text += f"{i}. 🗓 {date_label} (🆔 `{i_id[:8]}`)\n"
        builder.button(text=f"{i}", callback_data=f"sel_int:{i_id}")
    
    builder.adjust(5)
    text += "\nВыберите номер сессии, чтобы продолжить."
    
    await message.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("sel_int:"))
async def ask_context_level(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    interview_id = callback.data.split(":")[1]
    await state.update_data(interview_id=interview_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="❓ Последний вопрос", callback_data=f"ctx:last:{interview_id}")
    builder.button(text="📜 Вся история", callback_data=f"ctx:full:{interview_id}")
    builder.adjust(1)

    await callback.message.edit_text(
        f"🔄 Выбрана сессия `{interview_id[:8]}`.\nЧто вывести перед началом?",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("ctx:"))
async def resume_with_context(callback: types.CallbackQuery, api, state: FSMContext):
    await callback.answer()
    
    _, mode, i_id = callback.data.split(":")
    history = await api.get_interview_history(callback.from_user.id, i_id)
    
    if not history:
        text = "История пока пуста. Можно продолжать!"
    elif mode == "last":
        last_obj = history[-1]
        icon = "🤖" if last_obj.get('role') == 'assistant' or last_obj.get('sender') == 'bot' else "👤"
        last_msg = last_obj.get('content') or last_obj.get('text') or "Вопрос не найден"
        text = f"📌 **Последний вопрос был ({icon}):**\n\n_{last_msg}_"
    else:
        text = "📜 **Последние сообщения:**\n\n"
        for msg in history[-5:]:
            sender = msg.get('sender')
            role = msg.get('role')
            
            if sender == 'bot' or role == 'assistant' or msg.get('is_bot') is True:
                icon = "🤖"
            else:
                icon = "👤"
            
            content = msg.get('content') or msg.get('text') or "..."
            text += f"{icon}: {content}\n\n"
            text += "────────────────────\n"

    await state.set_state(InterviewProcess.interviewing)
    await state.update_data(interview_id=i_id)
    
    await callback.message.delete()
    await callback.message.answer(
        f"{text}\n\n**Интервью возобновлено. Жду ваш ответ!**",
        parse_mode="Markdown",
        reply_markup=get_main_menu(is_interviewing=True))



@router.message(F.text == "📂 Мои резюме")
@router.message(Command("resumes"))
async def show_my_resumes(message: types.Message, api, state: FSMContext):
    await state.set_state(None)
    
    resumes = await api.get_resumes(message.from_user.id)
    
    if not resumes:
        return await message.answer(
            "Вы еще не загрузили ни одного резюме. 📄 Пришлите PDF файл!",
            reply_markup=get_main_menu()
        )

    builder = InlineKeyboardBuilder()
    text = "📂 **Ваши загруженные резюме:**\n\n"
    
    for i, res in enumerate(resumes, 1):
        res_name = res.get('filename') or res.get('name') or f"Файл №{i}"
        res_id = res.get('id')
        
        text += f"{i}. 📄 {res_name}\n"
        builder.button(text=f"Выбрать {i}", callback_data=f"set_active_res:{res_id}")
    
    builder.adjust(2)
    
    await message.answer(
        text + "\nНажмите на кнопку с номером, чтобы выбрать резюме для интервью.",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


@router.message(F.text == "📊 Мои интервью")
@router.message(Command("completed"))
async def show_completed_interviews(event: types.Message | types.CallbackQuery, api, state: FSMContext):
    await state.set_state(None)
    
    user_id = event.from_user.id
    
    interviews = await api.get_completed_interview_details(user_id)
    
    if not interviews:
        text = "У вас пока нет завершенных интервью. 📑"
        if isinstance(event, types.CallbackQuery):
            return await event.message.answer(text)
        return await event.answer(text)

    builder = InlineKeyboardBuilder()
    text = "📋 **Завершенные интервью:**\n\n"
    
    for i, inter in enumerate(interviews, 1):
        i_id = inter.get('id')
        created_at = inter.get('created_at') or inter.get('start_time')
        score = inter.get('total_score', 0)
        
        date_str = format_date(created_at) if created_at else f"ID: {i_id[:8]}"
        text += f"{i}. 🗓 {date_str} — ⭐ **{score}** (🆔 `{i_id[:8]}`)\n"
        builder.button(text=f"{i}", callback_data=f"view_archive:{i_id}")
        
    builder.adjust(5)
    text += "\nНажмите на номер, чтобы посмотреть подробный фидбэк."
    
    if isinstance(event, types.Message):
        await event.answer(text, parse_mode="Markdown", reply_markup=builder.as_markup())
    else:
        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("view_archive:"))
async def handle_view_archive(callback: types.CallbackQuery, api):
    interview_id = callback.data.split(":")[1]
    await callback.answer("Загружаю подробности...")
    
    interviews = await api.get_completed_interview_details(callback.from_user.id)
    interview = next((i for i in interviews if i.get('id') == interview_id), None)
    
    if not interview:
        return await callback.message.answer("❌ Данные интервью не найдены.")

    history = await api.get_interview_history(callback.from_user.id, interview_id)
    
    ai_messages = [m for m in history if m.get('role') == 'assistant' or m.get('sender') == 'bot']
    feedback = ai_messages[-1].get('content') or ai_messages[-1].get('text') if ai_messages else "Разбор не найден в истории."

    score = interview.get('total_score', 0)
    raw_date = interview.get('created_at') or interview.get('start_time')
    date_str = format_date(raw_date)

    text = (
        f"📜 **Отчет по интервью**\n"
        f"🗓 Дата: `{date_str}`\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 **Ваш результат:** `{score}` баллов\n\n"
        f"📝 **Полный разбор:**\n\n{feedback}"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📜 Посмотреть историю и фидбэк", callback_data=f"arch_history:{interview_id}")
    builder.button(text="⬅️ К списку интервью", callback_data="back_to_completed_list")
    builder.adjust(1)

    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("arch_history:"))
async def handle_show_history(callback: types.CallbackQuery, api):
    interview_id = callback.data.split(":")[1]
    await callback.answer()

    history = await api.get_interview_history(callback.from_user.id, interview_id)
    
    if not history:
        return await callback.message.answer("История переписки пуста.")

    text = (
        f"📖 **ПОЛНЫЙ ПРОТОКОЛ ИНТЕРВЬЮ**\n"
        f"🆔 `ID: {interview_id[:8]}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    for msg in history:
        sender = msg.get('sender')
        role = msg.get('role')
        is_ai = sender == 'bot' or role == 'assistant' or msg.get('is_bot') is True
        
        icon = "🤖" if is_ai else "👤"
        author = "ИНТЕРВЬЮЕР (AI)" if is_ai else "ВАШ ОТВЕТ"
        content = msg.get('content') or msg.get('text') or "..."
        
        text += f"{icon} **{author}**\n{content}\n"
        text += f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n" 

    if len(text) > 4000:
        text = text[:4000] + "\n\n⚠️ *Часть истории скрыта из-за лимитов Telegram...*"

    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Вернуться к результатам", callback_data=f"view_archive:{interview_id}")
    builder.button(text="📂 К списку всех интервью", callback_data="back_to_completed_list")
    builder.adjust(1)
    
    await callback.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "back_to_completed_list")
async def process_back_to_completed(callback: types.CallbackQuery, api, state: FSMContext):
    await callback.answer()
    await show_completed_interviews(callback, api, state)


@router.message(F.document)
async def handle_resume_upload(message: types.Message, bot: Bot, api, state: FSMContext):
    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)

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
        await state.set_state(InterviewProcess.choosing_questions_count)
        
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="5"), KeyboardButton(text="10")],
                [KeyboardButton(text="15"), KeyboardButton(text="20")]
            ],
            resize_keyboard=True
        )
        await status_msg.delete() 
        await message.answer("✅ Резюме принято! Сколько вопросов задать тебе на интервью?", reply_markup=kb)



@router.message(InterviewProcess.choosing_questions_count)
async def process_questions_count(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Пожалуйста, введи число цифрами.")
    
    count = int(message.text)
    await state.update_data(questions_count=count)
    await state.set_state(None)
    
    await message.answer(
        f"Отлично! Настроено вопросов: {count}.\n"
        f"(Внимание: на данный момент доступно максимум 5 вопросов)\n"
        "Теперь нажми кнопку '🚀 Начать интервью'",
        reply_markup=get_main_menu(False) 
    )



@router.message(InterviewProcess.interviewing, F.text)
async def handle_interview_answer(message: types.Message, state: FSMContext, api):
    forbidden_commands = ["🚀 Начать интервью", "📂 Мои резюме", "📊 Мои интервью", "📊 Активные сессии", "❓ Помощь"]
    if message.text in forbidden_commands:
        return await message.answer("⚠️ Сначала завершите текущее интервью.")

    user_data = await state.get_data()
    interview_id = user_data.get("interview_id")
    answer_count = user_data.get("answer_count", 0)
    total_questions = 5

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            response = await api.send_message(
                user_id=message.from_user.id,
                answerText=message.text,
                interview_id=interview_id
            )
        except Exception as e:
            print(f"Ошибка API: {e}")
            return await message.answer("❌ Ошибка связи с сервером.")

    if not response:
        return await message.answer("❌ Ошибка связи с сервером.")

    if "score" in response:
        score = response.get("score", 0)
        feedback = response.get("feedback", "Разбор завершен.")
        
        await message.answer(
            f"✅ Интервью завершено!\n\n"
            f"📊 Итоговый балл: {score}\n\n"
            f"📝 Разбор: {feedback}",
            parse_mode="Markdown",
            reply_markup=get_main_menu(False)
        )
        await state.clear()
        return

    new_count = answer_count + 1
    await state.update_data(answer_count=new_count)
    
    display_number = new_count + 1
    
    question_text = response.get("reply")

    if question_text:
        await message.answer(
            f"**Вопрос {display_number} из {total_questions}:**\n\n{question_text}",
            parse_mode="Markdown"
        )
    else:
        await message.answer("🔄 Обработка ответа, подождите...")


@router.message(F.text == "🚀 Начать интервью")
async def cmd_prepare_interview(message: types.Message, state: FSMContext, api):
    user_data = await state.get_data()
    resume_id = user_data.get("resume_id")

    if not resume_id:
        return await message.answer(
            "⚠️ **Резюме не выбрано.**\n"
            "Сначала выберите резюме в разделе '📂 Мои резюме' или пришлите новый PDF файл.",
            parse_mode="Markdown"
        )


    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        interview_data = await api.start_interview(message.from_user.id, resume_id)
    
    if interview_data and interview_data.get("id"):
        await state.set_state(InterviewProcess.interviewing)
        await state.update_data(
            interview_id=interview_data.get("id"),
            answer_count=0
        )
        
        await message.answer(
            f"🚀 **Интервью началось!**\n\n"
            f"**Вопрос 1 из 5:**\n\n{interview_data.get('text')}",
            parse_mode="Markdown",
            reply_markup=get_main_menu(is_interviewing=True)
        )
    else:
        await message.answer("❌ Ошибка при создании сессии. Проверьте соединение с сервером.")

async def start_actual_interview(message, state, api, resume_id):
    data = await state.get_data()
    q_count = data.get("questions_count", 5)
    
    interview_data = await api.start_interview(message.from_user.id, resume_id)
    if interview_data:
        await state.update_data(interview_id=interview_data.get("id"))
        await state.set_state(InterviewProcess.interviewing)
        await message.answer(
            f"🚀 **Интервью началось!**\n\n{interview_data.get('text')}",
            parse_mode="Markdown",
            reply_markup=get_main_menu(is_interviewing=True)
        )


@router.callback_query(F.data.startswith("start_with_res:"))
async def handle_resume_choice(callback: types.CallbackQuery, state: FSMContext, api):
    await callback.answer()
    resume_id = callback.data.split(":")[1]
    await callback.message.delete()
    await start_actual_interview(callback.message, state, api, resume_id)



@router.message()
async def any_message(message: types.Message):
    print(f"Получено сообщение: {message.text}")
    await message.answer("Я не понимаю эту команду. Воспользуйтесь меню.", reply_markup=get_main_menu())
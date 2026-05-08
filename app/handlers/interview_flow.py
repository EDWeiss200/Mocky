import tempfile
import os
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.chat_action import ChatActionSender
from states import InterviewProcess, INTERVIEW_ROLES, get_main_menu
from utils import convert_ogg_to_mp3

router = Router()

@router.callback_query(F.data.startswith("set_active_res:"))
async def handle_set_active_resume(callback: types.CallbackQuery, state: FSMContext):
    resume_id = callback.data.split(":")[1]
    
    await state.update_data(resume_id=resume_id, questions_count=None, role=None)
    await state.set_state(InterviewProcess.choosing_questions_count)
    
    builder = InlineKeyboardBuilder()
    for count in ["5", "10", "15", "20"]:
        builder.button(text=f"{count} вопросов", callback_data=f"set_q_count:{count}")
    builder.adjust(1)

    await callback.answer()
    await callback.message.edit_text(
        "✅ <b>Резюме выбрано!</b>\n\n" 
        "Сколько вопросов задать тебе на интервью?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_q_count:"))
async def process_questions_count_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    try:
        count_str = callback.data.split(":")[1]
        count = int(count_str)
    except (IndexError, ValueError):
        return await callback.message.answer("Ошибка при выборе количества.")

    await state.update_data(questions_count=count)
    await state.set_state(InterviewProcess.choosing_role)
    
    builder = InlineKeyboardBuilder()
    for role_key, role_name in INTERVIEW_ROLES.items():
        builder.button(text=role_name, callback_data=f"set_role:{role_key}")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"⚙️ <b>Количество выбрано:</b> <code>{count}</code>\n\n"
        "Теперь выберите роль интервьюера:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("set_role:"))
async def process_role_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    try:
        chosen_role = callback.data.split(":")[1]
    except IndexError:
        return await callback.message.answer("Ошибка при выборе роли.")

    await state.update_data(role=chosen_role)
    await state.set_state(None)
    
    role_name = INTERVIEW_ROLES.get(chosen_role, chosen_role)
    await callback.message.edit_text(
        f"🎭 <b>Роль выбрана:</b> {role_name}\n\n"
        "Всё готово! Теперь нажмите кнопку <b>'🚀 Начать интервью'</b> в нижнем меню.",
        parse_mode="HTML"
    )

ALLOWED_QUESTION_COUNTS = {5, 10, 15, 20}

@router.message(InterviewProcess.choosing_questions_count)
async def process_questions_count(message: types.Message, state: FSMContext):
    if message.text == "🚀 Начать интервью":
        return await message.answer("⚠️ Сначала укажите количество вопросов, выбрав из списка.")
    if not message.text or not message.text.isdigit():
        return await message.answer("⚠️ Пожалуйста, выберите количество вопросов из кнопок выше: 5, 10, 15 или 20.")

    count = int(message.text)
    if count not in ALLOWED_QUESTION_COUNTS:
        return await message.answer(
            "⚠️ Допустимые значения: <b>5, 10, 15, 20</b>.\n"
            "Пожалуйста, выберите одно из них.",
            parse_mode="HTML"
        )

    await state.update_data(questions_count=count)
    await state.set_state(InterviewProcess.choosing_role)
    
    builder = InlineKeyboardBuilder()
    for role_key, role_name in INTERVIEW_ROLES.items():
        builder.button(text=role_name, callback_data=f"set_role:{role_key}")
    builder.adjust(1)
    
    await message.answer(
        f"Отлично! Настроено вопросов: {count}.\n"
        "Теперь выберите роль интервьюера:",
        reply_markup=builder.as_markup()
    )


@router.message(F.text == "🚀 Начать интервью")
async def cmd_prepare_interview(message: types.Message, state: FSMContext, api):
    user_data = await state.get_data()
    resume_id = user_data.get("resume_id")
    
    q_count = user_data.get("questions_count")
    role = user_data.get("role")

    if not resume_id:
        return await message.answer(
            "⚠️ <b>Резюме не выбрано.</b>\n"
            "Сначала выберите резюме в разделе «📂 Мои резюме» или пришлите новый PDF файл.",
            parse_mode="HTML"
        )

    if not q_count:
        await state.set_state(InterviewProcess.choosing_questions_count)
        builder = InlineKeyboardBuilder()
        for count in ["5", "10", "15", "20"]:
            builder.button(text=f"{count} вопросов", callback_data=f"set_q_count:{count}")
        builder.adjust(1)
        
        return await message.answer(
            "⚙️ Вы выбрали резюме, но не настроили параметры.\n\n"
            "<b>Сколько вопросов задать тебе на интервью?</b>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

    if not role:
        await state.set_state(InterviewProcess.choosing_role)
        builder = InlineKeyboardBuilder()
        for role_key, role_name in INTERVIEW_ROLES.items():
            builder.button(text=role_name, callback_data=f"set_role:{role_key}")
        builder.adjust(1)
        
        return await message.answer(
            f"⚙️ Вопросов: <b>{q_count}</b>.\n\n"
            "<b>Теперь выберите роль интервьюера:</b>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        try:
            interview_data = await api.start_interview(message.from_user.id, resume_id, q_count, role)
        except Exception:
            return await message.answer("❌ <b>Ошибка связи с сервером.</b> Попробуйте позже.", parse_mode="HTML")
    
    if interview_data:
        if isinstance(interview_data, dict) and interview_data.get("error") == "payment_required":
            return await message.answer(
                "⚠️ <b>Недостаточно попыток!</b>\n\n"
                "На вашем аккаунте закончились бесплатные интервью. "
                "Пожалуйста, пополните баланс.",
                parse_mode="HTML"
            )
        
        if interview_data.get("id"):
            await state.set_state(InterviewProcess.interviewing)
            await state.update_data(
                interview_id=interview_data.get("id"),
                answer_count=0
            )
            
            await message.answer(
                f"🚀 <b>Интервью началось!</b>\n\n"
                f"<b>Вопрос 1 из {q_count}:</b>\n\n{interview_data.get('text')}",
                parse_mode="HTML",
                reply_markup=get_main_menu(is_interviewing=True)
            )
            return
            
    await message.answer("❌ Ошибка при создании сессии. Проверьте соединение с сервером.", parse_mode="HTML")

async def start_actual_interview(message, state, api, resume_id):
    data = await state.get_data()
    q_count = data.get("questions_count")
    role = data.get("role")
    
    if not resume_id:
        return await message.answer(
            "⚠️ **Резюме не выбрано.**\n\nСначала выберите резюме в разделе '📂 Мои резюме' или пришлите новый PDF файл.",
            parse_mode="Markdown",
        )
    if q_count is None:
        return await message.answer(
            "⚠️ **Не указано количество вопросов.**\n\nСначала выберите количество вопросов.",
            parse_mode="Markdown",
        )
    if role is None:
        return await message.answer(
            "⚠️ **Не выбрана роль интервьюера.**\n\nСначала выберите роль интервьюера.",
            parse_mode="Markdown",
        )
    allowed_counts = {5, 10, 15, 20}
    if not isinstance(q_count, int) or q_count not in allowed_counts:
        return await message.answer(
            "⚠️ **Некорректное количество вопросов.**\n\nВыберите количество вопросов из предложенных вариантов.",
            parse_mode="Markdown",
        )
    if role not in INTERVIEW_ROLES:
        return await message.answer(
            "⚠️ **Некорректный тип интервьюера.**\n\nВыберите роль интервьюера из списка.",
            parse_mode="Markdown",
        )
    
    interview_data = await api.start_interview(message.from_user.id, resume_id, q_count, role)
    if interview_data:
        if isinstance(interview_data, dict) and interview_data.get("error") == "payment_required":
            return await message.answer(
                "⚠️ **Недостаточно токенов!**\n\n"
                "На вашем аккаунте закончились токены. Пожалуйста, пополните баланс на сайте.",
                parse_mode="Markdown"
            )
            
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



@router.message(InterviewProcess.interviewing, F.text)
async def handle_interview_answer(message: types.Message, state: FSMContext, api):
    forbidden_commands = [
        "🚀 Начать интервью", "📂 Мои резюме", "📊 Мои интервью", 
        "📊 Активные сессии", "❓ Помощь", "⏸ Поставить на паузу"
    ]
    
    if message.text in forbidden_commands:
        if message.text == "⏸ Поставить на паузу":
            await state.set_state(None) 
            return await message.answer(
                "⏸ <b>Интервью приостановлено.</b>\n\n"
                "Вы вернулись в главное меню. Чтобы продолжить, выберите эту сессию в разделе «📊 Активные сессии».",
                parse_mode="HTML",
                reply_markup=get_main_menu(is_interviewing=False)
            )
        else:
            return await message.answer("⚠️ Сначала завершите или приостановите текущее интервью.")

    user_data = await state.get_data()
    interview_id = user_data.get("interview_id")
    answer_count = user_data.get("answer_count", 0)
    total_questions = user_data.get("questions_count", 5)

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

    if isinstance(response, dict) and response.get("error") == "payment_required":
        await state.set_state(None)
        return await message.answer(
            "⚠️ **Лимит токенов исчерпан.**\n\n"
            "К сожалению, интервью прервано, так как у вас закончились токены. "
            "Пожалуйста, пополните баланс.",
            parse_mode="Markdown",
            reply_markup=get_main_menu(False)
        )

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
            f"<b>Вопрос {display_number} из {total_questions}:</b>\n\n{question_text}",
            parse_mode="HTML"
        )
    else:
        await message.answer("🔄 Обработка ответа, подождите...", parse_mode="HTML")

@router.message(InterviewProcess.interviewing, F.voice)
async def handle_voice_message(message: types.Message, state: FSMContext, api):
    user_data = await state.get_data()
    interview_id = user_data.get("interview_id")
    answer_count = user_data.get("answer_count", 0)
    total_questions = user_data.get("questions_count", 5)

    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
        file = await message.bot.get_file(message.voice.file_id)
        file_bytes = await message.bot.download_file(file.file_path)
        
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_file:
            ogg_file.write(file_bytes.read())
            ogg_path = ogg_file.name
        mp3_path = await convert_ogg_to_mp3(ogg_path)
        
        if not mp3_path:
            os.unlink(ogg_path)
            return await message.answer("❌ Ошибка при конвертации аудио.")

        with open(mp3_path, "rb") as f:
            mp3_bytes = f.read()

        try:
            response = await api.answer_voice(
                user_id=message.from_user.id,
                file_bytes=mp3_bytes,
                file_name="voice.mp3",
                interview_id=interview_id
            )
        except Exception as e:
            print(f"Ошибка API при отправке голосового: {e}")
            response = None
        finally:
            os.unlink(ogg_path)
            if os.path.exists(mp3_path):
                os.unlink(mp3_path)

    if not response:
        return await message.answer("❌ Ошибка связи с сервером.")

    if isinstance(response, dict) and response.get("error") == "payment_required":
        await state.set_state(None)
        return await message.answer(
            "⚠️ **Лимит токенов исчерпан.**\n\n"
            "К сожалению, интервью прервано, так как у вас закончились токены. "
            "Пожалуйста, пополните баланс.",
            parse_mode="Markdown",
            reply_markup=get_main_menu(False)
        )

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
            f"<b>Вопрос {display_number} из {total_questions}:</b>\n\n{question_text}",
            parse_mode="HTML"
        )
    else:
        await message.answer("🔄 Обработка ответа, подождите...", parse_mode="HTML")

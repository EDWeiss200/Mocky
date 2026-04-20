from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatAction
from states import get_main_menu

router = Router()


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
        builder.row(
            types.InlineKeyboardButton(text=f"Выбрать {i}", callback_data=f"set_active_res:{res_id}"),
            types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_res:{res_id}")
        )
    
    await message.answer(
        text + "\n💡 **Чтобы добавить новое резюме**, просто отправьте мне PDF-файл в этот чат.",
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
        builder.row(
            types.InlineKeyboardButton(text=f"{i}", callback_data=f"set_active_res:{res_id}"),
            types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_res:{res_id}")
        )
    
    await message.answer(
        text + "\n💡 **Чтобы добавить новое резюме**, просто отправьте мне PDF-файл в этот чат.",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )


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
        await state.set_state(None) 
        
        await status_msg.delete() 
        await message.answer(
            "✅ **Резюме успешно загружено!**\n\n",
            reply_markup=get_main_menu(False),
            parse_mode="Markdown"
        )


@router.message(F.text == "📄 Анализ резюме")
async def show_resumes_for_analysis(message: types.Message, api, state: FSMContext):
    await state.set_state(None)
    
    resumes = await api.get_resumes(message.from_user.id)
    
    if not resumes:
        return await message.answer(
            "Вы еще не загрузили ни одного резюме. 📄 Пришлите PDF файл!",
            reply_markup=get_main_menu()
        )

    builder = InlineKeyboardBuilder()
    text = "🔍 **Выберите резюме для анализа:**\n\n"
    
    for i, res in enumerate(resumes, 1):
        res_name = res.get('filename') or res.get('name') or f"Файл №{i}"
        res_id = res.get('id')
        
        text += f"{i}. 📄 {res_name}\n"
        builder.row(
            types.InlineKeyboardButton(text=f"Анализ {i}", callback_data=f"analyze_res:{res_id}"),
            types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_res:{res_id}")
        )
    
    await message.answer(
        text + "\nНажмите на кнопку с номером, чтобы получить детальный разбор.",
        parse_mode="Markdown",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("del_res:"))
async def process_delete_resume(callback: types.CallbackQuery, api):
    resume_id = callback.data.split(":")[1]
    
    success = await api.delete_resume(callback.from_user.id, resume_id)
    if success:
        await callback.answer("✅ Резюме удалено!", show_alert=True)
        await callback.message.delete()
    else:
        await callback.answer("❌ Ошибка при удалении.", show_alert=True)


@router.callback_query(F.data.startswith("analyze_res:"))
async def process_resume_analysis(callback: types.CallbackQuery, api):
    resume_id = callback.data.split(":")[1]
    
    await callback.message.edit_text("⏳ Анализирую резюме, это может занять пару минут...", parse_mode="Markdown")
    
    analysis = await api.analyze_resume(callback.from_user.id, resume_id)
    
    if not analysis:
        return await callback.message.edit_text("❌ Не удалось проанализировать резюме. Попробуйте еще раз позже.")
        
    if isinstance(analysis, dict) and analysis.get("error") == "payment_required":
        return await callback.message.edit_text(
            "⚠️ **Недостаточно токенов.**\n\n"
            "На вашем аккаунте закончились токены для анализа резюме. "
            "Пожалуйста, пополните баланс в личном кабинете на сайте.",
            parse_mode="Markdown"
        )
        
    grade = analysis.get("estimated_grade", "Не определено")
    demand = analysis.get("market_demand_score", 0)
    strong = analysis.get("strong_points", [])
    red_flags = analysis.get("red_flags", [])
    recommendations = analysis.get("recommendations", [])
    
    strong_text = "\n".join([f"• {p}" for p in strong]) if strong else "Нет данных"
    flags_text = "\n".join([f"• {p}" for p in red_flags]) if red_flags else "Серьезных проблем не найдено"
    recs_text = "\n".join([f"• {p}" for p in recommendations]) if recommendations else "Нет рекомендаций"
    
    result_text = (
        f"📊 **Анализ резюме**\n\n"
        f"⭐ **Примерный грейд:** {grade}\n"
        f"🔥 **Востребованность на рынке:** {demand}/10\n\n"
        f"✅ **Сильные стороны:**\n{strong_text}\n\n"
        f"🚩 **Зоны риска / Красные флаги:**\n{flags_text}\n\n"
        f"💡 **Рекомендации:**\n{recs_text}"
    )
    
    if len(result_text) > 4000:
        result_text = result_text[:4000] + "...\n(текст обрезан)"
        
    await callback.message.edit_text(result_text, parse_mode="Markdown")

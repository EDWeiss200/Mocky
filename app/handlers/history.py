from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.chat_action import ChatActionSender
from states import InterviewProcess, get_main_menu, format_date

router = Router()

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
        builder.row(
            types.InlineKeyboardButton(text=f"Продолжить {i}", callback_data=f"sel_int:{i_id}"),
            types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_int:{i_id}")
        )
    
    text += "\nВыберите сессию, чтобы продолжить или удалить."
    
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
            text += f"{icon}: {content}\n"
            text += "────────────────────\n"

    await state.set_state(InterviewProcess.interviewing)
    await state.update_data(interview_id=i_id)
    
    await callback.message.delete()
    await callback.message.answer(
        f"{text}\n**Интервью возобновлено. Жду ваш ответ!**",
        parse_mode="Markdown",
        reply_markup=get_main_menu(is_interviewing=True)
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
        builder.row(
            types.InlineKeyboardButton(text=f"Посмотреть {i}", callback_data=f"view_archive:{i_id}"),
            types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_int:{i_id}")
        )
        
    text += "\nНажмите на кнопку, чтобы посмотреть фидбэк или удалить запись."
    
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
        text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n" 

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


@router.callback_query(F.data.startswith("del_int:"))
async def process_delete_interview(callback: types.CallbackQuery, api):
    interview_id = callback.data.split(":")[1]
    
    success = await api.delete_interview(callback.from_user.id, interview_id)
    if success:
        await callback.answer("✅ Сессия удалена!", show_alert=True)
        await callback.message.delete()
    else:
        await callback.answer("❌ Ошибка при удалении.", show_alert=True)

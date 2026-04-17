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
        text + "\nНажмите на кнопку с номером, чтобы выбрать резюме для интервью.",
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

import datetime
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

class InterviewProcess(StatesGroup):
    waiting_for_resume = State() 
    ready_to_start = State()    
    interviewing = State()
    choosing_interview = State()
    choosing_questions_count = State()
    choosing_role = State()

INTERVIEW_ROLES = {
    "strict_senior": "🕵️ Суровый Senior",
    "pragmatic_lead": "👨‍💻 Прагматичный Tech Lead",
    "friendly_hr": "🤗 Поддерживающий HR"
}

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
            [KeyboardButton(text="📊 Активные сессии"), KeyboardButton(text="📄 Анализ резюме")],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )

def format_date(iso_string):
    """Превращает системную дату бэкенда в красивый формат для пользователя"""
    try:
        dt = datetime.datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return "Дата не указана"

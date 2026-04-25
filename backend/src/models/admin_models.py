from sqladmin import ModelView
from models.models import User, Interview, Resume

class UserAdmin(ModelView, model=User):
    column_list = "__all__"
    column_searchable_list = [User.id, User.email, User.telegram_id, User.balance, User.subscription_tier]
    icon = "fa-solid fa-user"
    name = "Пользователь"
    name_plural = "Пользователи"

class InterviewAdmin(ModelView, model=Interview):
    column_list = [Interview.id, Interview.user_id, Interview.resume, Interview.number_question,Interview.total_score]
    icon = "fa-solid fa-database"
    name = "Интервью"
    name_plural = "Интервью"

class ResumeAdmin(ModelView, model=Resume):
    column_list =[Resume.id, Resume.user_id, Resume.name]
    icon = "fa-solid fa-database"
    name = "Резюме"
    name_plural = "Резюме"


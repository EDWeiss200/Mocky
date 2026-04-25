from sqladmin import ModelView
from models.models import User, Interview, Resume

class UserAdmin(ModelView, model=User):
    column_list = "__all__"
    column_searchable_list = [User.email]
    icon = "fa-solid fa-user"
    name = "Пользователь"
    name_plural = "Пользователи"

class InterviewAdmin(ModelView, model=Interview):
    column_list = "__all__"
    icon = "fa-solid fa-database"
    name = "Интервью"
    name_plural = "Интервью"

class ResumeAdmin(ModelView, model=Resume):
    column_list = "__all__"
    icon = "fa-solid fa-database"
    name = "Резюме"
    name_plural = "Резюме"


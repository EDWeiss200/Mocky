from utils.repository import SQLAlchemyRepository

from models.models import Resume

class ResumeRepository(SQLAlchemyRepository):

    model = Resume
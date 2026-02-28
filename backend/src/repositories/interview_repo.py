from utils.repository import SQLAlchemyRepository

from models.models import Interview

class InterviewRepository(SQLAlchemyRepository):

    model = Interview
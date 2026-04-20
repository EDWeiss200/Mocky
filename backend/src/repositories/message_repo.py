from utils.repository import SQLAlchemyRepository

from models.models import Message

class MessageRepository(SQLAlchemyRepository):

    model = Message
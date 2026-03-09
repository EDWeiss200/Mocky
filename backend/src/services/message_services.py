from utils.repository import AbstractRepository
from schemas.schemas import MessageCreate


class MessageServices:

    def __init__(self,message_repo: AbstractRepository) -> None:
        self.message_repo = message_repo()

    async def add_message(self,interview_id,message_role,content):

        message = MessageCreate(
            interview_id=interview_id,
            role=message_role,
            content=content
        )

        message = message.model_dump()

        message_id = await self.message_repo.add_one(message)

        return message_id
    
    async def get_messages_inteview(self,interview_id):

        filters = [
            self.message_repo.model.interview_id == interview_id
        ]

        messages = await self.message_repo.find_filter(filters)

        return messages
    
    async def get_interview_history(self, interview_id: int):

        filters = [
            self.message_repo.model.interview_id == interview_id
        ]
        
        messages = await self.message_repo.find_filter(filters) 
        return messages
    
        
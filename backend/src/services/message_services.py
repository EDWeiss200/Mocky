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

        
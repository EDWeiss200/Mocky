from utils.repository import AbstractRepository


class UserServices:

    def __init__(self,user_repo: AbstractRepository) -> None:
        self.user_repo = user_repo()

    async def get_user_by_id(self,user_id):

        filters = [
            self.user_repo.model.id == user_id
        ]

        user = await self.user_repo.find_filter(filters)

        

        return user

        

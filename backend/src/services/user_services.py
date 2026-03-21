from utils.repository import AbstractRepository


class UserServices:

    def __init__(self,user_repo: AbstractRepository) -> None:
        self.user_repo = user_repo()

    async def get_user_by_id(self,user_id):

        filters = [
            self.user_repo.model.id == user_id
        ]

        user = await self.user_repo.find_filter_drm(filters)

        

        return user
    

    async def get_user_by_tgid(self,telegram_id):

        filters = [
            self.user_repo.model.telegram_id == telegram_id
        ]

        user = await self.user_repo.find_filter_drm(filters)

        return user
    


    async def update_telegram_id(self,user_id,telegram_id):

        data_to_update = {
            "telegram_id": telegram_id,
        }

        user = await self.user_repo.update(user_id,data_to_update)





        

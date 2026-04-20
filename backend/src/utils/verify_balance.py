from models.enum import Feature, FEATURE_COSTS
from fastapi import HTTPException, Depends
from datetime import datetime, timezone
from models.models import User
from auth.auth import current_user

class VerifyBalance:

    def __init__(self, feature: Feature):
        self.feature = feature

    async def __call__(self,user: User = Depends(current_user)):

        now = datetime.now(timezone.utc)
        has_sprint = user.subscription_tier == "sprint" and user.subscription_expires_at and user.subscription_expires_at.replace(tzinfo=timezone.utc) > now
        has_pro = user.subscription_tier == "pro" and user.subscription_expires_at and user.subscription_expires_at.replace(tzinfo=timezone.utc) > now

        if has_pro:
            return user
        

        if has_sprint:

            if self.feature in [Feature.RESUME_ANALYZE, Feature.GAP_ANALYZE, Feature.INTERVIEW_TEXT]:
                return user
            
            if self.feature == Feature.INTERVIEW_VOICE:
                if user.sprint_voice_used < 50:
                    return user
                else:
                    raise HTTPException(status_code=403, detail="Лимит голосовых сообщений (50) на тарифе Спринт исчерпан")
                
        cost = FEATURE_COSTS.get(self.feature, 0)

        if user.balance >= cost:
            return user
        
        raise HTTPException(status_code=402, detail=f"Недостаточно токенов. Нужно: {cost}")

from services.interview_services import InterviewServices
from services.resume_services import ResumeServices
from services.message_services import MessageServices
from models.models import User,Resume,MessageRole
from schemas.schemas import UserReadSchema, StartInterviewRequest, AnswerRequest, SessionStatus
from api.dependencies import interview_service
from api.dependencies import resume_service
from api.dependencies import message_service
from auth.auth import current_user
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException




router = APIRouter(
    tags=['message'],
    prefix='/messages'
)

@router.get("/{interview_id}/history")
async def get_interview_messages(
    interview_id: int,
    user: User = Depends(current_user),
    message_service: MessageServices = Depends(message_service),
    interview_service: InterviewServices = Depends(interview_service)
):
    
    interview = await interview_service.get_interview(interview_id)
    if not interview or interview.user_id!=user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")

    messages = await message_service.get_messages_inteview(interview_id)

    return messages
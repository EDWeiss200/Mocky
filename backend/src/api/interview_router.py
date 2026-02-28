from services.interview_services import InterviewServices
from services.resume_services import ResumeServices
from services.message_services import MessageServices
from models.models import User,Resume,MessageRole
from schemas.schemas import UserReadSchema, StartInterviewRequest
from api.dependencies import interview_service
from api.dependencies import resume_service
from api.dependencies import message_service
from auth.auth import current_user
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException




router = APIRouter(
    tags=['interview'],
    prefix='/interviews'
)

@router.post('start')
async def start_interview(
    req: StartInterviewRequest,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service)
    
):
    resume = await resume_service.get_resume(req.resume_id,user.id)
    interview_id,first_question = await interview_service.start_interview(resume,user.id)
    message_id = await message_service.add_message(interview_id,MessageRole.ASSISTANT,first_question)

    return {
        "interviewId": interview_id,
        "firstQuestion": first_question,
        "messageId": message_id
    }



    
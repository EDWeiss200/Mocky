from services.interview_services import InterviewServices
from services.resume_services import ResumeServices
from services.message_services import MessageServices
from models.models import User,Resume,MessageRole
from schemas.schemas import UserReadSchema, StartInterviewRequest, AnswerRequest
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


@router.post('answer/{interview_id}')
async def answer_question(
    interview_id: int,
    req: AnswerRequest,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service)
):


    interview = await interview_service.get_interview_by_id(interview_id)
    if not interview or interview.user_id!=user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")
    
    message_id = await message_service.add_message(interview_id,MessageRole.USER,req.answer_text)

    message_history = await message_service.get_interview_history(interview_id)
    resume = await resume_service.get_resume(interview.resume_id,user.id)

    ai_reply = await interview_service.answer(resume,message_history)

    message_id = await message_service.add_message(interview_id,MessageRole.ASSISTANT,ai_reply)

    return {
        "reply": ai_reply,
        "messageId": message_id
    }



    
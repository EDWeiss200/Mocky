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
    tags=['interview'],
    prefix='/interviews'
)

@router.post('/start')
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


@router.post('/answer/{interview_id}')
async def answer_question(
    interview_id: int,
    req: AnswerRequest,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service)
):

    MAX_QUESTIONS = 3

    interview = await interview_service.get_interview_by_id(interview_id)
    if not interview or interview.user_id!=user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")
    
    message_id = await message_service.add_message(interview_id,MessageRole.USER,req.answer_text)

    message_history = await message_service.get_interview_history(interview_id)
    resume = await resume_service.get_resume(interview.resume_id,user.id)

    user_answers_count = sum(1 for msg in message_history if msg.role == MessageRole.USER)
    if user_answers_count < MAX_QUESTIONS:

        ai_reply = await interview_service.answer(resume,message_history)
        message_id = await message_service.add_message(interview_id,MessageRole.ASSISTANT,ai_reply)
        return {
            "reply": ai_reply,
            "messageId": message_id
        }
    
    else:

        ai_reply,score,feedback = await interview_service.answer_finish(resume,message_history)

        await interview_service.finish_interview(interview_id, score)
        await message_service.add_message(interview_id, MessageRole.ASSISTANT, feedback)

        return {
            "status": "completed", 
            "score": score, 
            "feedback": feedback
        }


        



@router.post("/finish/{interview_id}")
async def finish_interview(
    interview_id:int,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service),
    message_service: MessageServices = Depends(message_service)
):
    interwiew = await interview_service.get_interview_by_id(interview_id)
    if not interview_service or interwiew.user_id != user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")
    
    if interwiew.status == SessionStatus.COMPLETED:
        raise HTTPException(status=400, detail="Интервью уже завершено")
    
    history = await message_service.get_interview_history(interview_id)

    score,feedback = await interview_service.get_score_interview(history)

    await interview_service.finish_interview(interview_id, score)
    await message_service.add_message(interview_id, MessageRole.ASSISTANT, feedback)

    return {
        "status": "completed",
        "totalScore": score,
        "feedback": feedback
    }

    



    
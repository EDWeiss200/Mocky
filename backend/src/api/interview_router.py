from services.interview_services import InterviewServices
from services.resume_services import ResumeServices
from services.message_services import MessageServices
from services.HeadHunter_services import HeadHunterService
from services.user_services import UserServices
from models.models import User,MessageRole
from schemas.schemas import StartInterviewRequest, AnswerRequest, SessionStatus, StartHHInterviewRequest, GapAnalysisResponse
from api.dependencies import interview_service
from api.dependencies import resume_service
from api.dependencies import message_service
from api.dependencies import headhunter_service
from api.dependencies import user_service
from auth.auth import current_user
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from uuid import UUID
from utils.verify_balance import VerifyBalance
from models.enum import Feature




router = APIRouter(
    tags=['interview'],
    prefix='/interviews'
)



@router.get('/{interview_id}')
async def get_interview(
    interview_id: UUID,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service)
):
    interview_id = await interview_service.get_interview(interview_id)

    return interview_id




@router.post('/start')
async def start_interview(
    req: StartInterviewRequest,
    user: User = Depends(VerifyBalance(Feature.INTERVIEW_TEXT)),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service),
    user_service: UserServices = Depends(user_service)
    
):
    resume = await resume_service.get_resume(req.resume_id,user.id)
    interview_id,first_question = await interview_service.start_interview(resume,user.id,req.role,req.number_question)
    message_id = await message_service.add_message(interview_id,MessageRole.ASSISTANT,first_question)

    await user_service.charge_for_feature(user, Feature.INTERVIEW_TEXT)

    return {
        "interviewId": interview_id,
        "firstQuestion": first_question,
        "messageId": message_id
    }






    

@router.post('/answer/{interview_id}')
async def answer_question(
    interview_id: UUID,
    req: AnswerRequest,
    user: User = Depends(VerifyBalance(Feature.INTERVIEW_TEXT)),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service),
    user_service: UserServices = Depends(user_service)
):



    interview = await interview_service.get_interview(interview_id)
    if not interview or interview.user_id!=user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")
    
    message_id = await message_service.add_message(interview_id,MessageRole.USER,req.answer_text)

    message_history = await message_service.get_interview_history(interview_id)
    resume = await resume_service.get_resume(interview.resume_id,user.id)

    user_answers_count = sum(1 for msg in message_history if msg.role == MessageRole.USER)
    if user_answers_count < interview.number_question:

        ai_reply = await interview_service.answer(resume,message_history,interview)
        message_id = await message_service.add_message(interview_id,MessageRole.ASSISTANT,ai_reply)

        await user_service.charge_for_feature(user, Feature.INTERVIEW_TEXT)

        return {
            "reply": ai_reply,
            "messageId": message_id
        }
    
    else:

        score,feedback,prep_plan,skill_scores = await interview_service.answer_finish(resume,message_history,interview)

        await interview_service.finish_interview(interview_id, score, prep_plan,skill_scores)
        await message_service.add_message(interview_id, MessageRole.ASSISTANT, feedback)

        await user_service.charge_for_feature(user, Feature.INTERVIEW_TEXT)

        return {
            "status": "completed",
            "totalScore": score,
            "feedback": feedback,
            "prepPlan": prep_plan,
            "skill_scores": skill_scores
        }






@router.post('/answer/voice/{interview_id}')
async def answer_question_voice(
    interview_id: UUID,
    file: UploadFile = File(...), 
    user: User = Depends(VerifyBalance(Feature.INTERVIEW_VOICE)),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service),
    user_service: UserServices = Depends(user_service)
):


    MAX_FILE_SIZE = 25 * 1024 * 1024 #25mb в байтах
    ALLOWED_EXTENSIONS = {"mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"}

    if not file.filename:
        raise HTTPException(status_code=400, detail="Файл не имеет имени")  
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Файл слишком большой. Максимальный размер: 25 МБ"
        )
    
    audio_data = (file.filename, file_bytes)

    transcription = await interview_service.transcribe(audio_data)

    interview = await interview_service.get_interview(interview_id)
    if not interview or interview.user_id!=user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")
    
    message_id = await message_service.add_message(interview_id,MessageRole.USER,transcription)

    message_history = await message_service.get_interview_history(interview_id)
    resume = await resume_service.get_resume(interview.resume_id,user.id)

    user_answers_count = sum(1 for msg in message_history if msg.role == MessageRole.USER)

    if user_answers_count < interview.number_question:

        ai_reply = await interview_service.answer(resume,message_history,interview)
        message_id = await message_service.add_message(interview_id,MessageRole.ASSISTANT,ai_reply)

        await user_service.charge_for_feature(user, Feature.INTERVIEW_VOICE)

        return {
            "reply": ai_reply,
            "messageId": message_id
        }
    
    else:

        score,feedback,prep_plan, skill_scores= await interview_service.answer_finish(resume,message_history,interview)

        await interview_service.finish_interview(interview_id, score,prep_plan,skill_scores)
        await message_service.add_message(interview_id, MessageRole.ASSISTANT, feedback)

        await user_service.charge_for_feature(user, Feature.INTERVIEW_VOICE)

        return {
            "status": "completed",
            "totalScore": score,
            "feedback": feedback,
            "prepPlan": prep_plan,
            "skill_scores": skill_scores
        }


        



@router.post("/finish/{interview_id}")
async def finish_interview(
    interview_id: UUID,
    user: User = Depends(VerifyBalance(Feature.INTERVIEW_TEXT)),
    interview_service: InterviewServices = Depends(interview_service),
    message_service: MessageServices = Depends(message_service),
    user_service: UserServices = Depends(user_service)
):
    interview = await interview_service.get_interview(interview_id)
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")
    
    if interview.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Интервью уже завершено")
    
    history = await message_service.get_interview_history(interview_id)

    score,feedback,prep_plan,skill_scores = await interview_service.get_score_interview(history,interview)

    await interview_service.finish_interview(interview_id, score, prep_plan,skill_scores)
    await message_service.add_message(interview_id, MessageRole.ASSISTANT, feedback)

    await user_service.charge_for_feature(user, Feature.INTERVIEW_TEXT)

    return {
        "status": "completed",
        "totalScore": score,
        "feedback": feedback,
        "prepPlan": prep_plan,
        "skill_scores": skill_scores
    }


@router.get("/")
#@cache(expire=60, key_builder=user_key_builder)
async def get_interviews_user(
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service)
):
    
    interviews = await interview_service.get_interview_user_all(user.id)

    return interviews


@router.get("/completed")
#@cache(expire=60, key_builder=user_key_builder)
async def get_interviews_user(
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service)
):
    
    interviews = await interview_service.get_interview_user_status(user.id,SessionStatus.COMPLETED)

    return interviews


@router.get("/active")
#@cache(expire=60, key_builder=user_key_builder)
async def get_interviews_user(
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service)
):
    
    interviews = await interview_service.get_interview_user_status(user.id,SessionStatus.ACTIVE)

    return interviews



@router.post('/TEST/start')
async def start_interview(
    req: StartInterviewRequest,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service)
    
):
    resume = await resume_service.get_resume(req.resume_id,user.id)
    interview_id,first_question = await interview_service.test_start_interview(resume,user.id,req.role,req.number_question)
    message_id = await message_service.add_message(interview_id,MessageRole.ASSISTANT,first_question)

    return {
        "interviewId": interview_id,
        "firstQuestion": first_question,
        "messageId": message_id
    }
    

@router.post('/TEST/answer/{interview_id}')
async def answer_question(
    interview_id: UUID,
    req: AnswerRequest,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service)
):


    interview = await interview_service.get_interview(interview_id)
    if not interview or interview.user_id!=user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")
    
    message_id = await message_service.add_message(interview_id,MessageRole.USER,req.answer_text)

    message_history = await message_service.get_interview_history(interview_id)
    resume = await resume_service.get_resume(interview.resume_id,user.id)

    user_answers_count = sum(1 for msg in message_history if msg.role == MessageRole.USER)
    if user_answers_count < interview.number_question:

        ai_reply = await interview_service.test_answer(resume,message_history,interview)
        message_id = await message_service.add_message(interview_id,MessageRole.ASSISTANT,ai_reply)
        return {
            "reply": ai_reply,
            "messageId": message_id
        }
    
    else:

        score,feedback = await interview_service.test_answer_finish(resume,message_history,interview)

        await interview_service.finish_interview(interview_id, score, [], {})
        await message_service.add_message(interview_id, MessageRole.ASSISTANT, feedback)

        return {
            "status": "completed", 
            "score": score, 
            "feedback": feedback
        }
    

@router.post("/TEST/finish/{interview_id}")
async def finish_interview(
    interview_id:UUID,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service),
    message_service: MessageServices = Depends(message_service)
):
    interwiew = await interview_service.get_interview(interview_id)
    if not interview_service or interwiew.user_id != user.id:
        raise HTTPException(status_code=404,detail="Интервью не найдено")
    
    if interwiew.status == SessionStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Интервью уже завершено")
    
    history = await message_service.get_interview_history(interview_id)

    score,feedback = await interview_service.test_get_score_interview(history,interwiew)

    await interview_service.finish_interview(interview_id, score, [], {})
    await message_service.add_message(interview_id, MessageRole.ASSISTANT, feedback)

    return {
        "status": "completed",
        "totalScore": score,
        "feedback": feedback,
        "prepPlan": [],
        "skill_scores": {}
    }


#=============================ЭНДПОИНТЫ ДЛЯ ИНТЕРВЬЮ С ВАКАНСИЕЙ==============================#

@router.post("/start/hh")
async def start_hh_interview_endpoint(
    req: StartHHInterviewRequest,
    user: User = Depends(VerifyBalance(Feature.INTERVIEW_TEXT)),
    interview_service: InterviewServices = Depends(interview_service),
    headhunter_service: HeadHunterService = Depends(headhunter_service),
    resume_service: ResumeServices = Depends(resume_service),
    message_service: MessageServices = Depends(message_service),
    user_service: UserServices = Depends(user_service)
):
    
    resume = await resume_service.get_resume(req.resume_id, user.id)

    vacancy_data = await headhunter_service.get_vacancy_data(req.hh_url)

    interview_id, first_question = await interview_service.start_hh_interview(resume, vacancy_data, user.id,req.role,req.number_question)
    
    message_id = await message_service.add_message(interview_id, MessageRole.ASSISTANT, first_question)

    await user_service.charge_for_feature(user, Feature.INTERVIEW_TEXT)

    return {
        "interviewId": interview_id,
        "vacancyTitle": vacancy_data['title'], 
        "firstQuestion": first_question,
        "messageId": message_id
    }

@router.post('/analyze_vacancy', response_model=GapAnalysisResponse)
async def analyze_vacancy_gaps(
    req: StartHHInterviewRequest,
    user: User = Depends(VerifyBalance(Feature.GAP_ANALYZE)),
    interview_service: InterviewServices = Depends(interview_service),
    resume_service: ResumeServices = Depends(resume_service),
    user_service: UserServices = Depends(user_service)
):
    resume = await resume_service.get_resume(req.resume_id, user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")
    
    hh_service = HeadHunterService()
    vacancy_data = await hh_service.get_vacancy_data(req.hh_url)
    
    # запускаем анализ
    gaps = await interview_service.analyze_gaps(resume, vacancy_data)

    await user_service.charge_for_feature(user, Feature.GAP_ANALYZE)
    
    return gaps


@router.delete('/{interview_id}')
async def delete_interview(
    interview_id: UUID,
    interview_service: InterviewServices = Depends(interview_service)
):
    interview_id = await interview_service.delete_interview(interview_id)

    return interview_id
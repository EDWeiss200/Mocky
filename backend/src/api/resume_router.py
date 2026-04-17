from services.resume_services import ResumeServices
from services.interview_services import InterviewServices
from models.models import User,Resume
from schemas.schemas import UserReadSchema, ResumeAnalysisResponse,ResumeStatisticsResponse
from api.dependencies import resume_service,interview_service
from auth.auth import current_user
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi_cache.decorator import cache
from uuid import UUID



router = APIRouter(
    tags=['resume'],
    prefix='/resumes'
)

@router.post('/upload')
async def upload_resume(
    resume_name: str | None = None,
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    resume_service: ResumeServices = Depends(resume_service)
):
    ALLOWED_EXTENSIONS = {"pdf"}
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    res = await resume_service.upload_resume(file,user,resume_name)
    return res


@router.get('')
#@cache(expire=60)
async def get_resumes_user(
    user: User = Depends(current_user),
    resume_service: ResumeServices = Depends(resume_service)
):
    

    resumes = await resume_service.get_resumes_user(user.id)

    return resumes

@router.post('/{resume_id}/analyze', response_model=ResumeAnalysisResponse)
async def analyze_resume_endpoint(
    resume_id: UUID,
    user: User = Depends(current_user),
    resume_service: ResumeServices = Depends(resume_service)
):
    # 1. Достаем резюме пользователя из базы
    resume = await resume_service.get_resume(resume_id, user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")
    

    analysis_result = await resume_service.analyze_resume(resume.raw_text)
    

    return analysis_result


@router.get('/{resume_id}/statistics', response_model=ResumeStatisticsResponse)
async def get_resume_statistics(
    resume_id: UUID,
    user: User = Depends(current_user),
    interview_service: InterviewServices = Depends(interview_service)
):
    stats = await interview_service.get_resume_stats(resume_id, user.id)
    if not stats:
        raise HTTPException(status_code=404, detail="Статистика пока не собрана. Пройдите хотя бы одно интервью!")
    return stats


@router.delete('/{resume_id}')
async def delete_resume(
    resume_id: UUID,
    user: User = Depends(current_user),
    resume_service: ResumeServices = Depends(resume_service)
):
    resume_id = await resume_service.delete_resume(resume_id)

    return resume_id


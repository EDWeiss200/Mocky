from services.resume_services import ResumeServices
from models.models import User,Resume
from schemas.schemas import UserReadSchema
from api.dependencies import resume_service
from auth.auth import current_user
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException




router = APIRouter(
    tags=['resume'],
    prefix='/resumes'
)

@router.post('upload')
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    resume_service: ResumeServices = Depends(resume_service)
):

    res = await resume_service.upload_resume(file,user)
    return res
from utils.repository import AbstractRepository
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import PyPDF2 
import io


class ResumeServices:

    def __init__(self,resume_repo: AbstractRepository) -> None:
        self.user_repo = resume_repo()

    async def upload_resume(self,file: File,user):

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Разрешены только PDF файлы")

        try:
            # читаем файл прямо в оперативной памяти
            content = await file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            
            # извлекаем текст со всех страниц
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"

            if not extracted_text.strip():
                raise HTTPException(status_code=400, detail="Не удалось извлечь текст из PDF")

            # сохраняем в базу данных

            new_resume = {
                'user_id':user.id,
                'raw_text':extracted_text.strip()
            }
            
            res = await self.user_repo.add_one(new_resume)

            # возвращаем camelCase ответ для реакта
            return {
                "resumeId": res,
                "message": "Резюме успешно загружено и обработано"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка парсинга PDF: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при обработке файла")
        
        finally:
            await file.close()
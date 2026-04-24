from utils.repository import AbstractRepository
from fastapi import File, HTTPException
import PyPDF2 
import io
from config import client
from models.models import Resume
import json
import asyncio

def extract_text_from_pdf_sync(file_bytes: bytes) -> str:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        return extracted_text.strip()


class ResumeServices:

    def __init__(self,resume_repo: AbstractRepository) -> None:
        self.resume_repo = resume_repo()

   

    async def upload_resume(self,file: File,user,resume_name):

        MAX_FILE_SIZE = 20 * 1024 * 1024

        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Разрешены только PDF файлы")

        try:
            # читаем файл прямо в оперативной памяти
            content = await file.read()

            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail="Файл слишком большой. Максимальный размер: 20 МБ"
                )

            extracted_text = await asyncio.to_thread(extract_text_from_pdf_sync, content)
            
            # извлекаем текст со всех страниц
            if not extracted_text:
                raise HTTPException(status_code=400, detail="Не удалось извлечь текст из PDF. Возможно, файл состоит из картинок.")

            if not extracted_text.strip():
                raise HTTPException(status_code=400, detail="Не удалось извлечь текст из PDF")

            # сохраняем в базу данных

            new_resume = {
                'user_id':user.id,
                "name":resume_name,
                'raw_text':extracted_text.strip()
            }
            
            res = await self.resume_repo.add_one(new_resume)

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

    async def get_resume_by_id(self,resume_id):

        resume = await self.resume_repo.find_id(resume_id)

        return resume
    

    async def get_resume(self,resume_id,user_id) -> Resume:

        filters = [
            self.resume_repo.model.id == resume_id,
            self.resume_repo.model.user_id == user_id
        ]

        resume = await self.resume_repo.find_filter_drm(filters)

        return resume
    

    async def delete_resume(self,resume_id):

        id = await self.resume_repo.delete_one(resume_id)

        return id
    
    async def get_resumes_user(self,user_id):

        filters = [
            self.resume_repo.model.user_id == user_id
        ]

        resumes = await self.resume_repo.find_filter(filters)

        return resumes
    
    async def analyze_resume(self,raw_text):


        system_prompt = """Ты топовый IT-рекрутер из FAANG и строгий Tech Lead в одном лице.
        Твоя задача — провести жесткий, но справедливый аудит резюме кандидата.

        Проанализируй текст и оцени:
        1. Какой реальный грейд (Junior/Middle/Senior) просматривается через описанный опыт?
        2. Насколько востребован этот стек технологий сейчас на рынке (оценка от 1 до 10)?
        3. Какие сильные стороны выделяют кандидата?
        4. Есть ли "красные флаги" (отсутствие достижений, непонятные формулировки, прыжки по стеку и тд)?
        5. Что конкретно нужно исправить, чтобы повысить конверсию в приглашения?

        Выдай ответ СТРОГО в формате JSON без markdown:
        {
            "estimated_grade": "Твой вердикт по грейду",
            "market_demand_score": <число 1-10>,
            "strong_points": ["плюс 1", "плюс 2" и тд],
            "red_flags": ["проблема 1", "проблема 2" и тд],
            "recommendations": ["совет 1", "совет 2" и тд]
        }
        """

        gpt_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Вот мое резюме:\n---\n{raw_text}\n---"}
        ]

        try:
            response = await client.chat.completions.create(
                model="o4-mini", # Отлично справляется с такими задачами анализа
                messages=gpt_messages,
            )
            ai_reply = response.choices[0].message.content

            # Очистка и парсинг JSON (твой проверенный метод)
            cleaned_reply = ai_reply.replace("```json", "").replace("```", "").strip()
            start_idx = cleaned_reply.find('{')
            end_idx = cleaned_reply.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                cleaned_reply = cleaned_reply[start_idx:end_idx]
                
            return json.loads(cleaned_reply)

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="ИИ выдал нечитаемый формат анализа резюме")
        except Exception as e:
            print(f"Ошибка API при аудите резюме: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при обращении к ИИ")
        

    

    
    


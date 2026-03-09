from utils.repository import AbstractRepository
from schemas.schemas import StartInterviewRequest,InterviewCreate,MessageCreate
from models.models import Resume,SessionStatus,Message,MessageRole
from fastapi import HTTPException
from config import client

class InterviewServices:

    def __init__(self,interview_repo: AbstractRepository) -> None:
        self.interview_repo = interview_repo()

    async def get_interview_by_id(self,user_id):

        filters = [
            self.interview_repo.model.id == user_id
        ]

        interview= await self.interview_repo.find_filter_drm(filters)

        

        return interview
    
    async def start_interview(self, resume: Resume,user_id): 

        if not resume:
            raise HTTPException(status_code=404, detail="Резюме не найдено")

        # создаем новую сессию собеседования
        interview = InterviewCreate(
            user_id=user_id, 
            resume_id=resume.id, 
            status=SessionStatus.ACTIVE
        )

        interview = interview.model_dump()

        interview_id = await self.interview_repo.add_one(interview)

        # формируем промпт для нейросети
        system_prompt = f"Ты строгий технический интервьюер. Вот резюме кандидата:\n{resume.raw_text}\nЗадай один сложный технический вопрос по его стеку, чтобы начать собеседование. Не пиши приветствий, сразу выдавай вопрос."
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.7
            )
            first_question = response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка генерации вопроса ИИ")




        return interview_id,first_question
    

    
    async def get_interview_id(self,interview_id):

        interview = await self.interview_repo.find_filter(interview_id)

        return interview
    

    async def answer(self, resume: Resume, message_history):

        gpt_messages = [
        {
            "role": "system", 
            "content": f"Ты строгий технический интервьюер. Резюме кандидата:\n{resume.raw_text}\nКратко оцени последний ответ и задай следующий технический вопрос."
        }
        ]

        for msg in message_history:

            role = "user" if msg.role == MessageRole.USER else "assistant"
            gpt_messages.append({"role": role, "content": msg.content})


       
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=gpt_messages,
                temperature=0.7
            )
            ai_reply = response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при обращении к ИИ")
        
        return ai_reply


        

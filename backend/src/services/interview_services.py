from utils.repository import AbstractRepository
from schemas.schemas import StartInterviewRequest,InterviewCreate,MessageCreate
from models.models import Resume,SessionStatus,Message,MessageRole
from fastapi import HTTPException
from config import client
import json

class InterviewServices:

    def __init__(self,interview_repo: AbstractRepository) -> None:
        self.interview_repo = interview_repo()

    async def get_interview(self,interview_id):

        filters = [
            self.interview_repo.model.id == interview_id
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
        system_prompt = f"""Ты строгий технический интервьюер. Вот резюме кандидата:
        ---
        {resume.raw_text}
        ---
        Твоя задача — начать собеседование. Задай ровно ОДИН конкретный технический вопрос по стеку кандидата. 
        
        СТРОГИЕ ПРАВИЛА:
        1. вопрос должен быть точечным и коротким (например, про внутреннее устройство FastAPI, изоляцию транзакций в SQLAlchemy или работу индексов в PostgreSQL).
        2. ни в коем случае не проси спроектировать архитектуру всего приложения или описать сразу несколько механизмов!
        3. вопрос должен предполагать быстрый устный ответ на 1-2 минуты.
        4. не пиши приветствий и вводных слов, сразу выдавай сам вопрос."""
        
        try:
            response = await client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "system", "content": system_prompt}],
            )
            first_question = response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка генерации вопроса ИИ")




        return interview_id,first_question
    

    


    async def answer(self, resume: Resume, message_history):

        system_prompt = f"""Ты опытный и адекватный технический Senior-интервьюер.
        
        Стек кандидата (используй ТОЛЬКО для подбора следующей темы):
        ---
        {resume.raw_text}
        ---

        Твои задачи:
        1. ФИДБЕК: Проанализируй ответ пользователя. Если он ответил "не знаю" или ошибся, отреагируй мягко (например: "Ничего страшного, это тонкий момент..."). Затем дай очень краткий правильный ответ (строго 1-2 предложения), чтобы закрыть пробел в знаниях.
        2. ВОПРОС: Задай следующий технический вопрос по стеку.
        
        СТРОГИЕ ПРАВИЛА ДЛЯ ВОПРОСА:
        - Вопрос должен быть коротким (максимум 1-2 предложения) и подходить для быстрого устного ответа.
        - КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать списки, нумерацию, булллиты или просить описать сразу несколько архитектурных шагов.
        - Фокусируйся только на ОДНОЙ конкретной детали (например: "В чем разница между X и Y?", "Как под капотом работает Z?").
        - Не пиши приветствий.
        
        История общения: (ASSISTENT - вопросы от Искуственного интелекта) (USER - ответы на вопросы от пользователя)
        
        """


        gpt_messages = [
        {
            "role": "system", 
            "content": system_prompt
        }
        ]

        for msg in message_history:

            role = "user" if msg.role == MessageRole.USER else "assistant"
            gpt_messages.append({"role": role, "content": msg.content})

        
        try:
            response = await client.chat.completions.create(
                model="gpt-5-mini",
                messages=gpt_messages,

            )
            ai_reply = response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при обращении к ИИ")
        
        return ai_reply
    



    async def answer_finish(self, resume: Resume, message_history):


        system_prompt = """Ты строгий Senior-разработчик. Собеседование завершено.
        
        твоя задача: проанализировать ТОЛЬКО историю переписки (мои вопросы и ответы кандидата). 
        резюме кандидата тебе недоступно. Оценивай исключительно то, что он отвечал в чате.
        
        правила оценки:
        1. ответ "не знаю" или уход от ответа — это 0 баллов за конкретный вопрос.
        2. если кандидат на все ответил "не знаю", итоговый балл должен быть строго 0.
        3. в фидбеке перечисли, на какие конкретно вопросы кандидат не смог ответить.
        
        выдай ответ строго в формате JSON:
        {"score": <число от 0 до 100>, "feedback": "<жесткий разбор ответов из чата>"}
        
        История общения: (ASSISTENT - вопросы от Искуственного интелекта) (USER - ответы на вопросы от пользователя)
        """

        gpt_messages = [
        {
            "role": "system", 
            "content": system_prompt
        }
        ]

        for msg in message_history:

            role = "user" if msg.role == MessageRole.USER else "assistant"
            gpt_messages.append({"role": role, "content": msg.content})

        
        try:
            response = await client.chat.completions.create(
                model="o4-mini",
                messages=gpt_messages,

            )
            ai_reply = response.choices[0].message.content
            print(f"Сырой текст от ИИ -> {ai_reply}") # выведи в консоль, чтобы увидеть врага в лицо
            
            # вычищаем возможную markdown-разметку
            cleaned_reply = ai_reply.replace("```json", "").replace("```", "").strip()
            
            # ищем границы самого объекта, отсекая болтовню до и после
            start_idx = cleaned_reply.find('{')
            end_idx = cleaned_reply.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                cleaned_reply = cleaned_reply[start_idx:end_idx]
                
            # теперь безопасно парсим
            try:
                parsed_reply = json.loads(cleaned_reply)
                score = parsed_reply.get("score", 0)
                feedback = parsed_reply.get("feedback", "Собеседование завершено.")
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="ИИ выдал нечитаемый формат")
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при обращении к ИИ")
        
        return [ai_reply,score,feedback]
    


            



    async def finish_interview(self, interview_id: int, score: int):

        data_to_update = {
            "status": SessionStatus.COMPLETED,
            "total_score": score
        }
        await self.interview_repo.update(interview_id, data_to_update)

        
    async def get_score_interview(self,history):

        system_prompt = """Ты строгий Senior-разработчик. Собеседование завершено.
        
        твоя задача: проанализировать ТОЛЬКО историю переписки (мои вопросы и ответы кандидата). 
        резюме кандидата тебе недоступно. Оценивай исключительно то, что он отвечал в чате.
        
        правила оценки:
        1. ответ "не знаю" или уход от ответа — это 0 баллов за конкретный вопрос.
        2. если кандидат на все ответил "не знаю", итоговый балл должен быть строго 0.
        3. в фидбеке перечисли, на какие конкретно вопросы кандидат не смог ответить.
        
        выдай ответ строго в формате JSON:
        {"score": <число от 0 до 100>, "feedback": "<жесткий разбор ответов из чата>"}
        
        История общения: (ASSISTENT - вопросы от Искуственного интелекта) (USER - ответы на вопросы от пользователя)
        """
        
        gpt_messages = [{"role": "system", "content": system_prompt}]
        
        for msg in history:
            role = "user" if msg.role == MessageRole.USER else "assistant"
            gpt_messages.append({"role": role, "content": msg.content})

        # стучимся в нейросеть
        try:
            response = await client.chat.completions.create(
                model="o4-mini",
                messages=gpt_messages,

            )
            ai_reply = response.choices[0].message.content
            print(f"Сырой текст от ИИ -> {ai_reply}") # выведи в консоль, чтобы увидеть врага в лицо
            
            # вычищаем возможную markdown-разметку
            cleaned_reply = ai_reply.replace("```json", "").replace("```", "").strip()
            
            # ищем границы самого объекта, отсекая болтовню до и после
            start_idx = cleaned_reply.find('{')
            end_idx = cleaned_reply.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                cleaned_reply = cleaned_reply[start_idx:end_idx]
                
            # теперь безопасно парсим
            try:
                parsed_reply = json.loads(cleaned_reply)
                score = parsed_reply.get("score", 0)
                feedback = parsed_reply.get("feedback", "Собеседование завершено.")
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="ИИ выдал нечитаемый формат")
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="ИИ вернул ответ в неверном формате")
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при подведении итогов")
        
        return score,feedback


    async def get_interview_user_all(self,user_id):

        filters = [
            self.interview_repo.model.user_id == user_id
        ]

        interviews = await self.interview_repo.find_filter(filters)

        return interviews
    


    async def get_interview_user_status(self,user_id, status: SessionStatus):

        filters = [
            self.interview_repo.model.user_id == user_id,
            self.interview_repo.model.status == status
        ]

        interviews = await self.interview_repo.find_filter(filters)

        return interviews
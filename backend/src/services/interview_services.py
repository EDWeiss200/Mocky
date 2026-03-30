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


        system_prompt = f"""Ты опытный и адекватный технический Senior-интервьюер. Вот резюме кандидата:
        ---
        {resume.raw_text}
        ---
        Твоя задача — начать собеседование. Выбери ОДНУ любую ключевую технологию из резюме и задай ровно один конкретный технический вопрос по ней.

        СТРОГИЕ ПРАВИЛА:
        1. вопрос должен быть точечным и коротким: спрашивай про внутреннее устройство, отличия подходов или неочевидные нюансы работы инструмента.
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
    

    async def test_start_interview(self, resume: Resume,user_id):
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

        first_question = "START INTERVIEW TEST MESSGAGE"
        
        return interview_id,first_question
    


    async def answer(self, resume: Resume, message_history):

        system_prompt = f"""Ты опытный и адекватный технический Senior-интервьюер.
        
        Стек кандидата (используй для подбора тем):
        ---
        {resume.raw_text}
        ---

        Твои задачи:
        1. ФИДБЕК: проанализируй ответ пользователя. Если он ответил "не знаю" или ошибся, отреагируй мягко и дай очень краткий правильный ответ (строго 1-2 предложения), чтобы закрыть пробел в знаниях.
        2. ВОПРОС: задай следующий технический вопрос.

        СТРОГИЕ ПРАВИЛА ДЛЯ ВОПРОСА:
        - СМЕНА ТЕМЫ: проанализируй историю общения. Твой новый вопрос должен быть по ДРУГОЙ технологии или из ДРУГОГО раздела резюме. Не задавай два вопроса подряд по одной теме!
        - Формат: вопрос должен быть коротким (максимум 1-2 предложения) и подходить для быстрого устного ответа.
        - Запреты: КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО использовать списки, нумерацию или просить описать сразу несколько шагов.
        - Фокус: спрашивай только об ОДНОЙ конкретной детали (например, "В чем разница между X и Y?", "Как под капотом работает Z?").
        - Без воды: не пиши приветствий.

        История общения: (ASSISTANT - твои вопросы, USER - ответы кандидата)
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
    

    async def test_answer(self, resume: Resume, message_history):

        ai_reply = "TEST ANSWER MESSAGE"
        
        return ai_reply
    



    async def answer_finish(self, resume: Resume, message_history):


        system_prompt = """Ты опытный и адекватный технический Senior-интервьюер. Собеседование завершено.
        
        Твоя задача: проанализировать ТОЛЬКО историю переписки (мои вопросы и ответы кандидата). 
        Резюме кандидата тебе недоступно. Оценивай исключительно то, что он отвечал в чате.

        Правила оценки:
        1. ответ "не знаю" или явный уход от ответа — это 0 баллов за конкретный вопрос.
        2. если кандидат на все ответил "не знаю", итоговый балл должен быть строго 0.
        3. в фидбеке перечисли, на какие конкретно вопросы кандидат не смог ответить, и отметь темы, в которых он показал хорошие знания.

        Выдай ответ строго в формате JSON без markdown-разметки:
        {"score": <число от 0 до 100>, "feedback": "<жесткий, но справедливый разбор ответов из чата>"}
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
        
        return score,feedback
    


    async def test_answer_finish(self, resume: Resume, message_history):


        score = 50

        feedback = "TEST FINISH FEEDBACK. MAX QUESTIONS"
        
        return score,feedback
    


            



    async def finish_interview(self, interview_id: int, score: int):

        data_to_update = {
            "status": SessionStatus.COMPLETED,
            "total_score": score
        }
        await self.interview_repo.update(interview_id, data_to_update)

        
    async def get_score_interview(self,history):

        system_prompt = """Ты строгий Senior-разработчик. Собеседование завершено.
        
        Твоя задача: проанализировать ТОЛЬКО историю переписки (мои вопросы и ответы кандидата). 
        Резюме кандидата тебе недоступно. Оценивай исключительно то, что он отвечал в чате.

        Правила оценки:
        1. ответ "не знаю" или явный уход от ответа — это 0 баллов за конкретный вопрос.
        2. если кандидат на все ответил "не знаю", итоговый балл должен быть строго 0.
        3. в фидбеке перечисли, на какие конкретно вопросы кандидат не смог ответить, и отметь темы, в которых он показал хорошие знания.

        Выдай ответ строго в формате JSON без markdown-разметки:
        {"score": <число от 0 до 100>, "feedback": "<жесткий, но справедливый разбор ответов из чата>"}
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
    

    async def test_get_score_interview(self,history):

        score = 50

        feedback = "TEST FINISH FEEDBACK. Forced termination"
        
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
    

    async def transcribe(self,audio_data):
                         
        try:

            transcription = await client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_data,
                response_format="text"
            )
            

        except Exception as e:
            print(f"Ошибка транскрибации: {e}")
            raise HTTPException(status_code=500, detail="Не удалось распознать аудио")
        
        return transcription
from utils.repository import AbstractRepository
from schemas.schemas import InterviewCreate
from models.models import Resume,SessionStatus,MessageRole, Interview
from models.enum import SessionStatus
from fastapi import HTTPException
from config import client
import json
from uuid import UUID
from schemas.schemas import ChartPoint,ResumeStatisticsResponse


PERSONAS = {
    "strict_senior": "Ты суровый и дотошный Senior-разработчик. Задаешь сложные вопросы, не терпишь воды, требуешь глубокого понимания «под капотом».",
    "pragmatic_lead": "Ты адекватный Tech Lead. Фокусируешься на бизнес-логике, прагматичных решениях и реальном опыте, без лишней духоты.",
    "friendly_hr": "Ты дружелюбный и поддерживающий ментор. Твоя цель — раскрыть потенциал кандидата, ты часто хвалишь и мягко направляешь при ошибках."
}

CATEGORY = ["Языки","Фреймворки","Архитектура","Базы данных","Теория"]

class InterviewServices:

    def __init__(self,interview_repo: AbstractRepository) -> None:
        self.interview_repo = interview_repo()


    async def delete_interview(self,interview_id):

        id = await self.interview_repo.delete_one(interview_id)

        return id
    

    async def get_interview(self,interview_id):

        filters = [
            self.interview_repo.model.id == interview_id
        ]

        interview= await self.interview_repo.find_filter_drm(filters)

        return interview
    
    async def start_interview(self, resume: Resume,user_id, role_key: str,number_question): 

        if not resume:
            raise HTTPException(status_code=404, detail="Резюме не найдено")

        # создаем новую сессию собеседования
        interview = InterviewCreate(
            user_id=user_id, 
            resume_id=resume.id, 
            status=SessionStatus.ACTIVE,
            role=role_key,
            number_question=number_question
        )

        interview = interview.model_dump()

        interview_id = await self.interview_repo.add_one(interview)


        persona = PERSONAS.get(role_key, PERSONAS["pragmatic_lead"])

        system_prompt = f"""{persona} 
        Вот резюме кандидата:
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
    

    async def test_start_interview(self, resume: Resume,user_id,role_key,number_question):
        if not resume:
            raise HTTPException(status_code=404, detail="Резюме не найдено")

        # создаем новую сессию собеседования
        interview = InterviewCreate(
            user_id=user_id, 
            resume_id=resume.id, 
            status=SessionStatus.ACTIVE,
            role=role_key,
            number_question=number_question
        )

        interview = interview.model_dump()

        interview_id = await self.interview_repo.add_one(interview)

        first_question = "START INTERVIEW TEST MESSGAGE"
        
        return interview_id,first_question
    


    async def answer(self, resume: Resume, message_history, interview: Interview):



        persona = PERSONAS[interview.role]
        if interview.vacancy_context:
            system_prompt = f"""{persona}
            Контекст вакансии: {interview.vacancy_context}
            Стек кандидата: {resume.raw_text}

            Твои задачи:
            1. ФИДБЕК: мягко скорректируй предыдущий ответ (1-2 предложения).
            2. ВОПРОС: задай следующий технический вопрос СТРОГО на пересечении вакансии и резюме. Если нужного навыка нет, спроси теорию.

            СТРОГИЕ ПРАВИЛА ДЛЯ ВОПРОСА:
            - УСТНЫЙ ФОРМАТ: категорически запрещено просить кандидата написать или прислать код . Требуй только устного объяснения концепций.
            - СМЕНА ТЕМЫ: проанализируй историю. Твой новый вопрос должен быть по ДРУГОЙ технологии. Не задавай два вопроса подряд по одной теме!
            - ОДИН ФОКУС: спрашивай только об ОДНОЙ конкретной детали. Никаких вопросов-комбайнов.
            - ФОРМАТ: вопрос должен быть коротким (максимум 2 предложения). Без списков и нумерации."""

        else:

            system_prompt = f"""{persona}
            
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
    

    async def test_answer(self, resume: Resume, message_history,interview):

        ai_reply = "TEST ANSWER MESSAGE"
        
        return ai_reply
    



    async def answer_finish(self, resume: Resume, message_history, interview):
        
        persona = PERSONAS[interview.role]
        if interview.vacancy_context:
            system_prompt = f"""{persona} 
            Собеседование на вакансию завершено.
            
            Контекст вакансии:
            {interview.vacancy_context}
            
            Твоя задача: проанализировать ТОЛЬКО историю переписки. 
            Оценивай исключительно ответы кандидата в чате.

            Обращайся к кандидату напрямую на "ты"

            Правила оценки:
            1. ответ "не знаю" — это 0 баллов за вопрос.
            2. если на всё ответил "не знаю", итоговый балл — 0.
            3. рассчитай итоговый балл (score) строго по 100-балльной шкале, где 100 — это идеальные ответы на все заданные вопросы.
            4. перечисли в фидбеке сильные стороны и ошибки. обращайся к пользователю строго на "ты", категорически запрещено использовать слово "кандидат" или писать в третьем лице.
            5. Оцени навыки по КАЖДОЙ из далее перечисленных категорий НЕЗАВИСИМО друг от друга по шкале от 0 до 100. кол-во категорий {len(CATEGORY)} категории: 
            {CATEGORY}. 
            КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО придумывать свои названия навыков, относи их в нужную категорию. 
            Если какая-то из {len(CATEGORY)} категорий вообще не обсуждалась, просто не включай её в JSON.
            6. составь prep_plan: список из 3-5 конкретных тем, которые нужно выучить под ЭТУ вакансию, исходя из ошибок.

            Выдай ответ строго в формате JSON без markdown-разметки:
            {{
              "score": <число>, 
              "skills_score": {{"категория 1": баллы, "Категория 2": баллы, "категория 3": баллы и тд}},
              "feedback": "<разбор>", 
              "prep_plan": ["тема 1", "тема 2" и тд]
            }}
            """
        else:
            system_prompt = f"""{persona}
            Собеседование завершено.
            
            Твоя задача: проанализировать ТОЛЬКО историю переписки (мои вопросы и ответы кандидата). 
            Резюме кандидата тебе недоступно. Оценивай исключительно то, что он отвечал в чате.

            Правила оценки:
            1. ответ "не знаю" или явный уход от ответа — это 0 баллов за конкретный вопрос.
            2. рассчитай итоговый балл (score) строго по 100-балльной шкале, где 100 — это идеальные ответы на все заданные вопросы.
            3. Оцени навыки по КАЖДОЙ из далее перечисленных категорий НЕЗАВИСИМО друг от друга по шкале от 0 до 100. кол-во категорий {len(CATEGORY)} категории: 
            {CATEGORY}. 
            КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО придумывать свои названия навыков, относи их в нужную категорию. 
            Если какая-то из {len(CATEGORY)} категорий вообще не обсуждалась, просто не включай её в JSON.
            4. перечисли в фидбеке сильные стороны и ошибки. обращайся к пользователю строго на "ты", категорически запрещено использовать слово "кандидат" или писать в третьем лице.
            5. составь prep_plan: список из 3-5 конкретных тем, которые нужно подтянуть.

            Выдай ответ строго в формате JSON без markdown-разметки:
            {{
              "score": <число>, 
              "skills_score": {{"категория 1": баллы, "Категория 2": баллы, "категория 3": баллы и тд}},
              "feedback": "<разбор>", 
              "prep_plan": ["тема 1", "тема 2" и тд]
            }}
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
                prep_plan = parsed_reply.get("prep_plan", [])
                skills_score = parsed_reply.get("skills_score", {})

            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="ИИ выдал нечитаемый формат")
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при обращении к ИИ")
        
        return score,feedback,prep_plan,skills_score
    


    async def test_answer_finish(self, resume: Resume, message_history,interview):


        score = 50

        feedback = "TEST FINISH FEEDBACK. MAX QUESTIONS"
        
        return score,feedback
    


            



    async def finish_interview(self, interview_id: int, score: int,prep_plan: list[str], skills_score: dict):

        data_to_update = {
            "status": SessionStatus.COMPLETED,
            "total_score": score,
            "prep_plan": prep_plan,
            "skills_score": skills_score
        }
        await self.interview_repo.update(interview_id, data_to_update)

        
    async def get_score_interview(self,history,interview):
        persona = PERSONAS[interview.role]
        if interview.vacancy_context:
            system_prompt = f"""{persona} 
            Собеседование на вакансию завершено.
            
            Контекст вакансии:
            {interview.vacancy_context}
            
            Твоя задача: проанализировать ТОЛЬКО историю переписки. 
            Оценивай исключительно ответы кандидата в чате.

            Обращайся к кандидату напрямую на "ты"

            Правила оценки:
            1. ответ "не знаю" — это 0 баллов за вопрос.
            2. если на всё ответил "не знаю", итоговый балл — 0.
            3. рассчитай итоговый балл (score) строго по 100-балльной шкале, где 100 — это идеальные ответы на все заданные вопросы.
            4. перечисли в фидбеке сильные стороны и ошибки. обращайся к пользователю строго на "ты", категорически запрещено использовать слово "кандидат" или писать в третьем лице..
            5. Оцени навыки по КАЖДОЙ из далее перечисленных категорий НЕЗАВИСИМО друг от друга по шкале от 0 до 100. кол-во категорий {len(CATEGORY)} категории: 
            {CATEGORY}. 
            КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО придумывать свои названия навыков, относи их в нужную категорию. 
            Если какая-то из {len(CATEGORY)} категорий вообще не обсуждалась, просто не включай её в JSON.
            6. составь prep_plan: список из 3-5 конкретных тем, которые нужно выучить под ЭТУ вакансию, исходя из ошибок.

            Выдай ответ строго в формате JSON без markdown-разметки:
            {{
              "score": <число>, 
              "skills_score": {{"категория 1": баллы, "Категория 2": баллы, "категория 3": баллы и тд}},
              "feedback": "<разбор>", 
              "prep_plan": ["тема 1", "тема 2" и тд]
            }}
            """
        else: 

            system_prompt = f"""{persona}
            Собеседование завершено
            
            Твоя задача: проанализировать ТОЛЬКО историю переписки (мои вопросы и ответы кандидата). 
            Резюме кандидата тебе недоступно. Оценивай исключительно то, что он отвечал в чате.

            Правила оценки:
            1. ответ "не знаю" или явный уход от ответа — это 0 баллов за конкретный вопрос.
            2. рассчитай итоговый балл (score) строго по 100-балльной шкале, где 100 — это идеальные ответы на все заданные вопросы.
            3. Оцени навыки по КАЖДОЙ из далее перечисленных категорий НЕЗАВИСИМО друг от друга по шкале от 0 до 100. кол-во категорий {len(CATEGORY)} категории: 
            {CATEGORY}. 
            КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО придумывать свои названия навыков, относи их в нужную категорию. 
            Если какая-то из {len(CATEGORY)} категорий вообще не обсуждалась, просто не включай её в JSON.
            4.перечисли в фидбеке сильные стороны и ошибки. обращайся к пользователю строго на "ты", категорически запрещено использовать слово "кандидат" или писать в третьем лице.
            5. составь prep_plan: список из 3-5 конкретных тем, которые нужно подтянуть.

            Выдай ответ строго в формате JSON без markdown-разметки:
            {{
              "score": <число>, 
              "skills_score": {{"категория 1": баллы, "Категория 2": баллы, "категория 3": баллы и тд}},
              "feedback": "<разбор>", 
              "prep_plan": ["тема 1", "тема 2" и тд]
            }}
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
                
                # ДОБАВЛЯЕМ ЭТУ СТРОКУ:
                prep_plan = parsed_reply.get("prep_plan", [])
                skills_score = parsed_reply.get("skills_score", {})
                
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="ИИ выдал нечитаемый формат")
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="ИИ вернул ответ в неверном формате")
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при подведении итогов")
        
        # ВОЗВРАЩАЕМ 3 ЗНАЧЕНИЯ:
        return score, feedback, prep_plan,skills_score
    

    async def test_get_score_interview(self,history,interview):

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
    



#===========  ФУНКЦИИ ДЛЯ ИНТЕРВЬЮ С ВАКАНСИЕЙ ==================#


    async def start_hh_interview(self, resume: Resume, vacancy_data: dict, user_id,role_key:str,number_question):

        context_string = (
            f"Позиция: {vacancy_data['title']}\n"
            f"Навыки: {', '.join(vacancy_data['key_skills'])}\n"
            f"Описание: {vacancy_data['description']}"
        )

        interview = InterviewCreate(
            user_id=user_id, 
            resume_id=resume.id, 
            status=SessionStatus.ACTIVE,
            vacancy_context=context_string,
            role=role_key,
            number_question=number_question
        )

        interview_id = await self.interview_repo.add_one(interview.model_dump())

        persona = PERSONAS.get(role_key, PERSONAS["pragmatic_lead"])
        system_prompt = f"""{persona} 
        
        Позиция: {vacancy_data['title']}
        Требования вакансии: {vacancy_data['description']}
        Ключевые навыки: {', '.join(vacancy_data['key_skills'])}
        
        Резюме кандидата:
        ---
        {resume.raw_text}
        ---
        
        Твоя задача — начать собеседование. Выбери ОДНУ технологию, которая есть И в вакансии, И в резюме кандидата, и задай конкретный технический вопрос.
        
        СТРОГИЕ ПРАВИЛА:
        1. УСТНЫЙ ФОРМАТ: категорически запрещено просить кандидата написать, напечатать или прислать код. Спрашивай только концепции, алгоритмы или названия методов
        2. вопрос должен быть коротким и точечным (1-2 предложения).
        3. не проси спроектировать архитектуру и не задавай несколько вопросов сразу.
        4. без приветствий и воды."""
        
        try:
            response = await client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "system", "content": system_prompt}],
            )
            first_question = response.choices[0].message.content
        except Exception as e:
            print(f"Ошибка API: {e}")
            raise HTTPException(status_code=500, detail="Ошибка генерации вопроса ИИ")

        return interview_id, first_question
    


    
    async def analyze_gaps(self, resume: Resume, vacancy_data: dict) -> dict:
        system_prompt = f"""Ты опытный IT-рекрутер. 
        Твоя задача — сравнить резюме кандидата и требования вакансии, чтобы выявить сильные стороны и пробелы (gap-анализ).

        Вакансия: {vacancy_data['title']}
        Требования: {vacancy_data['description']}
        Навыки: {', '.join(vacancy_data['key_skills'])}

        Резюме кандидата:
        ---
        {resume.raw_text}
        ---

        Выдай ответ СТРОГО в формате JSON:
        {{
          "match_percentage": <число от 0 до 100>,
          "matched_skills": ["навык 1", "навык 2"],
          "missing_skills": ["навык из вакансии, которого нет в резюме"],
          "warning": "<одно короткое предложение, к чему готовиться на собеседовании>"
        }}
        """

        try:
            response = await client.chat.completions.create(
                model="o4-mini",
                messages=[{"role": "system", "content": system_prompt}],
            )
            ai_reply = response.choices[0].message.content

            # вычищаем возможную markdown-разметку (как ты уже делал в финише)
            cleaned_reply = ai_reply.replace("```json", "").replace("```", "").strip()
            
            start_idx = cleaned_reply.find('{')
            end_idx = cleaned_reply.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                cleaned_reply = cleaned_reply[start_idx:end_idx]
                
            parsed_reply = json.loads(cleaned_reply)
            return parsed_reply

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="ИИ выдал нечитаемый формат анализа")
        except Exception as e:
            print(f"Ошибка API при gap-анализе: {e}")
            raise HTTPException(status_code=500, detail="Ошибка при обращении к ИИ")
        

    async def get_resume_stats(self,resume_id: UUID,user_id: UUID):

        filters = [
            self.interview_repo.model.user_id == user_id,
            self.interview_repo.model.resume_id == resume_id,
            self.interview_repo.model.status == SessionStatus.COMPLETED
        ]

        interviews = await self.interview_repo.find_filter(filters)
        
        if not interviews:
            return None
        
        scores = [i.total_score for i in interviews if i.total_score is not None]

        total = len(scores)
        avg_s = round(sum(scores)/total,1) if total > 0 else 0
        max_s = max(scores) if scores else 0

        chart = [ChartPoint(date=i.created_at, score=i.total_score) for i in interviews]

        tips = []
        for i in interviews[-3:]:
            if i.prep_plan:
                tips.extend(i.prep_plan)

        unique_tips = list(dict.fromkeys(tips))[:5]


        skill_sums = {}
        skill_counts = {}

        for interview in interviews:
            if interview.skills_score:
                for skill, score in interview.skills_score.items():
                    if skill not in skill_sums:
                        skill_sums[skill] = 0
                        skill_counts[skill] = 0
                    skill_sums[skill] += score
                    skill_counts[skill] += 1

        # Вычисляем средний балл по каждому навыку
        radar_data = {}
        for skill in skill_sums:
            radar_data[skill] = int(skill_sums[skill] / skill_counts[skill])


        return ResumeStatisticsResponse(
            total_interviews=total,
            average_score=avg_s,
            max_score=max_s,
            score_dynamics=chart,
            top_recommendations=unique_tips,
            radar_data=radar_data 
        )

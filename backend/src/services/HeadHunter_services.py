
import re
import httpx
from fastapi import HTTPException
from config import MYMAIL

class HeadHunterService:

    def __init__(self) -> None:

        self.headers = {
            "User-Agent": f"MockyInterviewApp/1.0 {MYMAIL}"
        }
    
    def extract_vacansy(self,url: str) -> str:

        url_str = str(url)

        match = re.search(r"/vacancy/(\d+)",url_str)
        if not match:
            raise HTTPException(status_code=400, detail="Неверная ссылка, убедитесь что это ссылка на вакансию hh.ru")
        
        return match.group(1)
    
    def clean_html(self, raw_html: str) -> str:

        if not raw_html:
            return ""

        clean_text = re.sub(r'<.*?>', ' ', raw_html)

        return re.sub(r'\s+', ' ', clean_text).strip()
        

    async def get_vacancy_data(self, url: str) -> dict:

        vacancy_id = self.extract_vacansy(url)
        api_url = f"https://api.hh.ru/vacancies/{vacancy_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=self.headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Вакансия не найдена или удалена")
        elif response.status_code != 200:
            raise HTTPException(status_code=400, detail="Ошибка при обращении к серверам HH")
        
        data = response.json()

        title = data.get("name", "Не указано")
        raw_description = data.get("description", "")
        clean_description = self.clean_html(raw_description)
        
        key_skills = [skill.get("name") for skill in data.get("key_skills", [])]

        return {
            "title": title,
            "description": clean_description,
            "key_skills": key_skills
        }



        

from fastapi import FastAPI
import uvicorn

from auth.auth import auth_backend,fastapi_users
from auth.schemas import UserCreate,UserRead

from fastapi.middleware.cors import CORSMiddleware
from api.user_router import router as user_router
from api.resume_router import router as resume_router
from api.interview_router import router as interview_router
from api.message_router import router as message_router



app = FastAPI(
    title='Mocky',
)



origins = [
    "http://127.0.0.1:5173",
    "http://127.0.0.1",
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:5173/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)






@app.get("/")
async def home():
    return "Hello World"



app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


app.include_router(user_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(message_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
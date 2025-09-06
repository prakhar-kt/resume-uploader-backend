from fastapi import FastAPI
from app.resume.routers import router as resume_router
from fastapi.middleware.cors import CORSMiddleware
from decouple import config

app = FastAPI()

FE_URL = config("FE_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FE_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume_router)

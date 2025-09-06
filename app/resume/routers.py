from typing import List
from datetime import date
from fastapi import APIRouter, UploadFile, Form, File
from app.db.config import SessionDep
from app.resume.schemas import ResumeCreate, ResumeOut, GenderEnum
from app.resume.services import create_resume, get_all_resumes


router = APIRouter(prefix="/resumes", tags=["Resume"])


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(
    session: SessionDep,
    name: str = Form(...),
    email: str = Form(...),
    dob: str = Form(...),
    state: str = Form(...),
    gender: GenderEnum = Form(...),
    # Swagger often sends arrays from forms unreliably; accept CSV and split
    preferred_locations: str = Form(...),
    image: UploadFile = File(...),
    resume_file: UploadFile = File(...),
):
    # Parse dob string to date
    parsed_dob = date.fromisoformat(dob)
    locations_list = [
        loc.strip() for loc in preferred_locations.split(",") if loc.strip()
    ]
    data = ResumeCreate(
        name=name,
        email=email,
        dob=parsed_dob,
        state=state,
        gender=gender,
        preferred_locations=locations_list,
    )
    resume = await create_resume(session, data, image, resume_file)
    return resume

@router.get("/allresumes", response_model=List[ResumeOut])
async def list_resumes(session: SessionDep):
    resumes = await get_all_resumes(session)
    return resumes

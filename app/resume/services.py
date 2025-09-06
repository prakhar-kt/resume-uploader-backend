from fastapi import HTTPException, UploadFile
from typing import List, cast
from app.resume.models import Resume
from app.resume.schemas import ResumeCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.resume.utils import save_uploaded_file


async def create_resume(
    session: AsyncSession,
    data: ResumeCreate,
    image: UploadFile,
    resume_file: UploadFile,
):
    stmt = select(Resume).where(Resume.email == data.email)
    result = await session.scalars(stmt)
    if result.first():
        raise HTTPException(status_code=400, detail="Email already exists")

    image_path = await save_uploaded_file(image, "images")
    file_path = await save_uploaded_file(resume_file, "resumes")

    locations: List[str] = cast(List[str], data.preferred_locations)
    resume = Resume(
        name=data.name,
        email=data.email,
        dob=data.dob,
        state=data.state,
        gender=data.gender,
        preferred_locations=",".join(locations),
        image_path=image_path,
        resume_file_path=file_path,
    )
    session.add(resume)
    await session.commit()
    await session.refresh(resume)
    return resume


async def get_all_resumes(session: AsyncSession):
    result = await session.scalars(select(Resume))
    return result.all()

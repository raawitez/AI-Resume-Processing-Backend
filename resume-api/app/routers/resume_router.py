import os
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.schemas.resume_schema import (
    ResumeUploadResponse,
    ResumeStatusResponse,
    ResumeScoreResponse
)
from app.services.resume_service import ResumeService
from app.dependencies import get_db, get_current_user
from app.core.file_validator import (
    validate_resume_file,
    read_and_validate_size,
    generate_safe_filename,
    get_upload_path
)

router = APIRouter(prefix="/resume", tags=["Resume"])

def get_service(db: Session = Depends(get_db))-> ResumeService:
    return ResumeService(db)

@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=202,
    summary="Upload a resume PDF for processing"
)
async def upload_resume(
    file: UploadFile = File(...),
    service: ResumeService = Depends(get_service),
    current_user: dict = Depends(get_current_user)
):
    validate_resume_file(file)

    content = await read_and_validate_size(file)
    stored_filename = generate_safe_filename(file.filename)
    file_path = get_upload_path(stored_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    resume = service.create_resume(
        user_id=current_user["user_id"],
        original_filename=file.filename,
        stored_filename=stored_filename,
        file_path=file_path,
        file_size=len(content)
    )

    return ResumeUploadResponse(
        resume_id=resume.id,
        status=resume.status,
        message="Resume uploaded successfully. Processing has started.",
        file_name=file.filename
    )

@router.get(
    "/{resume_id}/status",
    response_model=ResumeStatusResponse,
    summary="Check resume processing status"
)

def get_status(
    resume_id:    int,
    service:      ResumeService = Depends(get_service),
    current_user: dict = Depends(get_current_user)
):
    return service.get_status(resume_id, current_user["user_id"])


@router.get(
    "/{resume_id}/score",
    response_model=ResumeScoreResponse,
    summary="Get resume score"
)
def get_score(
    resume_id:    int,
    service:      ResumeService = Depends(get_service),
    current_user: dict = Depends(get_current_user)
):
    return service.get_score(resume_id, current_user["user_id"])
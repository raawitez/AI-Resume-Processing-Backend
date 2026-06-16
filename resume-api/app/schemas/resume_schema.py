from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import json

class ResumeUploadResponse(BaseModel):
    resume_id:int
    status:str
    message:str
    file_name:str

class ResumeStatusResponse(BaseModel):
    resume_id:int
    status:str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ResumeScoreResponse(BaseModel):
    resume_id: int
    status: str
    score: Optional[float] = None
    score_details: Optional[Dict[str, Any]] = None
    message: str

    class Config:
        from_attributes = True

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
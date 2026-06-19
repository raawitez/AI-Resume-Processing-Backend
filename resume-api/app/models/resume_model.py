from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)

    original_filename = Column(String(255), nullable=False)

    stored_filename = Column(String(255), nullable=False)

    file_path = Column(String(255), nullable=False)

    file_size = Column(Integer, nullable=False)

    status = Column(String(20), default="uploaded", nullable=False)

    score = Column(Float, nullable=True)

    score_details = Column(Text, nullable=True)
    

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return(
            f"<Resume id={self.id}> "
            f"user={self.user_id} "
            f"status={self.status} "
            f"score={self.score}"
        )
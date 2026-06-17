import json
from sqlalchemy.orm import Session
from fastapi import HTTPException
from loguru import logger

from app.models.resume_model import Resume
from app.messaging.rabbitmq_client import publisher
from app.messaging.events import(
    QUEUE_RESUME_PROCESSING,
    build_resume_processing_event
)
from app.cache.redis_client import get_cache, set_cache

CACHE_SCORE_KEY = "resume_score:{resume_id}"
TTL_SCORE = 3600

class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    def _get_resume_or_404(self, resume_id: int, user_id: int) -> Resume:
        resume = (
            self.db.query(Resume).filter(
                Resume.id = resume_id,
                Resume.user_id = user_id,
            ).first()
        )

        if not resume:
            raise HTTPException(
                status_code=404,
                detail=f"Resume {resume_id} not found"
            )
        return resume

    def create_resume(
            self,
            user_id: int,
            original_filename: str,
            stored_filename: str,
            file_path: str,
            file_size: int
    ) -> Resume:
        resume = Resume(
            user_id = user_id,
            original_filename = original_filename,
            stored_filename = stored_filename,
            file_path = file_path,
            file_size = file_size,
            status = "uploaded"
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)

        logger.info(
            f"Resume {resume.id} saved - "
            f"user={user_id} file={original_filename}"
        )

        event = build_resume_processing_event(
            resume_id= resume.id,
            file_path=file_path,
            user_id=user_id
        )

        published = publisher.publish(QUEUE_RESUME_PROCESSING, event)

        if published:
            resume.status = "queued"
            self.db.commit()
            logger.info(f"Resume {resume.id} queued for processing")

        else:
            logger.warning(
                f"Resume {resume.id} saved but NOT queued - "
                f"RabbitMQ unavailable"
            )

        return resume

    def get_status(self, resume_id: int, user_id: int) -> dict:
        resume = self._get_resume_or_404(resume_id, user_id)
        return{
            "resume_id": resume.id,
            "status": resume.status,
            "created_at": resume.created_at
        }

    def get_score(self, resume_id: int, user_id: int) -> dict:
        cache_key = CACHE_SCORE_KEY.format(resume_id=resume_id)

        cached = get_cache(cache_key)
        if cached:
            logger.info(f"Cache HIT - resume score {resume_id}")
            return cached

        logger.info(f"Cache MISS - querying DB for resume {resume_id}")
        resume = self._get_resume_or_404(resume_id, user_id)

        if resume.status in ("uploaded", "queued", "processing"):
            return{
                "resume_id": resume.id,
                "status": resume.status,
                "score": None,
                "score_details": None,
                "message": f"Resume is still {resume.status}. Check back soon."
            }

        if resume.status == "failed":
            return{
                "resume_id": resume.id,
                "status": "failed",
                "score": None,
                "score_details": None,
                "message": "Processing failed. Please re-upload your resume."
                }

        score_details = None
        if resume.score_details:
            try:
                score_details = json.loads(resume.score_details)
            except json.JSONDecodeError:
                score_details = None

        result = {
            "resume_id": resume.id,
            "status": resume.status,
            "score": resume.score,
            "score_details": score_details,
            "message": f"Score: {resume.score}/100"
        }

        set_cache(cache_key, result, TTL_SCORE)

        return result
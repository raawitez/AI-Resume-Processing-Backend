from datetime import datetime

QUEUE_RESUME_PROCESSING = "resume_processing"
EVENT_RESUME_UPLOADED = "resume_uploaded"

def build_resume_processing_event(
        resume_id: int,
        file_path: str,
        user_id: int
)-> dict:
    return {
        "event": EVENT_RESUME_UPLOADED,
        "resume_id": resume_id,
        "file_path": file_path,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }

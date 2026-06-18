from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.core.logger import setup_logger
setup_logger()

from app.database import Base, engine, SessionLocal
from app.models import resume_model              # registers with Base
from app.routers import auth_router
from app.routers.resume_router import router as resume_router
from app.routers.health_router import router as health_router
from app.routers.metrics_router import router as metrics_router
from app.middleware.logging_middleware import log_requests
from app.core.exceptions import global_exception_handler
from app.cache.redis_client import check_redis
from app.messaging.rabbitmq_client import publisher
from app.core.metrics import metrics
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("AI Resume Processing API — Starting Up")
    logger.info("=" * 60)

    metrics.start_time = time.time()

    
    logger.info("Database tables ready")

    redis_ok = check_redis()
    if not redis_ok:
        logger.warning(
            "Redis unavailable — "
            "score caching disabled, will use DB directly"
        )

    publisher.connect()
    if publisher.channel:
        logger.info(" RabbitMQ publisher connected")
    else:
        logger.warning(
            " RabbitMQ unavailable — "
            "resumes will be saved but not queued for processing"
        )

    logger.info("=" * 60)
    logger.info("API ready → http://localhost:8000/docs")
    logger.info("=" * 60)

    yield   

    logger.info("Shutting down API...")
    publisher.disconnect()
    logger.info("Goodbye ✅")



app = FastAPI(
    title="AI Resume Processing API",
    version="1.0",
    description="""
## AI Resume Processing Backend

An event-driven backend for async resume scoring.

### How it works:
1. **Register** → create account
2. **Login** → get JWT token
3. **Upload** → `POST /resume/upload` with PDF
4. **Poll status** → `GET /resume/{id}/status`
5. **Get score** → `GET /resume/{id}/score`

### Tech Stack:
FastAPI · SQLAlchemy · RabbitMQ · Redis · Docker · JWT

### Monitoring:
- `GET /health` → dependency status
- `GET /health/live` → liveness probe
- `GET /health/ready` → readiness probe
- `GET /metrics` → performance metrics
    """,
    lifespan=lifespan
)



app.middleware("http")(log_requests)

app.add_exception_handler(Exception, global_exception_handler)



app.include_router(auth_router.router)    
app.include_router(resume_router)         
app.include_router(health_router)        
app.include_router(metrics_router)       



@app.get("/", tags=["Root"])
def root():
    return {
        "name":        "AI Resume Processing API",
        "version":     "1.0",
        "status":      "running",
        "docs":        "/docs",
        "health":      "/health",
        "metrics":     "/metrics"
    }
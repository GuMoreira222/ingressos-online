import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.routes import router as payment_router
from core.config import settings
from core.logger import get_logger
from db.database import Base, engine


logger = get_logger()

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.warning(f"Database tables already initialized or being initialized: {e}")

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app)
except ModuleNotFoundError:
    logger.warning("Prometheus instrumentator is not installed")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} ProcessTime: {process_time:.4f}s"
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"message": "Internal server error"})


app.include_router(payment_router, prefix="/payments", tags=["payments"])


@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI
from api.webhook_receiver import router as webhook_router
from core.logger import logger

app = FastAPI(title="Python Enterprise XAI Reviewer")

app.include_router(webhook_router)

@app.get("/health")
def health_check():
    logger.info("Health check endpoint pinged.")
    return {"status": "healthy", "version": "1.0.0", "message": "Enterprise XAI Server is running."}
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from core.config import settings
from core.logger import logger
from services.review_orchestrator import process_pipeline

router = APIRouter()

async def verify_signature(request: Request):
    signature = request.headers.get("x-hub-signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    body = await request.body()
    expected_sig = "sha256=" + hmac.new(
        settings.WEBHOOK_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_sig):
        logger.error("HMAC Signature validation failed!")
        raise HTTPException(status_code=401, detail="Invalid signature")

@router.post("/api/webhook")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    await verify_signature(request) # Enforces HMAC Security!
    
    payload = await request.json()
    action = payload.get("action")
    
    if "pull_request" in payload and action in ["opened", "synchronize"]:
        pr_number = payload["pull_request"]["number"]
        repo_name = payload["repository"]["full_name"]
        head_sha = payload["pull_request"]["head"]["sha"] # Needed for Gatekeeper
        
        logger.info(f"Webhook Validated: PR #{pr_number} on {repo_name}")
        background_tasks.add_task(process_pipeline, repo_name, pr_number, head_sha)
        
        return {"status": "Processing in background"}

    return {"status": "Event ignored"}
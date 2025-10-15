import asyncio
import logging
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from src.models import TaskRequest, APIResponse, EvaluationPayload
from src.config import config
from src.utils import decode_and_save_attachments, sanitize_repo_name
from src.llm_generator import LLMAppGenerator
from src.github_manager import GitHubManager
from src.evaluator import EvaluationNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="LLM Code Deployment API",
    description="Automated app generation and deployment system",
    version="1.0.0"
)

# Store task state (in production, use a database)
task_state = {}


@app.on_event("startup")
async def startup_event():
    """Validate configuration on startup"""
    try:
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please set up your .env file based on .env.example")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "LLM Code Deployment API",
        "version": "1.0.0"
    }


@app.post("/request", response_model=APIResponse)
async def handle_request(
    request: TaskRequest,
    background_tasks: BackgroundTasks
):
    """
    Main endpoint to receive task requests
    Validates secret, returns immediate 200, then processes in background
    """
    logger.info(f"Received request for task: {request.task}, round: {request.round}")
    
    # Verify secret
    if request.secret != config.STUDENT_SECRET:
        logger.warning(f"Invalid secret for task {request.task}")
        raise HTTPException(status_code=401, detail="Invalid secret")
    
    # Check if task is already being processed
    task_key = f"{request.task}-{request.round}"
    if task_key in task_state and task_state[task_key].get("status") == "processing":
        logger.warning(f"Task {task_key} is already being processed")
        return APIResponse(
            status="accepted",
            message="Task is already being processed",
            task=request.task,
            round=request.round
        )
    
    # Mark as processing
    task_state[task_key] = {
        "status": "processing",
        "started_at": datetime.now().isoformat()
    }
    
    # Schedule background processing
    if request.round == 1:
        background_tasks.add_task(process_build_task, request)
    else:
        background_tasks.add_task(process_revision_task, request)
    
    # Return immediate 200 response
    return APIResponse(
        status="accepted",
        message=f"Task {request.task} round {request.round} accepted for processing",
        task=request.task,
        round=request.round
    )


async def process_build_task(request: TaskRequest):
    """Process round 1: Build and deploy new app"""
    task_key = f"{request.task}-{request.round}"
    start_time = time.time()
    
    try:
        logger.info(f"Starting build task: {request.task}")
        
        # 1. Decode and save attachments
        attachments = await decode_and_save_attachments(request.attachments, request.task)
        logger.info(f"Saved {len(attachments)} attachments")
        
        # 2. Generate app using LLM
        generator = LLMAppGenerator()
        app_dir = await generator.generate_app(
            brief=request.brief,
            checks=request.checks,
            attachments=attachments,
            task_id=request.task
        )
        logger.info(f"Generated app at: {app_dir}")
        
        # 3. Create GitHub repo and deploy to Pages
        elapsed = time.time() - start_time
        if elapsed > config.EVALUATION_TIMEOUT - 60:  # Leave 1 min buffer
            logger.warning(f"Approaching timeout ({elapsed:.1f}s elapsed)")
        
        github_mgr = GitHubManager()
        repo_url, commit_sha, pages_url = await github_mgr.create_and_deploy(
            app_dir=app_dir,
            task_id=request.task
        )
        logger.info(f"Deployed to GitHub Pages: {pages_url}")
        
        # 4. Notify evaluation URL
        elapsed = time.time() - start_time
        logger.info(f"Task processing took {elapsed:.1f}s")
        
        if elapsed > config.EVALUATION_TIMEOUT:
            logger.error(f"Task exceeded timeout ({elapsed:.1f}s > {config.EVALUATION_TIMEOUT}s)")
            raise TimeoutError(f"Task processing exceeded {config.EVALUATION_TIMEOUT}s")
        
        notifier = EvaluationNotifier()
        payload = EvaluationPayload(
            email=request.email,
            task=request.task,
            round=request.round,
            nonce=request.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
        
        success = await notifier.notify(request.evaluation_url, payload)
        
        # Update task state
        task_state[task_key] = {
            "status": "completed" if success else "failed",
            "completed_at": datetime.now().isoformat(),
            "repo_url": repo_url,
            "pages_url": pages_url,
            "notification_sent": success
        }
        
        logger.info(f"Build task completed: {request.task}")
    
    except Exception as e:
        logger.error(f"Build task failed: {e}", exc_info=True)
        task_state[task_key] = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }


async def process_revision_task(request: TaskRequest):
    """Process round 2: Update existing app"""
    task_key = f"{request.task}-{request.round}"
    start_time = time.time()
    
    try:
        logger.info(f"Starting revision task: {request.task}")
        
        # Get repo name from round 1
        round1_key = f"{request.task}-1"
        if round1_key not in task_state:
            raise ValueError("Round 1 must be completed before round 2")
        
        repo_name = sanitize_repo_name(request.task)
        
        # 1. Decode and save attachments
        attachments = await decode_and_save_attachments(request.attachments, request.task)
        logger.info(f"Saved {len(attachments)} attachments")
        
        # 2. Generate updated app using LLM
        generator = LLMAppGenerator()
        app_dir = await generator.generate_app(
            brief=request.brief,
            checks=request.checks,
            attachments=attachments,
            task_id=request.task
        )
        logger.info(f"Generated updated app at: {app_dir}")
        
        # 3. Update GitHub repo
        elapsed = time.time() - start_time
        if elapsed > config.EVALUATION_TIMEOUT - 60:  # Leave 1 min buffer
            logger.warning(f"Approaching timeout ({elapsed:.1f}s elapsed)")
        
        github_mgr = GitHubManager()
        commit_sha, pages_url = await github_mgr.update_repo(
            repo_name=repo_name,
            app_dir=app_dir,
            update_message=f"Round {request.round} update"
        )
        logger.info(f"Updated GitHub Pages: {pages_url}")
        
        # 4. Notify evaluation URL
        elapsed = time.time() - start_time
        logger.info(f"Task processing took {elapsed:.1f}s")
        
        if elapsed > config.EVALUATION_TIMEOUT:
            logger.error(f"Task exceeded timeout ({elapsed:.1f}s > {config.EVALUATION_TIMEOUT}s)")
            raise TimeoutError(f"Task processing exceeded {config.EVALUATION_TIMEOUT}s")
        
        notifier = EvaluationNotifier()
        repo_url = f"https://github.com/{config.GITHUB_USERNAME}/{repo_name}"
        payload = EvaluationPayload(
            email=request.email,
            task=request.task,
            round=request.round,
            nonce=request.nonce,
            repo_url=repo_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
        
        success = await notifier.notify(request.evaluation_url, payload)
        
        # Update task state
        task_state[task_key] = {
            "status": "completed" if success else "failed",
            "completed_at": datetime.now().isoformat(),
            "repo_url": repo_url,
            "pages_url": pages_url,
            "notification_sent": success
        }
        
        logger.info(f"Revision task completed: {request.task}")
    
    except Exception as e:
        logger.error(f"Revision task failed: {e}", exc_info=True)
        task_state[task_key] = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get status of a task"""
    results = {}
    for key, state in task_state.items():
        if key.startswith(task_id):
            results[key] = state
    
    if not results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )

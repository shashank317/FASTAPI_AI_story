import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from sqlalchemy.orm import Session, joinedload

from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schmeas.story import (
    CompleteStoryResponse,
    CompleteStoryNodeResponse,
    CreateStoryRequest
)
from schmeas.job import StoryJobResponse
from core.story_generators import StoryGenerator

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)

# Get or generate a new session ID from cookie
def get_session_id(session_id: Optional[str] = Cookie(None)) -> str:
    return session_id or str(uuid.uuid4())

@router.post("/create", response_model=StoryJobResponse)
def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    job_id = str(uuid.uuid4())
    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="pending"
    )
    db.add(job)
    db.commit()

    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )

    return job

def generate_story_task(job_id: str, theme: str, session_id: str):
    db = SessionLocal()
    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
        if not job:
            return

        try:
            job.status = "processing"
            db.commit()

            story = StoryGenerator.generate_story(db, session_id, theme)

            job.story_id = story.id
            job.status = "completed"
            job.completed_at = datetime.now()
            db.commit()

        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.completed_at = datetime.now()
            db.commit()

    finally:
        db.close()

@router.get("/{story_id}", response_model=CompleteStoryResponse)
def get_story(story_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a full story, including all its nodes.
    This endpoint uses an optimized query to fetch the story and all associated
    nodes at once to prevent performance issues.
    """
    story = (
        db.query(Story)
        .options(joinedload(Story.nodes))  # Eagerly load the related nodes
        .filter(Story.id == story_id)
        .first()
    )
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    # The nodes are already loaded on the story object thanks to `joinedload`
    node_dict = {
        node.id: CompleteStoryNodeResponse(
            id=node.id,
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending,
            options=node.options
        ) for node in story.nodes
    }

    root_node = next((node for node in story.nodes if node.is_root), None)
    if not root_node:
        raise HTTPException(status_code=500, detail="Root node not found")

    return CompleteStoryResponse(
        id=story.id,
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=node_dict[root_node.id],
        all_nodes=node_dict
    )

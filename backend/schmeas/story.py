from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

class StoryOptionSchema(BaseModel):
    text : str
    node_id: Optional[int] = None


class StoryNodeBase(BaseModel):
    content : str
    is_ending: bool = False
    is_winning_ending: bool = False



class CompleteStoryNodeResponse(StoryNodeBase):
    id: int
    options: List[StoryOptionSchema] = []

    class Config:
        from_attributes = True

class storyBase(BaseModel):
    title: str
    session_id: Optional[str] = None

    class Config:
        from_attributes =True

class CreateStoryRequest(BaseModel):
    theme : str


class CompleteStoryResponse(storyBase):
    id: int
    created_at: datetime
    root_node: CompleteStoryNodeResponse
    all_nodes: Dict[int, CompleteStoryNodeResponse]

    class Config:
        from_attributes =True
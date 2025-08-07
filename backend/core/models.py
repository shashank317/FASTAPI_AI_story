from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class StoryOptionLLM(BaseModel):
    text: str = Field(description="The text of the option")
    nextNode: StoryNodeLLM = Field(
        description="The next node content and its options"
    )


class StoryNodeLLM(BaseModel):
    content: str = Field(description="The content of the story node")
    isEnding: bool = Field(description="Whether this node is an ending node")
    isWinningEnding: bool = Field(description="Whether this ending node is a winning ending")
    options: Optional[List[StoryOptionLLM]] = Field(
        default=None, description="List of options available at this node. Null for ending nodes."
    )

class StoryLLMResponse(BaseModel):
    title: str = Field(description="The title of the story")
    rootNode: StoryNodeLLM = Field(
        description="The root node of the story, containing the starting situation and options"
    )
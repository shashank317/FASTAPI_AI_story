from sqlalchemy.orm import Session

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser

from core.prompts import STORY_PROMPT
from core.config import Settings

from models.story import Story, StoryNode
from core.models import StoryLLMResponse, StoryNodeLLM
from dotenv import load_dotenv
import os

load_dotenv()

class StoryGenerator:

    @classmethod
    def _get_llm(cls, settings: Settings):
        # Settings validation ensures the API key is present.
        return ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest",
                                       temperature=0,
                                       google_api_key=settings.GOOGLE_API_KEY,
                                     
                            
                                       )

    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy") -> Story:
        settings = Settings()
        llm = cls._get_llm(settings)
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        prompt = ChatPromptTemplate.from_messages([
        ("system", STORY_PROMPT),
        ("human", f"Create the story with this theme: {theme}\n\n{{format_instructions}}")
    ])

        prompt = prompt.partial(
            format_instructions=story_parser.get_format_instructions()
        )
        
        # Log the prompt being sent
        import logging
        logging.debug(f"Prompt: {prompt}")
        
        # Invoke the LLM
        raw_response = llm.invoke(prompt.invoke({}))

        # Get content depending on LLM response type
        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content
        elif hasattr(raw_response, "text"):
            response_text = raw_response.text

        # Parse the structured response
        story_structure = story_parser.parse(response_text)

        # Save the story
        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()

        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()
        return story_db

    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        node = StoryNode(
            story_id=story_id,
            content=node_data.content if hasattr(node_data, "content") else node_data["content"],
            is_root=is_root,
            is_ending=node_data.isEnding if hasattr(node_data, "isEnding") else node_data.get["isEnding"],
            is_winning_ending=node_data.isWinningEnding if hasattr(node_data, "isWinningEnding") else node_data.get["isWinningEnding"],
            options=[]
        )
        db.add(node)
        db.flush()

        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode

                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)

                child_node = cls._process_story_node(db, story_id, next_node, False)

                options_list.append({
                    "text": option_data.text,
                    "node_id": child_node.id
                })

            node.options = options_list

        db.flush()
        return node

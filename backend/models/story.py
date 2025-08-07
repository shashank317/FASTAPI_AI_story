from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.database import Base


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    session_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    nodes = relationship(
        argument="StoryNode",
        back_populates="story",
        cascade="all, delete-orphan"  # Added cascade behavior
    )
    job = relationship(
        "StoryJob",
        back_populates="story",
        uselist=False  # Ensures a one-to-one relationship
    )


class StoryNode(Base):
    __tablename__ = "story_nodes"

    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), index=True)  # Added ondelete="CASCADE"
    content = Column(Text)
    is_root = Column(Boolean, default=False)
    is_ending = Column(Boolean, default=False)
    is_winning_ending = Column(Boolean, default=False)
    options = Column(JSON, default=list)

    story = relationship(argument="Story", back_populates="nodes")


def test_cascading_deletes(db_session):
    # Create a story
    story = Story(title="Test Story", session_id="123")
    db_session.add(story)
    db_session.flush()

    # Create associated story nodes
    node1 = StoryNode(story_id=story.id, content="Node 1", is_root=True)
    node2 = StoryNode(story_id=story.id, content="Node 2", is_root=False)
    db_session.add_all([node1, node2])
    db_session.flush()

    # Delete the story
    db_session.delete(story)
    db_session.flush()

    # Verify that story nodes are deleted
    assert db_session.query(StoryNode).filter_by(story_id=story.id).count() == 0
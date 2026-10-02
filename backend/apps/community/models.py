from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from core.database import Base


class CommunityPost(Base):
    __tablename__ = 'community_posts'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    board = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String, default='Pending review')
    label = Column(String, default='Farmer experience')
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

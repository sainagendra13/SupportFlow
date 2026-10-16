from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class TicketCreate(BaseModel):
    title: str = Field(min_length=5, max_length=150)
    description: str = Field(min_length=10, max_length=5000)
    priority: Literal["low", "medium", "high"] = "medium"


class TicketUpdate(BaseModel):
    status: Literal["open", "in_progress", "resolved"] | None = None
    priority: Literal["low", "medium", "high"] | None = None


class TicketResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    owner_id: str
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    message: str = Field(min_length=1, max_length=2000)



class CommentResponse(BaseModel):
    id: str
    ticket_id: str
    author_id: str
    author_name: str
    author_role: str
    message: str
    created_at: datetime
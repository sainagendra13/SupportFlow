
from typing import Literal
from uuid import uuid4
from fastapi import APIRouter, Depends, Query
from app.config import settings
from app.csrf import require_csrf
from app.authorisation import get_current_user,require_customer,require_agent
from app.schemas.ticket import TicketCreate,TicketUpdate,TicketResponse
from app.services import ticketservice
from app.tasks.notification import ticket_updated


router = APIRouter(prefix="/api/tickets",tags=["Tickets"],dependencies=[Depends(require_csrf)])


@router.post("",response_model=TicketResponse,status_code=201)
async def create_ticket(data: TicketCreate,user=Depends(require_customer)):
    return await ticketservice.create_ticket(data, user)


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    status: Literal["open", "in_progress", "resolved"] | None = None,
    priority: Literal["low", "medium", "high"] | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user=Depends(get_current_user),
):
    return await ticketservice.list_tickets(user,status,priority,skip,limit)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str,user=Depends(get_current_user)):
    ticket = await ticketservice.get_accessible_ticket(ticket_id,user)
    return ticketservice.serialize(ticket)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str,data: TicketUpdate,agent=Depends(require_agent)):
    ticket = await ticketservice.update_ticket(ticket_id,data)

    if settings.enable_jobs:
        try:
            ticket_updated.delay(
                ticket["id"],
                ticket["owner_id"],
                data.model_dump(exclude_none=True),
                str(uuid4()),
            )
        except Exception:
            pass
    return ticket

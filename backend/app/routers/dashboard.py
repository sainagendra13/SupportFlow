from fastapi import APIRouter, Depends
from app.authorisation import get_current_user
from app.services.ticketservice import get_dashboard_stats


router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def dashboard_stats(user=Depends(get_current_user)):
    return await get_dashboard_stats(user)

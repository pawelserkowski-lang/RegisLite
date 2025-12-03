from fastapi import APIRouter

router = APIRouter()


@router.get("/signal/ping")
async def signal_ping():
    """Prosty endpoint testowy dla RTC / API."""
    return {"status": "ok", "message": "Regis RTC online"}

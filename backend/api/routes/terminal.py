"""
Terminal & Scan Log Route Handler.
GET    /api/terminal - Returns real-time log event stream with timestamps.
DELETE /api/terminal - Clears the log buffer.
"""
from typing import List
from fastapi import APIRouter
from backend.api.state import state
from backend.api.schemas import TerminalLogItem

router = APIRouter(prefix="/api/terminal", tags=["terminal"])


@router.get("", response_model=List[TerminalLogItem])
def get_terminal_logs():
    return [TerminalLogItem(**item) for item in state.scan_logs]


@router.delete("")
def clear_terminal_logs():
    state.scan_logs.clear()
    state.log_event("INFO", "Terminal log buffer cleared by operator.")
    return {"message": "Logs cleared"}

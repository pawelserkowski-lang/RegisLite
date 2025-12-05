from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

class WSMessage(BaseModel):
    """Model wiadomości WebSocket."""
    type: Literal["log", "progress", "result", "error"]
    content: str
    meta: dict[str, Any] = Field(default_factory=dict)

class UploadResponse(BaseModel):
    session_id: str
    message: str
    workspace_path: str

class HealthCheck(BaseModel):
    status: str
    version: str
    mode: str

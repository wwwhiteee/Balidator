"""Pydantic models for API payloads."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class OEEData(BaseModel):
    """OEE metrics returned by the API."""

    availability: float
    performance: float
    quality: float
    oee: float

class ParadaCreate(BaseModel):
    seccion: str
    motivo: str
    timestamp_inicio: Optional[datetime] = None
    timestamp_fin: Optional[datetime] = None

class ParadaResponse(ParadaCreate):
    id: int

class UserOut(BaseModel):
    username: str
    role: Optional[str]

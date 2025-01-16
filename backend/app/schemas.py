# backend/app/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ContractBase(BaseModel):
    file_name: Optional[str]

class ContractCreate(ContractBase):
    original_text: str

class ContractResponse(ContractBase):
    id: int
    original_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContractRevisionBase(BaseModel):
    revision_text: str
    revision_notes: Optional[str] = None

class ContractRevisionCreate(ContractRevisionBase):
    pass

class ContractRevisionResponse(ContractRevisionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ContractDetailResponse(ContractResponse):
    revisions: List[ContractRevisionResponse] = []

class ReviewRequest(BaseModel):
    instructions: Optional[str] = None
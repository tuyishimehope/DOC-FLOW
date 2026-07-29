from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict
class Processing_Type(str, Enum):
    DOCUMENT_SUMMARY = "DOCUMENT_SUMMARY"
    INVOICE_EXTRACTION = "INVOICE_EXTRACTION"
    CONTRACT_METADATA = "CONTRACT_METADATA"
    

class Processing_status(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    

class Document_Status(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"

class Processing_Job_Status(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"
    
class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes= True)
    
    id: int
    name: str
    status: Document_Status
    file_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
class PaginatedDocumentResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
    
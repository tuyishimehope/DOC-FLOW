from enum import Enum

    
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
from fastapi import APIRouter, UploadFile, status, File, Depends, Request, HTTPException

from app.config.env_config import settings
from app.config.log_config import logger
from app.exceptions.domain import AppError
from app.schemas.core.ingestion import IngestionRequest
from app.services.ingestion_service import ingestion_service
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["rag"])

def get_ingestion_request(file: UploadFile = File(...)) -> IngestionRequest:
  """Create an ingestion request from an uploaded file.

  Args:
    file: File uploaded via multipart form.

  Returns:
    IngestionRequest wrapping the file.
  """
  return IngestionRequest(file=file)


@router.post('/upload', status_code=status.HTTP_201_CREATED)
async def ingest_file(file_data: IngestionRequest = Depends(get_ingestion_request), db: Session = Depends(get_db)):
  """ Upload a file and index it 
  
  Args:
    request: IngestionRequest with uploaded file

  Returns:
    IngestionResponse wit message, file_path and filename

  """
  file = file_data.file
  structrued_data = ingestion_service.save_and_process_file(file, db)
  return structrued_data
  
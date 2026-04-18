from fastapi import UploadFile
from pydantic import BaseModel, Field, ConfigDict

class IngestionRequest(BaseModel):
  """Request body for file ingestion endpoint."""
  file: UploadFile = Field(..., description="File to Upload")
  model_config = ConfigDict(arbitrary_types_allowed=True)

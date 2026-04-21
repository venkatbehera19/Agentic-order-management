from fastapi import UploadFile
from app.config.log_config import logger
from app.exceptions import InternalServerError, ValidationError
from app.utils.pdf_plumber_utils import PdfPlumberUtils
from app.utils.file_utils import FileProcessor
from app.repository.qdrant_repo import QdrantRepository
from app.utils.embedding_utils import embeddings_client
from app.constants.app_constants import VECTOR_DB
from app.repository.mysql.inventory_repo import InventoryRepository

qdrant_db = QdrantRepository(embeddings=embeddings_client, collection_name=VECTOR_DB.COLLECTION_NAME.value)

class IngestionService:
  """This service is used for file storage and indexing"""

  def save_and_process_file(self, file:UploadFile, db) -> str:
    """Save the file to the upload directory
    
    Args:
      file: the uploaded file to save

    Returns: 
      path where the file was save

    Raises:
      ValidationError: If file save fails.
      InternalError: If unexpected error occurs.
    """
    try:
      file_processor = FileProcessor(file=file)
      file_processor.get_file_name()
      file_processor.get_file_extension()
      file_path = file_processor.get_file_path()
      file_processor.save_file(file_path)
      pdf_plumber_text = PdfPlumberUtils(file_path)
      text_data = pdf_plumber_text.process()

      # handle the 
      inventory_sql_db = InventoryRepository(db)
      inventory_sql_db.bulk_insert(text_data)
      records = inventory_sql_db.get_product_mappings()
      logger.info(f"RES {records}")
      qdrant_db.add_documents(text_data, records)
      return text_data

    except (OSError, IOError) as e:
      logger.info('ERRROR while saving the file:  %s', e)
      raise ValidationError('File Upload Fail') from e
    except Exception as e:
      logger.exception("Unexpected error saving file: %s", e)
      raise InternalServerError('file upload fail') from e
    

ingestion_service = IngestionService()
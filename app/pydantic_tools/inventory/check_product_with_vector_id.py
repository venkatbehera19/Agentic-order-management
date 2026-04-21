from langchain.tools import BaseTool
from pydantic import Field
from app.config.log_config import logger
from app.db.database import SessionLocal
from app.repository.mysql.inventory_repo import InventoryRepository


class CheckProductExistsWithVectorID(BaseTool):
    """Tool to check whether a product exists in inventory table using vector_id"""

    name: str = "check_product_exists_with_vector_id"
    description: str = "check if a product exists in inventory using vector_id"

    vector_id: str = Field(...)

    def _run(self) -> dict:
        logger.info(f"Checking product exists for ID: {self.vector_id}")

        try:
            with SessionLocal() as db:
                repo = InventoryRepository(db)
                exists = repo.check_product_exists_using_vector_id(self.vector_id)
                return {
                    "success": True,
                    "data": {"exists": exists},
                    "error": None
                }

        except Exception as e:
            logger.exception("Error checking product existence")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
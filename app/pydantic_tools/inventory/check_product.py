from langchain.tools import BaseTool
from pydantic import Field
from app.config.log_config import logger
from app.db.database import SessionLocal
from app.repository.mysql.inventory_repo import InventoryRepository

class CheckproductExistsTool(BaseTool):
    """Tool to check whether a product exists in inventory table"""

    name: str = "check_product_exists"
    description: str = "check if a product exists in inventory using prosuct_id"

    product_id: int = Field(..., description="Id of the product")


    def _run(self) -> dict:
        logger.info(f"Checking product exists for ID: {self.product_id}")

        try:
            with SessionLocal() as db:
                repo = InventoryRepository(db)
                exists = repo.check_product_exists(self.product_id)
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
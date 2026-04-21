from langchain.tools import BaseTool
from pydantic import Field
from app.config.log_config import logger
from app.db.database import SessionLocal
from app.repository.mysql.inventory_repo import InventoryRepository


class GetProductExistsWithVectorID(BaseTool):
    """Tool to get a product from inventory table using vector_id"""

    name: str = "get_product"
    description: str = "get the product from inventory using vector_id"

    vector_id: str = Field(...)

    def _run(self) -> dict:
        logger.info(f"getting product using vector ID: {self.vector_id}")

        try:
            with SessionLocal() as db:
                repo = InventoryRepository(db)
                product = repo.get_product(self.vector_id)
                return {
                    "success": True,
                    "data": {"product": product},
                    "error": None
                }

        except Exception as e:
            logger.exception("Error getting the product ")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
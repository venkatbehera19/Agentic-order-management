from langchain.tools import BaseTool
from pydantic import Field
from app.config.log_config import logger
from app.db.database import SessionLocal
from app.repository.mysql.inventory_repo import InventoryRepository


class UpdateStock(BaseTool):
    """Tool to update the stock of the product from inventory table using vector_id"""

    name: str = "update_stock"
    description: str = "update stock of the product in the inventory table"

    vector_id: str = Field(...)
    quantity: int = Field(..., description="Quantity to update")
    operation: str = Field(..., description="increase or decrease")

    def _run(self) -> dict:
        logger.info(f"Updating stock for vector_id: {self.vector_id}")

        try:
            with SessionLocal() as db:
                repo = InventoryRepository(db)
                product, error = repo.update_stock(
                    vector_id = self.vector_id,
                    quantity= self.quantity,
                    operation= self.operation
                )

                if error:
                    return {
                        "success": False,
                        "data": None,
                        "error": error
                    }
                
                return {
                    "success": True,
                    "data": {
                        "vector_id": product.vector_id,
                        "productName": product.productName,
                        "quantityAvailable": product.quantityAvailable
                    },
                    "error": None
                }

        except Exception as e:
            logger.exception("Error updating the product ")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
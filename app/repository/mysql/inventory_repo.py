from app.models.inventory import Inventory
from sqlalchemy.orm import Session
from datetime import datetime
from app.config.log_config import logger

class InventoryRepository:
    """All the opertaions related to inventory table"""

    def __init__(self, db: Session): 
        self.db = db
        logger.info(f"LOGGER InventoryRepository, :{self.db}")
        
    def check_product_exists(self, product_id: int) -> bool:
        """check that product is there or not using product_id
        
        Args:
            productId: id of the product

        Returns:
            if present return a boolean value
        """
        try:
            return self.db.query(Inventory).filter(
                Inventory.productId == product_id
            ).first is not None

        except Exception as e:
            logger.info(f"Getting the error while finding the product - {str(e)}")

    def check_product_exists_using_vector_id(self, vector_id: str) -> bool:
        """check that product is there or not using vector_id
        
        Args:
            vector_id: id of the vector product

        Returns:
            if present return a boolean value
        """
        try:
            return self.db.query(Inventory).filter(
                Inventory.vector_id == vector_id
            ).first is not None

        except Exception as e:
            logger.info(f"Getting the error while finding the product - {str(e)}")
            return False

    def get_product(self, vector_id: str):
        """fetch the product using vector_id
        
        Args:
            vector_id: id of the vector product

        Returns:
            if present return the product
        """
        try:
            return self.db.query(Inventory).filter(
                Inventory.vector_id == vector_id
            ).first

        except Exception as e:
            logger.info(f"Getting the error while finding the product - {str(e)}")
            return None

    def update_stock(self, vector_id: str, quantity: int, operation: str):
        """update the product using vector_id
        
        Args:
            vector_id: id of the vector product

        Returns:
            if present return the product
        """
        try:
            product = self.db.query(Inventory).filter(
                Inventory.vector_id == vector_id
            ).first()

            if not product:
                return None, "Product not found"
            
            if operation == "increase":
                product.quantityAvailable += quantity

            if operation == "decrease":
                if product.quantityAvailable < quantity:
                    return None, "Insufficient stock"
                product.quantityAvailable -= quantity
            else:
                return None, "Invalid operations"

            self.db.commit()
            self.db.refresh(product)

            return product, None


        except Exception as e:
            logger.info(f"Getting the error while finding the product - {str(e)}")
            return None



    def create_products(self, product: dict):
        item = Inventory(
            productName=product["name"],
            price=self.parse_price(product["price"]),
            quantityAvailable=10,
            about=product["about"],
            description=product["description"],
            specification=product["specification"],
            source=product["source"],
            page=product["page"],
            vector_id=product["id"]
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return item
    
    def bulk_insert(self, products: list):

        for product in products:
            price = float(product["price"].replace(",", ""))

            self.db.add(Inventory(
                productName=product["name"],
                quantityAvailable=10,
                price=price,
            ))

        self.db.commit()


    def get_product_mappings(self):
        records = self.db.query(
            Inventory.productID,
            Inventory.productName
        ).all()

        return [{ 
            "product_id": r.productID,
            "name": r.productName
        } for r in records]
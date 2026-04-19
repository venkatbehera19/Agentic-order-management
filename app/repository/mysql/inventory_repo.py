from app.models.inventory import Inventory
from sqlalchemy.orm import Session
from datetime import datetime
from app.config.log_config import logger

class InventoryRepository:
    """All the opertaions related to inventory table"""

    def __init__(self, db: Session): 
        self.db = db
        logger.info(f"LOGGER InventoryRepository, :{self.db}")
        

    def parse_price(self, price_str):
        return float(price_str.replace(",", ""))

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
            existing = self.db.query(Inventory).filter(
                Inventory.vector_id == product["id"]
            ).first()

            price = float(product["price"].replace(",", ""))

            if existing:
                existing.price = price
                existing.about = product.get("about")
                existing.description = product.get("description")
                existing.specification = product.get("specification")
                existing.source = product.get("source")
                existing.page = product.get("page")
                existing.lastUpdated = datetime.utcnow()

            else:
                self.db.add(Inventory(
                    vector_id=product["id"],
                    productName=product["name"],
                    quantityAvailable=10,
                    price=price,
                    category=None,
                    about=product.get("about"),
                    description=product.get("description"),
                    specification=product.get("specification"),
                    source=product.get("source"),
                    page=product.get("page"),
                    lastUpdated=datetime.utcnow()
                ))

        self.db.commit()



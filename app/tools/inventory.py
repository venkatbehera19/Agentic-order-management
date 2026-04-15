from sqlalchemy import text
from app.db.database import SessionLocal
from app.config.log_config import logger

def check_product_exists(product_id: int) -> dict:
    """Check weather that product is present in db using product_id
    
    Args:
        product_id: id of the product

    Returns:
        dict with exists key
    """
    logger.info(f"checking product exists")
    with SessionLocal() as session:
        result = session.execute(
            text("SELECT 1 FROM inventory WHERE productID = :pid"),
            {"pid": product_id}
        ).fetchone()

        return {
            "success": True,
            "data": {"exists": result is not None},
            "error": None
        }
    
    
def get_stock_quantity(product_id: int) -> dict:
    "fetch the stock quantity in the inventory"
    logger.info(f"checking stock quanity")

    with SessionLocal() as session:
        result = session.execute(
            text("SELECT quantityAvailable FROM inventory WHERE productID = :pid"),
            {"pid": product_id}
        ).fetchone()

        if not result:
            return {
                "success": False,
                "data": None,
                "error": "Product not found"
            }
        
        return {
            "success": True,
            "data": {"stock": result[0]},
            "error": None
        }
    

def update_inventory(product_id: int, quantity: int) -> dict:
    """update the product inventory"""
    logger.info(f"updating product inventory")
    with SessionLocal() as session:
        try:
            session.execute(
                text(
                    """
                    UPDATE inventory
                    SET quantityAvailable = quantityAvailable - :qty
                    WHERE productID = :pid
                """),
                {
                    "qty": quantity, "pid": product_id
                }
            )
            session.commit()
            return {
                "success": True,
                "data": None,
                "error": None
            }
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
        
def get_product_id_by_name(product_name: str) -> dict:
    """
    Fetch productID from inventory using product name (LIKE search)
    """
    logger.info(f"Fetching product_id for product_name={product_name}")
    with SessionLocal() as session:
        try:
            result = session.execute(
                text("""
                    SELECT productID, productName 
                    FROM inventory 
                    WHERE LOWER(productName) LIKE LOWER(:name)
                    LIMIT 1
                """),
                {"name": f"%{product_name}%"}
            ).fetchone()

            if not result:
                return {
                    "success": False,
                    "data": None,
                    "error": "Product not found"
                }
            
            return {
                "success": True,
                "data": {
                    "product_id": result[0],
                    "product_name": result[1]
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Product lookup failed: {str(e)}")

            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
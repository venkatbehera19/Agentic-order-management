from sqlalchemy import text
from app.db.database import SessionLocal

def check_product_exists(product_id: int) -> dict:
    """Check weather that product is present in db using product_id
    
    Args:
        product_id: id of the product

    Returns:
        dict with exists key
    """
    with SessionLocal() as session:
        result = session.execute(
            text("SELECT 1 FROM inventory WHERE productID = :pid"),
            {"pid": product_id}
        ).fetchone()

        return {
            "exists": result is not None
        }
    
    
def get_stock_quantity(product_id: int) -> dict:
    "fetch the stock quantity in the inventory"
    with SessionLocal() as session:
        result = session.execute(
            text("SELECT stockQuantity FROM inventory WHERE productID = :pid"),
            {"pid": product_id}
        ).fetchone()

        if not result:
            return {"error": "Product not found"}
        
        return { "stock": result[0] }
    

def update_inventory(product_id: int, quantity: int) -> dict:
    """update the product inventory"""
    with SessionLocal() as session:
        try:
            session.execute(
                text(
                    """
                    UPDATE inventory
                    SET stockQuantity = stockQuantity - :qty
                    WHERE productID = :pid
                """),
                {
                    "qty": quantity, "pid": product_id
                }
            )
            session.commit()
            return {"status": "success"}
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
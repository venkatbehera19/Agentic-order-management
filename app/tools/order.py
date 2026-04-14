from sqlalchemy import text
from app.db.database import SessionLocal
from app.config.log_config import logger

def create_order(product_id: int, quantity: int) -> dict:
    """create the order"""
    logger.info(f"Creating order for product_id={product_id}, quantity={quantity}")
    with SessionLocal() as session:
        try:
            result = session.execute(
                text(
                    """
                    INSERT INTO orders (productID, quantity, status, remarks, orderDate)
                    VALUES (:pid, :qty, 'PLACED', 'Order created', NOW())
                """
                ), {"pid": product_id, "qty": quantity}
            )
            session.commit()
            order_id = result.lastrowid
            return {
                "success": True,
                "data": {"order_id": order_id},
                "error": None
            }

        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
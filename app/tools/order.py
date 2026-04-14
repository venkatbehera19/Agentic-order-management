from sqlalchemy import text
from app.db.database import SessionLocal

def create_order(product_id: int, quantity: int) -> dict:
    """create the order"""
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
            return { "order_id": order_id }

        except Exception as e:
            session.rollback()
            return {"error": str(e)}
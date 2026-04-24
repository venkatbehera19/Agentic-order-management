from sqlalchemy import text
from app.db.database import SessionLocal
from app.config.log_config import logger
from app.models.order import Order
from sqlalchemy.exc import SQLAlchemyError

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
            logger.info(f"CREATE ORDER {order_id}")
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
        
def get_order_by_id(order_id: int):
    db = SessionLocal()
    try:
        order = (
            db.query(Order)
            .filter(Order.orderID == order_id)
            .first()
        )



        if not order:
            return {
                "success": False,
                "error": f"Order {order_id} not found"
            }

        return {
            "success": True,
            "data": {
                "order_id": order.orderID,
                "product_id": order.productID,
                "quantity": order.quantity,
                "status": order.status
            }
        }

    except SQLAlchemyError as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        db.close()

def cancel_order_in_db(order_id: int):
    db = SessionLocal()
    try:
        order = (
            db.query(Order)
            .filter(Order.order_id == order_id)
            .first()
        )

        if not order:
            return {"success": False, "error": "Order not found"}

        if order.status == "CANCELLED":
            return {"success": False, "error": "Already cancelled"}

        order.status = "CANCELLED"

        db.commit()

        return {"success": True}

    except SQLAlchemyError as e:
        db.rollback()
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        db.close()
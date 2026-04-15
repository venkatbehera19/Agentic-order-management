from sqlalchemy import text
from app.db.database import SessionLocal
from app.config.log_config import logger

def log_order_audit(order_id: int, prev_status: str, new_status: str, remarks: str) -> dict:
    """"""
    logger.info(f"Log Order audit")
    with SessionLocal() as session:
        try:
            session.execute(
                text("""
                    INSERT INTO order_audit (orderID, previousStatus, newStatus, timestamp, remarks)
                    VALUES (:oid, :prev, :new, NOW(), :remarks)
                """),
                {
                    "oid": order_id,
                    "prev": prev_status,
                    "new": new_status,
                    "remarks": remarks
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
        
def log_inventory_audit(
    product_id: int,
    change_type: str,
    quantity_changed: int,
    remarks: str
) -> dict:
    """
    Log inventory changes into inventory_audit table
    """

    logger.info(f"Logging inventory audit for product_id={product_id}")
    with SessionLocal() as session:
        logger.info(f"Logging inventory audit SessionLocal product_id={product_id}, {quantity_changed}, {remarks}")

        try:
            result = session.execute(
                text("""
                    INSERT INTO inventory_audit
                    (productID, changeType, quantityChanged, timestamp, remarks)
                    VALUES (:pid, :ctype, :qty, NOW(), :remarks)
                """),
                {
                    "pid": product_id,
                    "ctype": change_type,
                    "qty": quantity_changed,
                    "remarks": remarks
                }
            )

            session.commit()

            logger.info(f"LOG Inventoy {result.lastrowid}")

            return {
                "success": True,
                "data": None,
                "error": None
            }

        except Exception as e:
            logger.error(f"Inventory audit failed: {str(e)}")

            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
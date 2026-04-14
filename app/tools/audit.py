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
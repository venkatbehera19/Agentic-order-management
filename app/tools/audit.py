from sqlalchemy import text
from app.db.database import SessionLocal

def log_order_audit(order_id: int, prev_status: str, new_status: str, remarks: str) -> dict:
    """"""
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

            return {"status": "logged"}
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
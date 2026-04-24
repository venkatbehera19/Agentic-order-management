from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column("orderID", Integer, primary_key=True, index=True, autoincrement=True)

    product_id = Column("productID", Integer, ForeignKey("inventory.productID", ondelete="SET NULL"), nullable=True)

    quantity = Column(Integer, nullable=False)

    status = Column(String(50), default="CREATED")

    remarks = Column(String(255), nullable=True)

    order_date = Column("orderDate", TIMESTAMP, server_default=func.current_timestamp())

    # Optional relationship (useful later)
    product = relationship("Inventory", back_populates="orders")
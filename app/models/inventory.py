from sqlalchemy import Column, Integer, String, Float, JSON, TIMESTAMP
from datetime import datetime
from app.db.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    productID = Column(Integer, primary_key=True, index=True)

    productName = Column(String, index=True)
    quantityAvailable = Column(Integer, default=10)

    price = Column(Float)

    lastUpdated = Column(TIMESTAMP, default=datetime.utcnow)
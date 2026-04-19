from sqlalchemy import Column, Integer, String, Float, JSON, TIMESTAMP
from datetime import datetime
from app.db.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    productId = Column(Integer, primary_key=True, index=True)

    productName = Column(String, index=True)
    quantityAvailable = Column(Integer, default=10)

    price = Column(Float)
    category = Column(String)

    about = Column(String)
    description = Column(String)
    specification = Column(JSON)

    source = Column(String)       
    page = Column(Integer)

    vector_id = Column(String, unique=True)

    lastUpdated = Column(TIMESTAMP, default=datetime.utcnow)
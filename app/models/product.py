from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON  # ✅ Add JSON


Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    category = Column(String)
    sku = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    status = Column(String, default="publish")
    stock_status = Column(String, default="instock") 
    image = Column(String)  # Primary image URL
    images = Column(JSON)   # Array of all image URLs (requires JSON column type)


    url = Column(String)        # ✅ ADD THIS
    slug = Column(String)       # ✅ ADD THIS

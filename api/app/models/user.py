from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    stripe_customer_id = Column(String, unique=True, index=True)
    subscription_plan = Column(String, default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    usage_records = relationship("UsageRecord", back_populates="user")
    instances = relationship("Instance", back_populates="user")

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model = Column(String)
    tokens_used = Column(Integer)
    cost = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="usage_records")

class Instance(Base):
    __tablename__ = "instances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    status = Column(String)  # running, stopped, etc.
    instance_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    
    user = relationship("User", back_populates="instances")
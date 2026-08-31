from sqlalchemy import Boolean, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    stripe_customer_id = Column(String, unique=True, index=True)
    subscription_plan = Column(String, default="free")
    subscription_status = Column(String, default="incomplete")  # active, past_due, canceled, incomplete
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # FAX設定（BYOK - Bring Your Own Key）
    telnyx_api_key = Column(String, nullable=True)
    telnyx_connection_id = Column(String, nullable=True)
    telnyx_from = Column(String, nullable=True)
    
    phaxio_api_key = Column(String, nullable=True)
    phaxio_api_secret = Column(String, nullable=True)
    
    # リレーションシップ
    usage_records = relationship("UsageRecord", back_populates="user")
    instances = relationship("Instance", back_populates="user")
    fax_usage_records = relationship("FaxUsageRecord", back_populates="user")

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

class FaxUsageRecord(Base):
    __tablename__ = "fax_usage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    fax_id = Column(String)
    provider = Column(String)
    to_number = Column(String)
    pages = Column(Integer, default=1)
    cost_credits = Column(Integer, default=1)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="fax_usage_records")
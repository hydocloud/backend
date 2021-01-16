from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from pydantic import BaseModel, Field
from models.authorization import Base


class Devices(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    serial = Column(String, unique=True)
    name = Column(String)
    device_group_id = Column(Integer)
    hmac_key = Column(LargeBinary)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class DevicesModel(BaseModel):
    id: int
    name: str
    serial: str
    device_group_id: int = Field(..., alias="deviceGroupId")
    hmac_key: str = Field(..., alias="hmacKey")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

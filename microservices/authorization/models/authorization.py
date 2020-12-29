import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from typing import Optional

Base = declarative_base()


class Authorization(Base):
    __tablename__ = "authorizations"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True))
    device_id = (Column(Integer),)
    access_time = Column(Integer)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class AuthorizationModel(BaseModel):
    id: int
    user_id: uuid.UUID
    device_id: int
    access_time: Optional[int]
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class AuthorizationModelShort(BaseModel):
    id: int
    user_id: uuid.UUID = Field(..., alias="userId")
    device_id: int = Field(..., alias="deviceId")
    access_time: Optional[int] = Field(..., alias="accessTime")
    start_time: datetime = Field(default_factory=datetime.utcnow, alias="startTime")
    end_time: Optional[datetime] = Field(..., alias="endTime")

    class Config:
        allow_population_by_field_name = True


class AuthorizationModelApiInput(BaseModel):
    userId: uuid.UUID
    deviceId: int = Field(..., alias="deviceId")
    accessTime: Optional[int]
    startTime: datetime = Field(default_factory=datetime.utcnow)
    endTime: Optional[datetime]

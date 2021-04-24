import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Authorization(Base):
    __tablename__ = "authorizations"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True))
    device_id = Column(Integer)
    access_limit = Column(Integer)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class AuthorizationModel(BaseModel):
    id: int
    user_id: uuid.UUID
    device_id: int
    access_limit: Optional[int]
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
    access_limit: Optional[int] = Field(..., alias="accessLimit")
    start_time: datetime = Field(default_factory=datetime.utcnow, alias="startTime")
    end_time: Optional[datetime] = Field(..., alias="endTime")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class AuthorizationModelApiInput(BaseModel):
    userId: uuid.UUID
    deviceId: int = Field(..., alias="deviceId")
    accessLimit: Optional[int]
    startTime: datetime = Field(default_factory=datetime.utcnow)
    endTime: Optional[datetime]


class AuthorizationModelParameters(BaseModel):
    authorizationId: Optional[int]
    userId: Optional[uuid.UUID]
    deviceId: Optional[int]
    pageNumber: Optional[int] = Field(default=1)
    pageSize: Optional[int] = Field(default=5)

    @root_validator(pre=True)
    def authorization_id_user_id_device_id(cls, values):
        if values.get("authorizationId") is not None and (
            values.get("deviceId") is not None or values.get("userId") is not None
        ):
            raise ValueError("incompatible input")
        return values

    @root_validator(pre=True)
    def user_id_device_id(cls, values):
        if (
            values.get("authorizationId") is None
            and values.get("deviceId") is None
            and values.get("userId") is None
        ):
            raise ValueError("incompatible input")
        return values


class Unlock(BaseModel):
    userId: Optional[uuid.UUID]
    deviceSerial: uuid.UUID
    message: str
    deviceNonce: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

Base = declarative_base()


class DeviceGroups(Base):
    __tablename__ = "device_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organization_id = Column(Integer)
    owner_id = Column(UUID(as_uuid=True))
    devices = relationship("Devices", cascade="all, delete")
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class Devices(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    serial = Column(String)
    device_group_id = Column(Integer, ForeignKey("device_groups.id"), unique=True,)
    owner_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class DeviceGroupsModel(BaseModel):
    id: int
    name: str
    organization_id: int
    owner_id: uuid.UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True


class DeviceGroupsModelShort(BaseModel):
    id: int
    name: str
    organization_id: int = Field(..., alias="organizationId")
    owner_id: uuid.UUID = Field(..., alias="ownerId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class DevicesModel(BaseModel):
    id: int
    serial: str
    device_group_id: int = Field(..., alias="deviceGroupId")
    owner_id: uuid.UUID = Field(..., alias="ownerId")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class DevicesModelShort(BaseModel):
    id: int
    serial: str
    device_group_id: int = Field(..., alias="deviceGroupId")
    owner_id: uuid.UUID = Field(..., alias="ownerId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class DeviceGroupsApiInput(BaseModel):
    name: str
    organizationId: int


class DeviceGroupsApiEditInput(BaseModel):
    name: str

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, root_validator
from typing import Optional

Base = declarative_base()
secret_key = "secretkey1234"


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
    serial = Column(String, unique=True)
    name = Column(String)
    device_group_id = Column(
        Integer,
        ForeignKey("device_groups.id"),
    )
    hmac_key = Column(LargeBinary)
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
    name: str
    serial: str
    device_group_id: int = Field(..., alias="deviceGroupId")
    hmac_key: str = Field(..., alias="hmacKey")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class DevicesModelShort(BaseModel):
    id: int
    name: str
    serial: str
    device_group_id: int = Field(..., alias="deviceGroupId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class DeviceGroupsApiInput(BaseModel):
    name: str
    organizationId: int


class DeviceGroupsApiEditInput(BaseModel):
    name: str


class DevicesApiInput(BaseModel):
    name: str
    serial: str
    deviceGroupId: int
    hmacKey: str


class DevicesEditInput(BaseModel):
    name: Optional[str]
    deviceGroupId: Optional[int]


class DevicesModelParameters(BaseModel):
    deviceId: Optional[int]
    deviceGroupId: Optional[int]
    organizationId: Optional[int]
    pageNumber: Optional[int] = Field(default=1)
    pageSize: Optional[int] = Field(default=5)

    @root_validator(pre=True)
    def organization_id_device_group_id(cls, values):
        if (
            values.get("deviceGroupId") is not None
            and values.get("organizationId") is not None
        ):
            raise ValueError("incompatible input")
        if values.get("organizationId") is None and values.get("deviceGroupId") is None:
            raise ValueError("incompatible input")
        return values

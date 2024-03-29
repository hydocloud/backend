import uuid
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional
from pydantic import BaseModel, Field

Base = declarative_base()


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    license_id = Column(Integer)
    owner_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class OrganizationQuery(BaseModel):
    id: int


class OrganizationBase(BaseModel):
    name: str
    licenseId: int


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationComplete(OrganizationBase):
    id: int

    class Config:
        orm_mode = True


class ResponseModel(BaseModel):
    id: int
    name: str
    license_id: int = Field(..., alias="licenseId")
    owner_id: uuid.UUID = Field(..., alias="ownerId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class OrganizationsUpdate(BaseModel):
    name: Optional[str] = None
    licenseId: Optional[int] = None

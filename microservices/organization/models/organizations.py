
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from typing import Union, List, Optional
from pydantic import BaseModel
import uuid
Base = declarative_base()

class Organization(Base):
    __tablename__ = 'organizations'

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
    licenseId: int
    ownerId: uuid.UUID
    
class OrganizationsList(BaseModel):
    organizations: List[ResponseModel]
    total: Optional[int] = None
    nextPage: Optional[int] = None
    previousPage: Optional[int] = None
    totalPages: Optional[int] = None

class OrganizationsUpdate(BaseModel):
    name: Optional[str] = None
    licenseId: Optional[int] = None
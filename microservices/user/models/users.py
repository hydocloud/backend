from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserGroups(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    organization_id = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class UserBelongUserGroups(Base):
    __tablename__ = "user_belong_user_groups"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True))
    user_group_id = Column(
        Integer,
        ForeignKey("user_groups.id"),
        unique=True,
    )
    attributes = Column(String)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    user_groups = relationship("UserGroups", back_populates = "user_belong_user_groups")


UserGroups.user_belong_user_groups = relationship("UserBelongUserGroups", order_by=UserBelongUserGroups.id, back_populates="UserGroups")
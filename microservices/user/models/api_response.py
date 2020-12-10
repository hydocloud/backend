from pydantic import BaseModel
from typing import List, Optional
from models.users import UserGroupsModelShort, UserBelongUserGroups


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class UserGroupsList(BaseModel):
    userGroups: List[UserGroupsModelShort]


class Message(BaseModel):
    message: str


class DataModel(BaseModel):
    data: UserGroupsList
    total: int = None
    nextPage: int = None
    previousPage: int = None
    totalPages: int = None

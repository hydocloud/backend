from pydantic import BaseModel
from typing import List, Optional
from models.users import UserGroupsModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class UserGroupsList(BaseModel):
    userGroups: List[UserGroupsModelShort]


class Message(BaseModel):
    message: str


class DataModel(BaseModel):
    data: UserGroupsList
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]

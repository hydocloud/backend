from pydantic import BaseModel
from typing import List, Optional
from models.users import UserGroupsModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class Message(BaseModel):
    message: str


class DataModel(BaseModel):
    data: List[UserGroupsModelShort]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]

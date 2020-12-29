from pydantic import BaseModel
from typing import List, Optional
from models.authorization import AuthorizationModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class AuthorizationList(BaseModel):
    authorizations: List[AuthorizationModelShort]


class Message(BaseModel):
    message: str


class DataModel(BaseModel):
    data: AuthorizationList
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]

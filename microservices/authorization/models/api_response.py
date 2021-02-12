from pydantic import BaseModel
from typing import List, Optional
from models.authorization import AuthorizationModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class Message(BaseModel):
    message: str


class DataModel(BaseModel):
    data: List[AuthorizationModelShort]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]


class UnlockModel(BaseModel):
    success: bool
    message: Optional[str]
    digest: Optional[str]

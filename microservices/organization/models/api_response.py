from typing import Any, Optional, List
from pydantic import BaseModel
from models.organizations import ResponseModel


class Message(BaseModel):
    message: Any


class Data(BaseModel):
    data: List[ResponseModel]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]


class LambdaSuccessResponse(BaseModel):
    statusCode: int
    body: Data


class LambdaSuccessResponseWithoutData(BaseModel):
    statusCode: int
    body: Message


class LambdaErrorResponse(BaseModel):
    statusCode: int
    body: Message

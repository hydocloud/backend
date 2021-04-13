from typing import Any, Optional, List
from pydantic import BaseModel
from models.organizations import ResponseModel


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class Message(BaseModel):
    message: str


class Data(BaseModel):
    data: List[ResponseModel]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]

class DataNoList(BaseModel):
    data: ResponseModel


class LambdaSuccessResponse(BaseModel):
    statusCode: int
    body: Data


class LambdaSuccessResponseWithoutData(BaseModel):
    statusCode: int
    body: Message


class LambdaErrorResponse(BaseModel):
    statusCode: int
    body: Message

from typing import Any
from pydantic import BaseModel
from models.organizations import OrganizationsList


class Message(BaseModel):
    message: Any


class Data(BaseModel):
    data: OrganizationsList


class LambdaSuccessResponse(BaseModel):
    statusCode: int
    body: Data


class LambdaSuccessResponseWithoutData(BaseModel):
    statusCode: int
    body: Message


class LambdaErrorResponse(BaseModel):
    statusCode: int
    body: Message

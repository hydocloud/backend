from typing import Optional, List
from pydantic import BaseModel
from models.organizations import ResponseModel
from models.devices import DeviceGroupsModelShort, DevicesModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class Message(BaseModel):
    message: str


class Data(BaseModel):
    data: List[ResponseModel or DeviceGroupsModelShort or DevicesModelShort]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]


class DataNoList(BaseModel):
    data: ResponseModel or DeviceGroupsModelShort or DevicesModelShort


class LambdaSuccessResponse(BaseModel):
    statusCode: int
    body: Data


class LambdaSuccessResponseWithoutData(BaseModel):
    statusCode: int
    body: Message


class LambdaErrorResponse(BaseModel):
    statusCode: int
    body: Message

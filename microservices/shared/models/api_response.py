from typing import Optional, List, Union
from pydantic import BaseModel
from models.organizations import ResponseModel
from models.devices import DeviceGroupsModelShort, DevicesModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class Message(BaseModel):
    message: str


class Data(BaseModel):
    data: List[Union[ResponseModel, DevicesModelShort, DeviceGroupsModelShort]]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]


class DataNoList(BaseModel):
    data: Union[ResponseModel, DevicesModelShort, DeviceGroupsModelShort]


class LambdaSuccessResponse(BaseModel):
    statusCode: int
    body: Data


class LambdaSuccessResponseWithoutData(BaseModel):
    statusCode: int
    body: Message


class LambdaErrorResponse(BaseModel):
    statusCode: int
    body: Message

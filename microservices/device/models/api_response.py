from pydantic import BaseModel
from typing import List, Optional
from models.devices import DeviceGroupsModelShort, DevicesModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class Message(BaseModel):
    message: str


class DataModel(BaseModel):
    data: List[DeviceGroupsModelShort]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]


class DataModelNoList(BaseModel):
    data: DeviceGroupsModelShort


class DevicesDataModel(BaseModel):
    data: List[DevicesModelShort]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]


class DevicesDataNoList(BaseModel):
    data: DevicesModelShort

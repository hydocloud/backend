from pydantic import BaseModel
from typing import List, Optional
from models.devices import DeviceGroupsModelShort, DevicesModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class DeviceGroupsList(BaseModel):
    deviceGroups: List[DeviceGroupsModelShort]


class DevicesList(BaseModel):
    devices: List[DevicesModelShort]


class Message(BaseModel):
    message: str


class DataModel(BaseModel):
    data: DeviceGroupsList
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]


class DevicesDataModel(BaseModel):
    data: DevicesList
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]

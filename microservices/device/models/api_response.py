from pydantic import BaseModel
from typing import List
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
    total: int = None
    nextPage: int = None
    previousPage: int = None
    totalPages: int = None


class DevicesDataModel(BaseModel):
    data: DevicesList
    total: int = None
    nextPage: int = None
    previousPage: int = None
    totalPages: int = None

from pydantic import BaseModel
from typing import List
from models.devices import DeviceGroupsModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class DeviceGroupsList(BaseModel):
    deviceGroups: List[DeviceGroupsModelShort]


class Message(BaseModel):
    message: str


class DataModel(BaseModel):
    data: DeviceGroupsList
    total: int = None
    nextPage: int = None
    previousPage: int = None
    totalPages: int = None

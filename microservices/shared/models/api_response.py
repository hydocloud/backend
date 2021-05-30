from typing import Optional, List, Union
from pydantic import BaseModel
from models.organizations import ResponseModel
from models.devices import DeviceGroupsModelShort, DevicesModelShort, DevicesModelShortPublicKey
from models.authorization import AuthorizationModelShort
from models.users import UserGroupsModelShort


class LambdaResponse(BaseModel):
    statusCode: int
    body: str


class Message(BaseModel):
    message: str


class Data(BaseModel):
    data: List[
        Union[
            ResponseModel,
            DevicesModelShort,
            DeviceGroupsModelShort,
            AuthorizationModelShort,
            UserGroupsModelShort,
        ]
    ]
    total: Optional[int]
    nextPage: Optional[int]
    previousPage: Optional[int]
    totalPages: Optional[int]


class DataNoList(BaseModel):
    data: Union[
        ResponseModel,
        DevicesModelShort,
        DevicesModelShortPublicKey,
        DeviceGroupsModelShort,
        AuthorizationModelShort,
        UserGroupsModelShort,
    ]


class LambdaSuccessResponse(BaseModel):
    statusCode: int
    body: Data


class LambdaSuccessResponseWithoutData(BaseModel):
    statusCode: int
    body: Message


class LambdaErrorResponse(BaseModel):
    statusCode: int
    body: Message


class UnlockModel(BaseModel):
    success: bool
    message: Optional[str]
    digest: Optional[str]
    signature: Optional[str]


from typing import Any
from pydantic import BaseModel

class Message(BaseModel):
    message: Any

class Data(BaseModel):
    sessionId: str
    jwt: str
    serviceId: str

class LambdaSuccessResponse(BaseModel):
    statusCode: int
    body: Data

class LambdaErrorResponse(BaseModel):
    statusCode: int
    body: Message
   

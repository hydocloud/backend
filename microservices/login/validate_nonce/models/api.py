from pydantic import BaseModel


class Message(BaseModel):
    success: bool


class LambdaSuccessResponse(BaseModel):
    statusCode: int
    body: Message


class LambdaErrorResponse(BaseModel):
    statusCode: int
    body: Message


class InputMessage(BaseModel):
    message: str
    sessionId: str

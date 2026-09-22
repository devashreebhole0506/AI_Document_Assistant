from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )


class Source(BaseModel):
    document: str
    page: int | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: list[Source] = []


class ErrorResponse(BaseModel):
    error: bool = True
    message: str


class UploadResponse(BaseModel):
    filename: str
    status: str
    chunks: int
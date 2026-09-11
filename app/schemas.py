from pydantic import BaseModel

class SanitizeRequest(BaseModel):
    text: str

class SanitizeResponse(BaseModel):
    original_text: str
    sanitized_text: str

class DesanitizeRequest(BaseModel):
    text: str

class DesanitizeResponse(BaseModel):
    restored_text: str

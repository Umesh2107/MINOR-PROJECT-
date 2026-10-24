from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class MaterialBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., min_length=1)
    file_size: int
    extracted_text: Optional[str] = None


class MaterialCreate(MaterialBase):
    file_path: str


class MaterialUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    extracted_text: Optional[str] = None


class Material(MaterialBase):
    id: int
    user_id: int
    file_path: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MaterialUploadResponse(BaseModel):
    id: int
    title: str
    file_type: str
    file_size: int
    extracted_text: Optional[str] = None
    message: str = "Material uploaded successfully"

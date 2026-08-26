from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ServiceBase(BaseModel):
    """Base service model."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": 1,
            "name": "example-service",
            "type": "web",
            "url": "http://example.com",
            "version": "1.0.0",
            "status": "active"
        }
    })

    name: str = Field(..., min_length=1, description="Service name")
    type: str = Field(..., min_length=1, description="Service type")
    url: str = Field(..., min_length=1, description="Service URL")
    version: Optional[str] = Field("", description="Service version")
    status: Optional[str] = Field("", description="Service status")


class ServiceCreate(ServiceBase):
    """Service creation model."""
    pass


class ServiceUpdate(BaseModel):
    """Service update model."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "version": "2.0.0",
            "status": "inactive"
        }
    })

    name: Optional[str] = Field(None, min_length=1)
    type: Optional[str] = Field(None, min_length=1)
    url: Optional[str] = Field(None, min_length=1)
    version: Optional[str] = Field(None)
    status: Optional[str] = Field(None)


class Service(ServiceBase):
    """Complete service model with ID."""
    id: int = Field(..., description="Service ID")


class AreaServices(BaseModel):
    """Model for area with its services."""
    area: str
    services: List[Service]


class AreaCreate(BaseModel):
    """Area creation model."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "area": "production"
        }
    })

    area: str = Field(..., min_length=1, description="Area name")


class AreaUpdate(BaseModel):
    """Area update model."""
    area: str
    services: List[Service]


class ErrorResponse(BaseModel):
    """Error response model."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "error": "Unauthorized access"
        }
    })

    error: str


class MessageResponse(BaseModel):
    """Generic message response model."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "message": "Operation completed successfully"
        }
    })

    message: str

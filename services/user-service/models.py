from typing import List
from pydantic import BaseModel, Field


class UserRole(str):
    """User role enum as string"""
    ROLE_CUSTOMER = "ROLE_CUSTOMER"
    ROLE_SELLER = "ROLE_SELLER"


class User(BaseModel):
    """User model - matches Symfony monolit format"""
    id: int
    email: str
    firstName: str
    lastName: str
    roles: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "firstName": "John",
                "lastName": "Doe",
                "roles": ["ROLE_CUSTOMER"]
            }
        }


class UserCreateRequest(BaseModel):
    """Request model for creating a user"""
    email: str
    firstName: str
    lastName: str
    roles: List[str] = Field(default_factory=lambda: ["ROLE_CUSTOMER"])

from pydantic import BaseModel, EmailStr


class BaseResponse(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'
    expires_in: int
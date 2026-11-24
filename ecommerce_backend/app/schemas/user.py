from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8)
    phone: str | None = None


class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None


# Password change schema
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None = None

    model_config = {
        "from_attributes": True
    }
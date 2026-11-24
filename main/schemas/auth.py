from pydantic import BaseModel, Field, EmailStr

class UserRegistration(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email : EmailStr
    password : str = Field(min_length=8, max_length=120)
    phone : str | None = None

class UserLogin(BaseModel):
    username : EmailStr    
    password:  str
    
class Token(BaseModel):
    access_token : str
    token_type : str = "bearer"
    

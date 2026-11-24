from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from main.utils.security import verify_token
from fastapi import Depends, HTTPException
from main.database import get_db
from main.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user(token: str =Depends(oauth2_scheme), 
                     db: Session =Depends(get_db)):
    
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(status_code=401,
                            detail="Unauthorized token")
        
    user = db.query(User).filter(User.id==user_id).first()
    
    if user is None:
        raise HTTPException(status_code=401,
                            detail="User Not Found")
        
    return user

    
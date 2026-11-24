from dotenv import load_dotenv
from jwt import InvalidTokenError, ExpiredSignatureError
import jwt
from pwdlib import PasswordHash
import os
from datetime import datetime, timezone, timedelta
load_dotenv()

SECRET_KEY= os.getenv("SECRET_KEY")
ALGORTIHM = os.getenv("ALGORITHM")
# TOKEN_EXPIRE_MINUTES = 15

password_hash = PasswordHash.recommended()


def hash_password(plain_password):
    
    return password_hash.hash(plain_password)



def verify_password(plain_password, hashed_password):
    
    return password_hash.verify(plain_password,hashed_password)



def create_access_token(user_id : int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "sub" : str(user_id),
        "exp" : expire
    }
    
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORTIHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORTIHM)
        
        return int(payload.get("sub"))
    

    except InvalidTokenError:
        print("Invalid Token")
        return None
    except ExpiredSignatureError:
        print("Token Expired")
        return None
    

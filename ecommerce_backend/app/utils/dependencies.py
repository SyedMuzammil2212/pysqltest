from fastapi import Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.user import User

from app.utils.oauth2 import oauth2_scheme

from app.utils.token import verify_token


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:

    # Step 1: Verify and decode the token
    payload = verify_token(token)

    # Step 2: Extract user ID from token
    user_id = payload.get("sub")

    if user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Step 3: Convert user ID into integer
    try:

        user_id = int(user_id)

    except (ValueError, TypeError):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Step 4: Find user in database
    current_user = db.query(User).filter(
        User.id == user_id
    ).first()

    # Step 5: Check whether user exists
    if current_user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Step 6: Return logged-in user
    return current_user
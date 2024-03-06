import requests
import json
from jwt import decode
from fastapi import Request, HTTPException, status

from src.config.settings import USER_MICROSERVICE_KEY, USER_MICROSERVICE_BASE_URL, JWT_SIGNING_KEY, VERIFY_USERS_REQUESTS

def is_staff_user(request: Request):
    """
    Checks if the user is staff
    :return: True if the user is staff, otherwise raises HTTPException 403
    """
    authorization = request.headers.get("Authorization", None)
    if not authorization:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials")

    user_id = decode(token,JWT_SIGNING_KEY ,algorithms=["HS256"]).get("user_id")

    if VERIFY_USERS_REQUESTS:
        user_data = requests.post(f"{USER_MICROSERVICE_BASE_URL}/api/user/check/",
                                  {"user_id": int(user_id), "microservice_key": USER_MICROSERVICE_KEY})
        status_code = user_data.status_code
        user_data = json.loads(user_data.content)
        if (user_data.get("is_superuser", False) or user_data.get("is_staff", False)) and status_code == 200:
            return True
    else:
        return True

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to perform this action")

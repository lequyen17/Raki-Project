import jwt
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import (
    decode_token,
    get_current_user_id,
    get_user_id_from_token,
)
from app.core.config import SECRET_KEY, JWT_ALGORITHM

if __name__ == "__main__":

    print("========== Test decode_token ==========")

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgyOTc2ODc5LCJpYXQiOjE3ODI5NzU5NzksImp0aSI6ImRlMDJkNGY3NGY0MjRkZWFhMTNmNzJjMjczODkyZGM1IiwidXNlcl9pZCI6IjEifQ.ZawhFPtGx-YyngHixHJYvI1cExnKYTHUQamUWhFGGk0"

    payload = decode_token(token)
    print(payload)

    print("\n========== Test get_user_id_from_token ==========")

    user_id = get_user_id_from_token(token)
    print(user_id)

    print("\n========== Test get_current_user_id ==========")

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    user_id = get_current_user_id(credentials)
    print(user_id)

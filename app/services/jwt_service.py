from jose import jwt
from fastapi import HTTPException
from config import settings
from fastapi.security.http import HTTPAuthorizationCredentials
from typing import Optional, Union


def create_jwt_token(data: dict) -> str:
    encoded_jwt = jwt.encode(data, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_jwt_token(token: Optional[Union[HTTPAuthorizationCredentials, str]] = None) -> dict:
    try:
        decoded_payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return decoded_payload
    except jwt.JWTError as error:
        raise HTTPException(status_code=400, detail="Signature verification failed.")


def check_jwt_type(token: Optional[HTTPAuthorizationCredentials] = None) -> Optional[bool]:
    try:
        token_view = jwt.get_unverified_claims(token.credentials)
        owner = token_view.get('owner', None)
        return owner
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Not Found or Bad Request")

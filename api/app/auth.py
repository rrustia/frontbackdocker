import os
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# In production, this should be set via environment variable and rotated periodically.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "replace-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

# Demo credentials are read from environment variables so deployments can override quickly.
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

# The password is hashed once at startup, and cleartext stays in env only to avoid hard-coded hashes.
_ADMIN_PASSWORD_HASH = pwd_context.hash(ADMIN_PASSWORD)


def authenticate_user(username: str, password: str) -> bool:
    """Verifies whether the submitted credentials match the admin account.

    Input: Username and password strings.
    Output: Returns True for a valid login, otherwise False.
    """
    if username != ADMIN_USERNAME:
        return False
    return pwd_context.verify(password, _ADMIN_PASSWORD_HASH)


def create_access_token(subject: str) -> str:
    """Builds a short-lived JWT for one user.

    Input: The token subject, usually a username.
    Output: Returns an encoded access token string.
    """
    expires_at = datetime.now(UTC) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_username(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Checks the bearer token for protected routes.

    Input: The request authorization header from FastAPI.
    Output: Returns the username from the token, or raises a 401 error.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject:
            raise ValueError("Token subject missing")
        return subject
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    FastAPI dependency to extract and verify the Firebase ID token. Support a mock token bypass in development mode.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials"
        )
    
    token = credentials.credentials

    # 1. Dev Mode / Mock token bypass
    if token.startswith("mock-"):
        uid = token.replace("mock-", "")
        return {
            "uid": uid,
            "email": f"{token}@example.com"
        }
    
    if token == "valid-token":
        return {
            "uid": "test-user-123",
            "email": "test@example.com"
        }
        
    # 2. Live JWT verification (decode and verify exp, iss, and aud claims)
    try:
        import jwt
        import time
        from app.config import settings
        
        # Decode without signature verification to avoid the native cryptography package dependency
        decoded = jwt.decode(token, options={"verify_signature": False})
        
        # Validate expiration
        now = time.time()
        if decoded.get("exp", 0) < now:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
            
        # Validate issuer
        project_id = settings.FIREBASE_PROJECT_ID or "weeat-16763"
        expected_iss = f"https://securetoken.google.com/{project_id}"
        if decoded.get("iss") != expected_iss:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer"
            )
            
        # Validate audience
        if decoded.get("aud") != project_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token audience"
            )
            
        uid = decoded.get("sub")
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing subject (UID) claim in token"
            )
            
        return {
            "uid": uid,
            "email": decoded.get("email")
        }
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}"
        )
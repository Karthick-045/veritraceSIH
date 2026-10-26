from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.rbac import get_current_user
from app.models.models import User
from app.schemas.schemas import LoginRequest, TokenResponse, UserOut, ApiResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == creds.email).first()
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})
    data = TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        full_name=user.full_name,
        user_id=user.id
    )
    return ApiResponse(data=data)

@router.get("/me", response_model=ApiResponse[UserOut])
def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=UserOut.model_validate(current_user))

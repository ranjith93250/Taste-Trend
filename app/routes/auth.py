"""
Authentication routes (login, signup, logout)
"""
from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta
import logging

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..database import db
from ..auth_utils import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(None),
    password: str = Form(None)
):
    """Handle login form submission"""
    try:
        # Log the request details
        logger.info(f"Login POST request received")
        logger.info(f"Content-Type: {request.headers.get('content-type')}")
        logger.info(f"Email received: {email}")
        logger.info(f"Password received: {'***' if password else None}")
        
        # Validate that we received the form data
        if not email or not password:
            logger.warning("Missing email or password in form submission")
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Please provide both email and password"
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Login attempt for email: {email}")
        
        # Authenticate user
        user = authenticate_user(email.strip().lower(), password)
        
        if not user:
            logger.warning(f"Failed login attempt for email: {email}")
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Incorrect email or password"
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Set token in cookie and redirect to profile
        response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
        cookie_value = f"Bearer {access_token}"
        response.set_cookie(
            key="access_token",
            value=cookie_value,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        logger.info(f"User {email} logged in successfully")
        logger.debug(f"Set cookie with token (length: {len(access_token)})")
        logger.info(f"Redirecting to /profile")
        return response
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "An error occurred during login. Please try again."
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Display signup page"""
    return templates.TemplateResponse("signup.html", {"request": request})


@router.post("/signup")
async def signup(request: Request):
    """Handle signup form submission"""
    try:
        form = await request.form()
        email = form.get("email", "").strip().lower()
        password = form.get("password", "")
        confirm_password = form.get("confirm_password", "")
        full_name = form.get("full_name", "").strip()

        logger.info(f"Signup attempt for email: {email}")

        # Basic validation
        if not all([email, password, confirm_password, full_name]):
            error_msg = f"Missing fields - Email: {bool(email)}, Password: {bool(password)}, Name: {bool(full_name)}"
            logger.warning(error_msg)
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "All fields are required"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if "@" not in email or "." not in email:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Please enter a valid email address"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if password != confirm_password:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Passwords do not match"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 8:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Password must be at least 8 characters long"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Check password length in bytes (for bcrypt compatibility)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Password is too long. Please use 72 characters or fewer."},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Check if user already exists
        logger.debug(f"Checking if user {email} already exists")
        try:
            existing_user = db.users.find_one({"email": email})
            if existing_user:
                logger.warning(f"Registration attempt with existing email: {email}")
                return templates.TemplateResponse(
                    "signup.html",
                    {"request": request, "error": "Email already registered"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Create user
            logger.debug("Creating new user document")
            try:
                hashed_password = get_password_hash(password)
                user_dict = {
                    "email": email,
                    "full_name": full_name,
                    "hashed_password": hashed_password,
                    "disabled": False,
                    "created_at": datetime.utcnow()
                }
                logger.debug(f"User document prepared: {user_dict}")
            except Exception as e:
                logger.error(f"Error preparing user document: {str(e)}")
                raise

            # Insert user into database
            result = db.users.insert_one(user_dict)
            logger.info(f"User {email} created successfully with ID: {result.inserted_id}")

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return templates.TemplateResponse(
                "signup.html",
                {"request": request, "error": "Database error. Please try again later."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Log the user in automatically after signup
        logger.info(f"Creating access token for new user: {email}")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )

        # Set the access token in a secure HTTP-only cookie
        response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
        cookie_value = f"Bearer {access_token}"
        response.set_cookie(
            key="access_token",
            value=cookie_value,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        logger.info(f"Signup complete for {email}, redirecting to /profile")
        logger.debug(f"Cookie set with token (length: {len(access_token)})")
        return response

    except Exception as e:
        logger.error(f"Unexpected error in signup: {str(e)}", exc_info=True)
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "An unexpected error occurred. Please try again."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/logout")
async def logout():
    """Logout user by clearing the access token cookie"""
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

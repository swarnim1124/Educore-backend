"""
File: xsc_libc_models.py
Description: Shared base models for the OneApp Framework.

Author: Siddharth Amdal
App: OneApp

"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class OneAppRequest(BaseModel):
    """
    Standard request payload for internal OneApp routing.
    """

    mod: str = Field(..., description="The target module (e.g., m_AAA)")
    subMod: str = Field(..., description="The target submodule (e.g., sm_auth)")
    action: str = Field(..., description="The target action class (e.g., session)")
    actionType: str = Field(
        ..., description="The action verb (e.g., add, view, update, delete)"
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict, description="The business payload"
    )

class LoginRequest(BaseModel):
    """
    Standard login request payload validation.
    """
    username: str = Field(..., min_length=1, description="The user's login ID or email")
    password: str = Field(..., min_length=1, description="The user's password")
    captchaToken: Optional[str] = Field(None, description="The reCAPTCHA token if required")


class OneAppResponse(BaseModel):
    """
    Standardized response structure for all endpoints.
    """

    status: str = Field(..., description="'success' or 'error'")
    message: str = Field(..., description="Human readable message")
    error_code: Optional[str] = Field(
        None, description="Standardized error code if error"
    )
    data: Optional[Dict[str, Any]] = Field(None, description="Result payload")
    meta: Optional[Dict[str, Any]] = Field(
        None, description="Pagination or request metadata"
    )

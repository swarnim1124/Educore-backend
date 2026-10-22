from pydantic import BaseModel
from typing import List, Optional, Any

class PasswordPolicy(BaseModel):
    min_length: int = 8
    require_uppercase: bool = True
    require_number: bool = True
    require_special: bool = True
    expiry_days: int = 90
    history_count: int = 5
    max_attempts: int = 5

class SessionPolicy(BaseModel):
    idle_timeout_minutes: int = 15
    max_session_duration: int = 720 # 12 hours
    max_concurrent_sessions: int = 1
    enforce_device_binding: bool = False
    ip_whitelist: Optional[List[str]] = None

class LoginPolicy(BaseModel):
    enable_captcha: bool = False
    captcha_threshold: str = "0.5"
    allowed_auth_methods: List[str] = ["password"]
    enable_ip_restriction: bool = False
    blocked_ips: Optional[List[str]] = None
    enable_geo_restriction: bool = False
    allowed_countries: Optional[List[str]] = None
    
    # MFA Policies
    mfa_max_attempts: int = 5
    backup_code_count: int = 10
    backup_code_length: int = 8
    enrollment_challenge_expiry_minutes: int = 15

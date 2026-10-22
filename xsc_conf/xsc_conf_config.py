"""
Author: Siddharth Amdal.
"""

CODE_VERSION = 1.0

FASTAPI_VERSION = "0.136.1"
UVICORN_VERSION = "0.46.0"

import os

# Authentication & Security
JWT_SECRET = os.environ.get("JWT_SECRET")
# Production environments MUST configure this properly.
# Fail early if in production and no valid secret is provided.
is_production = os.environ.get("ENV", "development").lower() == "production"
if is_production and (not JWT_SECRET or len(JWT_SECRET) < 32):
    raise ValueError("CRITICAL SECURITY ERROR: A valid cryptographically secure JWT_SECRET (>= 32 bytes) must be set in the production environment.")
elif not JWT_SECRET:
    # Development fallback
    JWT_SECRET = "dev-only-insecure-secret-change-me-in-env-file"  # local development only


# CAPTCHA Configuration
XSC_CAPTCHA_ENABLED = False
XSC_CAPTCHA_PROVIDER = "google"  # Options: "dev", "google"
XSC_RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY")
XSC_RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")
XSC_RECAPTCHA_SCORE_THRESHOLD = 0.5

# Razorpay Configuration
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

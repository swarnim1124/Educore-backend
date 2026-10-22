"""
File: xsc_libe_recaptcha.py
Description: Production provider for Google reCAPTCHA v3 verification.

Author: Siddharth Amdal
App: OneApp

"""

import httpx
import xsc_conf.xsc_conf_config as config
from xsc_lib.xsc_lib_app.xsc_liba_captcha import ICaptchaProvider
from xsc_lib.xsc_lib_common.xsc_libc_logger import XSCLogger


class GoogleRecaptchaProvider(ICaptchaProvider):
    """
    A concrete CAPTCHA provider for Google reCAPTCHA v3.
    """

    VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

    async def verify(
        self, token: str, action: str = "login", ip_address: str = None
    ) -> bool:
        """
        Verify the provided CAPTCHA token against Google reCAPTCHA v3 API.
        """
        if not token:
            XSCLogger.error("GoogleRecaptchaProvider: Missing CAPTCHA token")
            return False

        secret = getattr(config, "XSC_RECAPTCHA_SECRET_KEY", None)
        threshold = getattr(config, "XSC_RECAPTCHA_SCORE_THRESHOLD", 0.5)

        if not secret or secret == "YOUR_RECAPTCHA_SECRET_KEY":
            XSCLogger.error(
                "GoogleRecaptchaProvider: Missing or default XSC_RECAPTCHA_SECRET_KEY configuration"
            )
            return False

        data = {"secret": secret, "response": token}
        if ip_address:
            data["remoteip"] = ip_address

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(self.VERIFY_URL, data=data)

            if response.status_code != 200:
                XSCLogger.error(
                    f"GoogleRecaptchaProvider: API returned HTTP {response.status_code}"
                )
                return False

            result = response.json()
            success = result.get("success", False)
            res_action = result.get("action", "")
            score = result.get("score", 0.0)
            error_codes = result.get("error-codes", [])
            hostname = result.get("hostname", "unknown")

            if not success:
                XSCLogger.warning(
                    "GoogleRecaptchaProvider: Verification failed. Reason: success=False. "
                    f"Score: {score}. Errors: {error_codes}. Hostname: {hostname}"
                )
                return False

            if res_action != action:
                XSCLogger.warning(
                    f"GoogleRecaptchaProvider: Action mismatch. Expected '{action}', got '{res_action}'. "
                    f"Score: {score}. Errors: {error_codes}. Hostname: {hostname}"
                )
                return False

            if score < threshold:
                XSCLogger.warning(
                    f"GoogleRecaptchaProvider: Score {score} below threshold {threshold}. "
                    f"Action: {res_action}. Errors: {error_codes}. Hostname: {hostname}"
                )
                return False

            XSCLogger.info(
                "GoogleRecaptchaProvider: Verification successful. "
                f"Action: {action}. Score: {score}. IP: {ip_address}"
            )
            return True

        except httpx.TimeoutException:
            XSCLogger.error("GoogleRecaptchaProvider: Request to Google API timed out")
            return False
        except httpx.RequestError as e:
            XSCLogger.error(f"GoogleRecaptchaProvider: Request failed. Error: {str(e)}")
            return False
        except ValueError:
            XSCLogger.error(
                "GoogleRecaptchaProvider: Malformed JSON response from Google API"
            )
            return False
        except Exception as _e:
            XSCLogger.error("GoogleRecaptchaProvider: Unexpected error", exc=e)
            return False

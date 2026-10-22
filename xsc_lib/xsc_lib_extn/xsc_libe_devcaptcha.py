"""
File: xsc_libe_devcaptcha.py
Description: Development provider for CAPTCHA verification that always succeeds.

Author: Siddharth Amdal
App: OneApp

"""

from xsc_lib.xsc_lib_app.xsc_liba_captcha import ICaptchaProvider


class DevCaptchaProvider(ICaptchaProvider):
    """
    A concrete CAPTCHA provider for development purposes.
    Always returns True.
    """

    async def verify(
        self, token: str, action: str = "login", ip_address: str = None
    ) -> bool:
        """
        Verify the provided CAPTCHA token for development.
        """
        if not token:
            return False

        # In development, any non-empty token passes
        return True

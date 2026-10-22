"""
File: xsc_liba_captcha.py
Description: Abstraction interface for CAPTCHA verification.

Author: Siddharth Amdal
App: OneApp

"""

from abc import ABC, abstractmethod


class ICaptchaProvider(ABC):
    """
    Common interface for CAPTCHA providers.
    """

    @abstractmethod
    async def verify(
        self, token: str, action: str = "login", ip_address: str = None
    ) -> bool:
        """
        Verify the provided CAPTCHA token.

        Args:
            token: The token provided by the client-side CAPTCHA challenge.
            action: The expected action name (e.g., 'login').
            ip_address: The IP address of the user (optional, required by some providers).

        Returns:
            bool: True if validation passes, False otherwise.
        """


def get_captcha_provider() -> ICaptchaProvider:
    """
    Factory function to retrieve the configured CAPTCHA provider.
    Reads XSC_CAPTCHA_PROVIDER from configuration.
    """
    import xsc_conf.xsc_conf_config as config

    provider_name = getattr(config, "XSC_CAPTCHA_PROVIDER", "dev").lower()

    if provider_name == "google":
        from xsc_lib.xsc_lib_extn.xsc_libe_recaptcha import GoogleRecaptchaProvider

        return GoogleRecaptchaProvider()

    # Default to dev
    from xsc_lib.xsc_lib_extn.xsc_libe_devcaptcha import DevCaptchaProvider

    return DevCaptchaProvider()

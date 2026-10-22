"""
File: lib_communication.py
Description: Handler for lib_communication operations in OneApp.

Author: Siddharth, Siddharth Amdal.
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility


from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager


class CommunicationManager:
    """
    Class representing CommunicationManager.
    """

    def __init__(self, institution_id):
        """
        Executes the __init__ operation.
        """
        self.institution_id = institution_id
        self.providers = {}

    def _get_provider(self):
        """
        Executes the _get_provider operation.
        """
        db = PostgreSQLManager()
        db.connectDB()

        res = db.select(
            ["provider_name", "credentials"],
            "tb_integration_config",
            {
                "institution_id": self.institution_id,
                "integration_type": "SMS",
                "is_active": True,
            },
        )

        provider_name = None
        credentials = {}

        if res.get("status") == "success" and res.get("data"):
            config = res["data"][0]
            provider_name = config.get("provider_name")
            credentials = config.get("credentials") or {}
        else:
            # Fallback
            provider_name = XSCUtility.get_env("DEFAULT_SMS_PROVIDER", "TWILIO")
            if provider_name == "TWILIO":
                credentials = {
                    "account_sid": XSCUtility.get_env("TWILIO_ACCOUNT_SID"),
                    "auth_token": XSCUtility.get_env("TWILIO_AUTH_TOKEN"),
                    "twilio_number": XSCUtility.get_env("TWILIO_NUMBER"),
                }
            elif provider_name == "MSG91":
                credentials = {
                    "auth_key": XSCUtility.get_env("MSG91_AUTH_KEY"),
                    "sender_id": XSCUtility.get_env("MSG91_SENDER_ID"),
                }

        if not provider_name:
            raise ValueError("No SMS provider configured")

        provider_name = XSCUtility.to_upper(provider_name)

        if provider_name in self.providers:
            return self.providers[provider_name]

        if provider_name == "TWILIO":
            from xsc_lib.xsc_lib_extn.xsc_libe_twilio import TwilioProvider

            provider = TwilioProvider(credentials)
            self.providers[provider_name] = provider
            return provider
        elif provider_name == "MSG91":
            from xsc_lib.xsc_lib_extn.xsc_libe_msg91 import Msg91Provider

            provider = Msg91Provider(credentials)
            self.providers[provider_name] = provider
            return provider

        raise ValueError(f"Unsupported SMS provider: {provider_name}")

    def send_sms(self, phone_number, message):
        """
        Executes the send_sms operation.
        """
        try:
            provider = self._get_provider()
            return provider.send_sms(phone_number, message)
        except Exception as _e:
            print(f"[CommunicationManager] Error: {e}")
            return XSCUtility.error_response(message=str(e))

    def send_email(self, to_email, subject, body):
        """
        Executes the send_email operation.
        """
        return XSCUtility.error_response(message="Not implemented yet")

    def send_whatsapp(self, phone_number, message):
        """
        Executes the send_whatsapp operation.
        """
        return XSCUtility.error_response(message="Not implemented yet")

    def send_push(self, user_id, title, body):
        """
        Executes the send_push operation.
        """
        return XSCUtility.error_response(message="Not implemented yet")

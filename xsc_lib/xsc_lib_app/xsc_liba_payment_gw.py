from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility

"""
File: lib_payment_gw.py
Description: Handler for lib_payment_gw operations in OneApp.

Author: Siddharth, Siddharth Amdal.
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_pgrs import PostgreSQLManager


class PaymentGatewayManager:
    """
    Class representing PaymentGatewayManager.
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
                "integration_type": "PAYMENT",
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
            provider_name = XSCUtility.get_env("DEFAULT_PAYMENT_PROVIDER", "RAZORPAY")
            if provider_name == "RAZORPAY":
                import xsc_conf.xsc_conf_config as conf

                credentials = {
                    "key_id": XSCUtility.get_env("RAZORPAY_KEY_ID")
                    or getattr(conf, "RAZORPAY_KEY_ID", None),
                    "key_secret": XSCUtility.get_env("RAZORPAY_KEY_SECRET")
                    or getattr(conf, "RAZORPAY_KEY_SECRET", None),
                }
        if not provider_name:
            raise ValueError("No payment provider configured")

        provider_name = XSCUtility.to_upper(provider_name)

        if provider_name in self.providers:
            return self.providers[provider_name]

        if provider_name == "RAZORPAY":
            from xsc_lib.xsc_lib_extn.xsc_libe_razorpay import RazorpayProvider

            provider = RazorpayProvider(credentials)
            self.providers[provider_name] = provider
            return provider

        raise ValueError(f"Unsupported payment provider: {provider_name}")

    def create_order(
        self, amount, currency="INR", receipt="receipt_default", metadata=None
    ):
        """
        Executes the create_order operation.
        """
        try:
            provider = self._get_provider()
            return provider.create_order(amount, currency, receipt, metadata)
        except Exception as _e:
            print(f"[PaymentGatewayManager] Error: {e}")
            return XSCUtility.error_response(str(e))

    def verify_payment(self, payment_data):
        """
        Executes the verify_payment operation.
        """
        try:
            provider = self._get_provider()
            return provider.verify_payment(payment_data)
        except Exception as _e:
            print(f"[PaymentGatewayManager] Error: {e}")
            return XSCUtility.error_response(str(e))

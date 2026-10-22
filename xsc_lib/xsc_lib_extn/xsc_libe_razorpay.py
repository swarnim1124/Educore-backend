"""
File: xsc_lib_razorpay.py
Description: Handler for xsc_lib_razorpay operations in OneApp.

Author: Siddharth, Siddharth Amdal.
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility


import razorpay


class RazorpayProvider:
    """
    Class representing RazorpayProvider.
    """

    def __init__(self, credentials):
        """
        Executes the __init__ operation.
        """
        # TODO: Secrets stored in database should support encryption later.
        self.key_id = credentials.get("key_id")
        self.key_secret = credentials.get("key_secret")
        if self.key_id and self.key_secret:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        else:
            self.client = None

    def create_order(
        self, amount, currency="INR", receipt="receipt_default", metadata=None
    ):
        """
        Executes the create_order operation.
        """
        if not amount:
            return XSCUtility.error_response(message="amount is required")

        try:
            # DEMO / MOCK Implementation
            if not self.key_id or not self.key_secret:
                import uuid

                return XSCUtility.success_response(
                    message="",
                    order={
                        "id": f"order_mock_{uuid.uuid4().hex[:10]}",
                        "entity": "order",
                        "amount": amount,
                        "currency": currency,
                        "receipt": receipt,
                        "status": "created",
                    },
                )

            order_data = {
                "amount": amount,
                "currency": currency,
                "receipt": receipt,
                "payment_capture": 1,
            }
            if metadata:
                order_data["notes"] = metadata

            order = self.client.order.create(order_data)
            return XSCUtility.success_response(message="", order=order)
        except Exception as _e:
            return XSCUtility.error_response(
                message="", provider="razorpay", error=str(e)
            )

    def verify_payment(self, payment_data):
        """
        Executes the verify_payment operation.
        """
        params = {
            "razorpay_order_id": payment_data.get("razorpay_order_id"),
            "razorpay_payment_id": payment_data.get("razorpay_payment_id"),
            "razorpay_signature": payment_data.get("razorpay_signature"),
        }
        try:
            self.client.utility.verify_payment_signature(params)
            return XSCUtility.success_response(message="Payment verified")
        except razorpay.errors.SignatureVerificationError:
            return XSCUtility.error_response(message="Invalid payment signature")
        except Exception as _e:
            return XSCUtility.error_response(
                message="", provider="razorpay", error=str(e)
            )

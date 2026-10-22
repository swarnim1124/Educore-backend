"""
File: xsc_lib_twilio.py
Description: Handler for xsc_lib_twilio operations in OneApp.

Author: Siddharth, Siddharth Amdal.
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility


from twilio.rest import Client


class TwilioProvider:
    """
    Class representing TwilioProvider.
    """

    def __init__(self, credentials):
        """
        Executes the __init__ operation.
        """
        # TODO: Secrets stored in database should support encryption later.
        self.account_sid = credentials.get("account_sid")
        self.auth_token = credentials.get("auth_token")
        self.twilio_number = credentials.get("twilio_number")

        self.client = Client(self.account_sid, self.auth_token)

    def send_sms(self, phone_number, message):
        """
        Executes the send_sms operation.
        """
        try:
            response = self.client.messages.create(
                body=message, from_=self.twilio_number, to=phone_number
            )
            return XSCUtility.success_response(
                message=message,
                provider="twilio",
                message_sid=response.sid,
                phone_number=phone_number,
            )
        except Exception as ex:
            return XSCUtility.error_response(
                message="", provider="twilio", error=str(ex)
            )

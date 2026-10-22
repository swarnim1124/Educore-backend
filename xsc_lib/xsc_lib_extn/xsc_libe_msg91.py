"""
File: xsc_lib_msg91.py
Description: Handler for xsc_lib_msg91 operations in OneApp.

Author: Siddharth, Siddharth Amdal.
App: OneApp

"""

from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility


class Msg91Provider:
    """
    Class representing Msg91Provider.
    """

    def __init__(self, credentials):
        """
        Executes the __init__ operation.
        """
        # TODO: Secrets stored in database should support encryption later.
        self.auth_key = credentials.get("auth_key")
        self.sender_id = credentials.get("sender_id")

    def send_sms(self, phone_number, message):
        """
        Executes the send_sms operation.
        """
        print(f"[MSG91] Sending SMS to {phone_number} using sender {self.sender_id}")
        return XSCUtility.success_response(
            message=message, provider="msg91", phone_number=phone_number
        )

"""
Author: Siddharth Amdal
File: xsc_lib_firebase_fcm.py
Description: Wrapper around Firebase Admin SDK for Cloud Messaging (FCM).
"""

import os
import firebase_admin
from firebase_admin import credentials, messaging
from typing import Dict, Any, List, Optional
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility


class XSCFirebase:
    _is_initialized = False
    _is_demo_mode = False

    @classmethod
    def initialize(cls) -> None:
        """
        Initialize the Firebase Admin SDK if not already initialized.
        Loads credentials from xsc_conf/firebase_credentials.json.
        """
        if cls._is_initialized:
            return

        # Attempt to find the credentials file
        cred_path = os.path.join(os.getcwd(), "xsc_con", "firebase_credentials.json")

        try:
            if not os.path.exists(cred_path):
                print(
                    f"[XSCFirebase] Credentials not found at {cred_path}. Running FCM demo mode."
                )
                cls._is_demo_mode = True
                cls._is_initialized = True
                return

            cred = credentials.Certificate(cred_path)
            # Check if default app is already initialized in firebase_admin
            try:
                firebase_admin.get_app()
            except ValueError:
                firebase_admin.initialize_app(cred)

            cls._is_initialized = True
            print("[XSCFirebase] Initialized successfully.")
        except Exception as _e:
            print(f"[XSCFirebase] Initialization error: {e}")

    @classmethod
    def send_notification(
        cls, token: str, title: str, body: str, data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send a notification to a specific device token.
        """
        if not cls._is_initialized:
            cls.initialize()

        if not cls._is_initialized:
            return XSCUtility.error_response(
                "Firebase is not initialized.", "FCM_NOT_INIT"
            )

        # Convert all data values to string as FCM requires string values for data payload
        fcm_data = {}
        if data:
            fcm_data = {str(k): str(v) for k, v in data.items()}

        if cls._is_demo_mode:
            return XSCUtility.success_response(
                "Notification sent successfully", {"message_id": "mock_message_id"}
            )

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=fcm_data,
                token=token,
            )
            response = messaging.send(message)
            return XSCUtility.success_response(
                "Notification sent successfully", {"message_id": response}
            )
        except Exception as _e:
            print(f"[XSCFirebase] Error sending notification: {e}")
            return XSCUtility.error_response(str(e), "FCM_SEND_ERROR")

    @classmethod
    def send_topic_notification(
        cls, topic: str, title: str, body: str, data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send a notification to a subscribed topic.
        """
        if not cls._is_initialized:
            cls.initialize()

        if not cls._is_initialized:
            return XSCUtility.error_response(
                "Firebase is not initialized.", "FCM_NOT_INIT"
            )

        fcm_data = {}
        if data:
            fcm_data = {str(k): str(v) for k, v in data.items()}

        if cls._is_demo_mode:
            return XSCUtility.success_response(
                "Topic notification sent successfully",
                {"message_id": "mock_message_id"},
            )

        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=fcm_data,
                topic=topic,
            )
            response = messaging.send(message)
            return XSCUtility.success_response(
                "Topic notification sent successfully", {"message_id": response}
            )
        except Exception as _e:
            print(f"[XSCFirebase] Error sending topic notification: {e}")
            return XSCUtility.error_response(str(e), "FCM_TOPIC_SEND_ERROR")

    @classmethod
    def subscribe_to_topic(cls, tokens: List[str], topic: str) -> Dict[str, Any]:
        """
        Subscribe a list of device tokens to a topic.
        """
        if not cls._is_initialized:
            cls.initialize()

        if not cls._is_initialized:
            return XSCUtility.error_response(
                "Firebase is not initialized.", "FCM_NOT_INIT"
            )

        if not tokens:
            return XSCUtility.error_response("No tokens provided.", "FCM_NO_TOKENS")

        if cls._is_demo_mode:
            return XSCUtility.success_response(
                "Subscribed to topic",
                {"success_count": len(tokens), "failure_count": 0},
            )

        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            return XSCUtility.success_response(
                "Subscribed to topic",
                {
                    "success_count": response.success_count,
                    "failure_count": response.failure_count,
                },
            )
        except Exception as _e:
            print(f"[XSCFirebase] Error subscribing to topic: {e}")
            return XSCUtility.error_response(str(e), "FCM_SUBSCRIBE_ERROR")

    @classmethod
    def unsubscribe_from_topic(cls, tokens: List[str], topic: str) -> Dict[str, Any]:
        """
        Unsubscribe a list of device tokens from a topic.
        """
        if not cls._is_initialized:
            cls.initialize()

        if not cls._is_initialized:
            return XSCUtility.error_response(
                "Firebase is not initialized.", "FCM_NOT_INIT"
            )

        if not tokens:
            return XSCUtility.error_response("No tokens provided.", "FCM_NO_TOKENS")

        if cls._is_demo_mode:
            return XSCUtility.success_response(
                "Unsubscribed from topic",
                {"success_count": len(tokens), "failure_count": 0},
            )

        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            return XSCUtility.success_response(
                "Unsubscribed from topic",
                {
                    "success_count": response.success_count,
                    "failure_count": response.failure_count,
                },
            )
        except Exception as _e:
            print(f"[XSCFirebase] Error unsubscribing from topic: {e}")
            return XSCUtility.error_response(str(e), "FCM_UNSUBSCRIBE_ERROR")

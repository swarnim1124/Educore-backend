from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pyotp
import secrets
import string

class MFAProvider(ABC):
    """
    Abstract Base Class defining the interface for all MFA mechanisms.
    Providers own secret/OTP generation and verification.
    Providers do NOT own session management, database persistence, or policy evaluation.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Returns the unique identifier for this provider (e.g., 'totp', 'email_otp')."""
        pass

    @abstractmethod
    def create_enrollment_challenge(self, username: str, issuer_name: str, **kwargs) -> Dict[str, Any]:
        """
        Initiates the enrollment process.
        Returns a dictionary containing the secret and provisioning URI.
        """
        pass

    @abstractmethod
    def verify_enrollment_challenge(self, secret: str, response: str, **kwargs) -> bool:
        """
        Verifies the challenge response during enrollment.
        """
        pass

    @abstractmethod
    def create_authentication_challenge(self, secret: str, **kwargs) -> Dict[str, Any]:
        """
        Initiates the authentication process for a given secret.
        For TOTP, this may simply be a no-op that returns metadata.
        For SMS/Email, this triggers sending the OTP.
        """
        pass

    @abstractmethod
    def verify_authentication_challenge(self, secret: str, response: str, **kwargs) -> bool:
        """
        Verifies the authentication response.
        """
        pass

    def generate_backup_codes(self, count: int, length: int) -> List[str]:
        """
        Generates cryptographically secure backup codes.
        These are returned in plaintext exactly once for the user to store.
        """
        alphabet = string.ascii_uppercase + string.digits
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(alphabet) for _ in range(length))
            codes.append(code)
        return codes


class TOTPProvider(MFAProvider):
    """
    Time-Based One-Time Password (TOTP) Provider.
    """

    @property
    def provider_id(self) -> str:
        return "totp"

    def create_enrollment_challenge(self, username: str, issuer_name: str, **kwargs) -> Dict[str, Any]:
        secret = pyotp.random_base32()
        provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=issuer_name
        )
        return {
            "secret": secret,
            "provisioning_uri": provisioning_uri
        }

    def verify_enrollment_challenge(self, secret: str, response: str, **kwargs) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(response)

    def create_authentication_challenge(self, secret: str, **kwargs) -> Dict[str, Any]:
        # For TOTP, generating an authentication challenge is conceptually passive.
        # The user's device continuously generates codes based on time.
        return {
            "status": "challenge_ready",
            "message": "Please enter the TOTP from your authenticator app."
        }

    def verify_authentication_challenge(self, secret: str, response: str, **kwargs) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(response)

async def register_mfa_provider():
    """
    Called during application/module startup to register the active 
    MFAProvider into the central CapabilityRegistry.
    """
    from xsc_lib.xsc_lib_app.xsc_liba_capability import CapabilityRegistry
    
    # We register the default TOTP provider.
    CapabilityRegistry.register_capability("mfa_provider", TOTPProvider(), "DEFAULT TOTP")


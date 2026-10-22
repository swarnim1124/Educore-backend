"""
File: xsc_libc_utility.py
Description: OneApp Common Utility Library - Reusable framework-level helpers.

Author: Siddharth Amdal
App: OneApp

"""

import re
import base64
import difflib
import os
import uuid
import json
import random
import string
import secrets
import hashlib
from datetime import datetime, date, timezone, timedelta
from typing import Any, List, Optional, Dict


class XSCUtility:
    """
    A common utility library containing reusable framework-level helpers for OneApp backend.
    """

    # ==================================================
    # 1. STRING UTILITIES
    # ==================================================

    @staticmethod
    def trim(value: Any) -> str:
        """
        Remove leading and trailing spaces.
        """
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def get_pagination_limits(page: int = 1, limit: int = 50) -> Dict[str, int]:
        """
        Calculates pagination offset based on page and limit.
        Ensures limit does not exceed a sensible maximum (e.g., 1000).
        Returns a dict with 'limit' and 'offset' safe for SQL queries.
        """
        page = max(1, int(page)) if page else 1
        limit = min(max(1, int(limit)), 1000) if limit else 50
        offset = (page - 1) * limit
        return {"limit": limit, "offset": offset}

    @staticmethod
    def normalize_spaces(value: Any) -> str:
        """
        Replace multiple spaces with single spaces.
        """
        if value is None:
            return ""
        return re.sub(r"\s+", " ", str(value)).strip()

    @staticmethod
    def to_upper(value: Any) -> str:
        """
        Convert string to uppercase.
        """
        if value is None:
            return ""
        return str(value).upper()

    @staticmethod
    def to_lower(value: Any) -> str:
        """
        Convert string to lowercase.
        """
        if value is None:
            return ""
        return str(value).lower()

    @staticmethod
    def to_title_case(value: Any) -> str:
        """
        Convert names properly to title case.
        """
        if value is None:
            return ""
        return str(value).title()

    @staticmethod
    def to_snake_case(value: Any) -> str:
        """
        Convert string to snake_case (e.g. 'portal admin' -> 'portal_admin', 'sm_feeAssignment' -> 'sm_fee_assignment').
        """
        if value is None:
            return ""
        s = str(value).strip()
        s = re.sub(r"[\s\-]+", "_", s)
        s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
        return s.lower()

    @staticmethod
    def to_pascal_case(value: Any) -> str:
        """
        Convert string to PascalCase (e.g. 'personal_detail' -> 'PersonalDetail').
        """
        if value is None:
            return ""
        words = re.split(r"[\s_\-]+", str(value).strip())
        return "".join(word.capitalize() for word in words if word)

    @staticmethod
    def remove_special_chars(value: Any) -> str:
        """
        Remove unwanted symbols.
        """
        if value is None:
            return ""
        return re.sub(r"[^a-zA-Z0-9\s]", "", str(value))

    @staticmethod
    def is_empty(value: Any) -> bool:
        """
        Return True for None, empty string, or whitespace string.
        """
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if not str(value).strip():
            return True
        return False

    @staticmethod
    def safe_str(value: Any) -> str:
        """
        Convert any input safely into string.
        """
        if value is None:
            return ""
        return str(value)

    # ==================================================
    # 2. DATE AND TIME UTILITIES
    # ==================================================

    @staticmethod
    def convert_date_format(
        date_value: Any, input_format: str, output_format: str
    ) -> str:
        """
        Convert date string from input_format to output_format.
        """
        if not date_value or not isinstance(date_value, str):
            return ""
        try:
            dt = datetime.strptime(date_value, input_format)
            return dt.strftime(output_format)
        except ValueError:
            return ""

    @staticmethod
    def get_current_timestamp() -> datetime:
        """
        Return current datetime.
        """
        return datetime.now()

    @staticmethod
    def get_utc_timestamp() -> datetime:
        """
        Return UTC datetime.
        """
        return datetime.now(timezone.utc)

    @staticmethod
    def _parse_date(d: Any) -> Optional[datetime]:
        """
        Helper to parse various date formats safely.
        """
        if isinstance(d, datetime):
            return d
        if isinstance(d, date):
            return datetime.combine(d, datetime.min.time())
        if isinstance(d, str):
            try:
                return datetime.fromisoformat(d)
            except ValueError:
                pass
        return None

    @staticmethod
    def date_difference(start_date: Any, end_date: Any) -> int:
        """
        Return difference in days between two dates.
        """
        sd = XSCUtility._parse_date(start_date)
        ed = XSCUtility._parse_date(end_date)
        if sd and ed:
            return (ed - sd).days
        return 0

    @staticmethod
    def calculate_age(dob: Any) -> int:
        """
        Calculate age from DOB.
        """
        dob_dt = XSCUtility._parse_date(dob)
        if not dob_dt:
            return 0
        today = datetime.now()
        age = (
            today.year
            - dob_dt.year
            - ((today.month, today.day) < (dob_dt.month, dob_dt.day))
        )
        return max(0, age)

    @staticmethod
    def get_academic_year() -> str:
        """
        Generate academic year. Example: 2026-2027
        """
        today = datetime.now()
        if today.month >= 6:
            return f"{today.year}-{today.year + 1}"
        else:
            return f"{today.year - 1}-{today.year}"

    # ==================================================
    # 3. EMAIL UTILITIES
    # ==================================================

    @staticmethod
    def validate_email(email: Any) -> bool:
        """
        Check valid email syntax using regex.
        """
        if not email or not isinstance(email, str):
            return False
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_domain_email(email: Any, domain: str) -> bool:
        """
        Check if email belongs to the specific domain.
        """
        if not XSCUtility.validate_email(email):
            return False
        if not domain or not isinstance(domain, str):
            return False
        return email.lower().endswith(f"@{domain.lower()}")

    @staticmethod
    def mask_email(email: Any) -> str:
        """
        Mask email address. (e.g. siddharth@gmail.com to sid*****@gmail.com)
        """
        if not email or not isinstance(email, str):
            return ""
        if "@" not in email:
            return email
        local_part, domain = email.split("@", 1)
        if len(local_part) <= 3:
            masked_local = local_part + "*****"
        else:
            masked_local = local_part[:3] + "*****"
        return f"{masked_local}@{domain}"

    # ==================================================
    # 4. PHONE UTILITIES
    # ==================================================

    @staticmethod
    def validate_phone(phone: Any) -> bool:
        """
        Validate Indian phone numbers.
        Accepts 10 digits, optional +91, 91 or 0 prefix.
        Valid starting digits: 6, 7, 8, 9
        """
        if not phone:
            return False
        phone_str = str(phone).strip()
        pattern = r"^(?:\+91|91|0)?[6-9]\d{9}$"
        return bool(re.match(pattern, phone_str))

    @staticmethod
    def format_phone(phone: Any, country_code: str = "+91") -> str:
        """
        Format phone with country code.
        """
        if not phone:
            return ""
        phone_str = str(phone).strip()
        digits = re.sub(r"\D", "", phone_str)
        if len(digits) == 10:
            return f"{country_code}{digits}"
        elif len(digits) == 12 and digits.startswith("91"):
            return f"{country_code}{digits[2:]}"
        return phone_str

    @staticmethod
    def mask_phone(phone: Any) -> str:
        """
        Mask phone number. (e.g. 9876543210 to 98765XXXXX)
        """
        if not phone:
            return ""
        phone_str = str(phone).strip()
        digits = re.sub(r"\D", "", phone_str)
        if len(digits) >= 10:
            return digits[:5] + "X" * (len(digits) - 5)
        return phone_str

    # ==================================================
    # 5. NUMBER UTILITIES
    # ==================================================

    @staticmethod
    def safe_int(value: Any) -> int:
        """
        Safely convert to int.
        """
        if value is None:
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def safe_float(value: Any) -> float:
        """
        Safely convert to float.
        """
        if value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def calculate_percentage(obtained: Any, total: Any) -> float:
        """
        Calculate percentage safely.
        """
        obt = XSCUtility.safe_float(obtained)
        tot = XSCUtility.safe_float(total)
        if tot == 0.0:
            return 0.0
        return (obt / tot) * 100.0

    @staticmethod
    def round_value(number: Any, decimal_places: int = 2) -> float:
        """
        Round a number to given decimal places.
        """
        num = XSCUtility.safe_float(number)
        return round(num, decimal_places)

    # ==================================================
    # 6. ID GENERATION UTILITIES
    # ==================================================

    @staticmethod
    def generate_uuid() -> str:
        """
        Return UUID string.
        """
        return str(uuid.uuid4())

    @staticmethod
    def generate_short_id(prefix: Optional[str] = None) -> str:
        """
        Generate short ID like STU-X82HD
        """
        chars = string.ascii_uppercase + string.digits
        random_str = "".join(random.choices(chars, k=5))
        if prefix:
            return f"{prefix}-{random_str}"
        return random_str

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """
        Generate numeric OTP.
        """
        if length <= 0:
            length = 6
        return "".join(random.choices(string.digits, k=length))

    # ==================================================
    # 7. JSON UTILITIES
    # ==================================================

    @staticmethod
    def is_valid_json(value: Any) -> bool:
        """
        Validate JSON string.
        """
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def parse_json(value: Any) -> Any:
        """
        Safely convert JSON string into dictionary or appropriate type.
        """
        if not isinstance(value, str):
            return {}
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return {}

    @staticmethod
    def format_json(data: Any) -> str:
        """
        Pretty print JSON.
        """
        try:
            return json.dumps(data, indent=4)
        except (ValueError, TypeError):
            return "{}"

    @staticmethod
    def to_json(data: Any) -> str:
        """
        Convert Python objects into JSON strings safely.
        """
        if data is None:
            return "{}"
        try:
            return json.dumps(data, default=str)
        except Exception:
            return "{}"

    @staticmethod
    def serialize_response(data: Any) -> Any:
        """
        Convert Python objects into JSON-safe Python structures.
        """
        if data is None:
            return None

        if isinstance(data, dict):
            return {str(k): XSCUtility.serialize_response(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple, set)):
            return [XSCUtility.serialize_response(v) for v in data]
        elif isinstance(data, (datetime, date)):
            return data.isoformat()
        elif isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, (int, float, str, bool)):
            return data
        else:
            return str(data)

    @staticmethod
    def json_to_bytes(data: Any) -> bytes:
        """
        Convert dictionary/list JSON data into bytes.
        """
        if data is None:
            return b"{}"
        try:
            return XSCUtility.to_json(data).encode("utf-8")
        except Exception:
            return b"{}"

    @staticmethod
    def bytes_to_json(data: Any) -> Any:
        """
        Convert bytes back into Python dictionary/list.
        """
        if not data or not isinstance(data, bytes):
            return {}
        try:
            decoded = data.decode("utf-8")
            return XSCUtility.parse_json(decoded)
        except Exception:
            return {}

    # ==================================================
    # 8. SECURITY UTILITIES
    # ==================================================

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Secure random token.
        """
        return secrets.token_hex(max(1, length // 2))

    @staticmethod
    def generate_hash(value: Any) -> str:
        """
        Generate SHA256 hash.
        """
        val_str = XSCUtility.safe_str(value)
        return hashlib.sha256(val_str.encode("utf-8")).hexdigest()

    @staticmethod
    def compare_hash(value: Any, hashed_value: Any) -> bool:
        """
        Compare plain text with hashed value.
        """
        if not value or not hashed_value:
            return False
        return XSCUtility.generate_hash(value) == str(hashed_value)

    # ==================================================
    # 9. FILE UTILITIES
    # ==================================================

    @staticmethod
    def validate_file_extension(filename: Any, allowed_extensions: List[str]) -> bool:
        """
        Validate file extension.
        """
        if not filename or not isinstance(filename, str):
            return False
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        return ext in [e.lower() for e in allowed_extensions]

    @staticmethod
    def validate_file_size(file_size: Any, max_mb: Any) -> bool:
        """
        Validate file size (file_size in bytes).
        """
        if file_size is None or max_mb is None:
            return False
        fs = XSCUtility.safe_int(file_size)
        mb = XSCUtility.safe_int(max_mb)
        if fs < 0 or mb <= 0:
            return False
        return fs <= (mb * 1024 * 1024)

    @staticmethod
    def sanitize_filename(filename: Any) -> str:
        """
        Sanitize filename to a safe format.
        """
        if not filename:
            return ""
        name = str(filename)
        name = name.replace(" ", "_").lower()
        name = re.sub(r"[^a-z0-9_.-]", "", name)
        return name

    # ==================================================
    # 10. DATABASE HELPER UTILITIES
    # ==================================================

    @staticmethod
    def generate_pagination(page: Any, limit: Any) -> Dict[str, int]:
        """
        Generate limit and offset for pagination.
        """
        p = XSCUtility.safe_int(page)
        l = XSCUtility.safe_int(limit)
        if p <= 0:
            p = 1
        if l <= 0:
            l = 10
        offset = (p - 1) * l
        return {"limit": l, "offset": offset}

    @staticmethod
    def remove_none_values(dictionary: Any) -> dict:
        """
        Remove keys having None values.
        """
        if not isinstance(dictionary, dict):
            return {}
        return {k: v for k, v in dictionary.items() if v is not None}

    @staticmethod
    def camel_to_snake(value: Any) -> str:
        """
        Convert camelCase to snake_case.
        """
        if not value or not isinstance(value, str):
            return ""
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def snake_to_camel(value: Any) -> str:
        """
        Convert snake_case to camelCase.
        """
        if not value or not isinstance(value, str):
            return ""
        parts = value.split("_")
        if not parts:
            return ""
        return parts[0] + "".join(word.title() for word in parts[1:] if word)

    # ==================================================
    # 11. ONEAPP SPECIFIC UTILITIES
    # ==================================================

    @staticmethod
    def validate_institution_id(value: Any) -> bool:
        """
        Validate institution ID.
        """
        val = XSCUtility.safe_str(value).strip()
        return bool(val)

    @staticmethod
    def normalize_roll_number(value: Any) -> str:
        """
        Convert roll number to uppercase and strip spaces.
        """
        if value is None:
            return ""
        return XSCUtility.safe_str(value).strip().upper()

    @staticmethod
    def validate_semester(value: Any) -> bool:
        """
        Validate semester (1-8).
        """
        val = XSCUtility.safe_int(value)
        return 1 <= val <= 8

    @staticmethod
    def validate_branch_code(value: Any) -> bool:
        """
        Validate branch code (CSE, ISE, ECE, EEE, ME).
        """
        valid_branches = {"CSE", "ISE", "ECE", "EEE", "ME"}
        if value is None:
            return False
        val = XSCUtility.safe_str(value).strip().upper()
        return val in valid_branches

    @staticmethod
    def normalize_attendance_status(value: Any) -> str:
        """
        Normalize attendance status to P or A.
        """
        if value is None:
            return ""
        val = XSCUtility.safe_str(value).strip().lower()
        if val in ("present", "p"):
            return "P"
        if val in ("absent", "a"):
            return "A"
        return ""

    # ==================================================
    # 12. BOOLEAN UTILITIES
    # ==================================================

    @staticmethod
    def safe_bool(value: Any) -> bool:
        """
        Safely convert different input types into boolean.
        """
        if value is True or value == 1:
            return True
        if isinstance(value, str):
            val = value.strip().lower()
            if val in ("1", "true", "yes", "y", "enabled", "active"):
                return True
        return False

    # ==================================================
    # 13. LIST CLEANING UTILITIES
    # ==================================================

    @staticmethod
    def clean_list(values: Any) -> List[Any]:
        """
        Clean incoming list data.
        """
        if not isinstance(values, list):
            return []

        cleaned = []
        for v in values:
            if v is None:
                continue
            if isinstance(v, str):
                v_str = v.strip()
                if not v_str:
                    continue
                cleaned.append(v_str)
            else:
                cleaned.append(v)
        return cleaned

    # ==================================================
    # 14. DICTIONARY SANITIZER
    # ==================================================

    @staticmethod
    def sanitize_dict(data: Any) -> Any:
        """
        Clean API payload dictionaries recursively.
        """
        if isinstance(data, dict):
            return {k: XSCUtility.sanitize_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [XSCUtility.sanitize_dict(v) for v in data]
        elif isinstance(data, str):
            return data.strip()
        else:
            return data

    # ==================================================
    # 15. SQL HELPER UTILITIES
    # ==================================================

    @staticmethod
    def escape_sql_like(value: Any) -> str:
        """
        Escape LIKE query special characters.
        """
        if not value or not isinstance(value, str):
            return ""
        return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    # ==================================================
    # 16. TIMEZONE SUPPORT
    # ==================================================

    @staticmethod
    def get_timestamp_with_timezone(timezone: str = "Asia/Kolkata") -> datetime:
        """
        Return timezone-aware datetime.
        """
        import zoneinfo

        try:
            tz = zoneinfo.ZoneInfo(timezone)
        except Exception:
            tz = timezone.utc
        return datetime.now(tz)

    # ==================================================
    # 17. PASSWORD VALIDATION
    # ==================================================

    @staticmethod
    def validate_password_strength(password: Any) -> Dict[str, Any]:
        """
        Validate password strength.
        """
        errors = []
        if not password or not isinstance(password, str):
            return {"valid": False, "errors": ["Invalid password format"]}

        if len(password) < 8:
            errors.append("Minimum 8 characters required")
        if not re.search(r"[A-Z]", password):
            errors.append("Missing uppercase letter")
        if not re.search(r"[a-z]", password):
            errors.append("Missing lowercase letter")
        if not re.search(r"\d", password):
            errors.append("Missing number")
        if not re.search(r"[^A-Za-z0-9]", password):
            errors.append("Missing special character")

        return {"valid": len(errors) == 0, "errors": errors}

    # ==================================================
    # 18. URL VALIDATION
    # ==================================================

    @staticmethod
    def validate_url(url: Any) -> bool:
        """
        Validate URLs stored in ERP.
        """
        if not url or not isinstance(url, str):
            return False
        from urllib.parse import urlparse

        try:
            result = urlparse(url)
            return all([result.scheme in ("http", "https"), result.netloc])
        except Exception:
            return False

    # ==================================================
    # 19. UUID VALIDATION
    # ==================================================

    @staticmethod
    def validate_uuid(value: Any) -> bool:
        """
        Check whether a string is valid UUID.
        """
        if not value or not isinstance(value, str):
            return False
        try:
            uuid_obj = uuid.UUID(value)
            return str(uuid_obj) == value.lower()
        except ValueError:
            return False

    # ==================================================
    # 20. ENUM VALIDATOR
    # ==================================================

    @staticmethod
    def validate_enum(value: Any, allowed_values: List[str]) -> bool:
        """
        Generic status/type validator.
        """
        if value is None or allowed_values is None:
            return False
        if not isinstance(value, str):
            return False
        lower_allowed = [str(x).lower() for x in allowed_values if x is not None]
        return value.lower() in lower_allowed

    # ==================================================
    # 21. ADVANCED STRING UTILITIES
    # ==================================================

    @staticmethod
    def generate_slug(value: Any) -> str:
        """
        Generate URL-friendly slug from string.
        """
        if not value or not isinstance(value, str):
            return ""
        val = value.lower().strip()
        val = re.sub(r"[^a-z0-9\s-]", "", val)
        val = re.sub(r"[\s-]+", "-", val)
        return val

    @staticmethod
    def generate_initials(name: Any) -> str:
        """
        Generate initials from a name.
        """
        if not name or not isinstance(name, str):
            return ""
        parts = [p for p in name.strip().split() if p]
        if not parts:
            return ""
        return "".join([p[0].upper() for p in parts[:2]])

    @staticmethod
    def truncate_string(value: Any, max_length: int, suffix: str = "...") -> str:
        """
        Truncate string to max length.
        """
        if not value or not isinstance(value, str):
            return ""
        if len(value) <= max_length:
            return value
        return value[:max_length].rstrip() + suffix

    @staticmethod
    def string_similarity(first: Any, second: Any) -> float:
        """
        Calculate string similarity percentage.
        """
        if not isinstance(first, str) or not isinstance(second, str):
            return 0.0
        return difflib.SequenceMatcher(None, first, second).ratio() * 100

    @staticmethod
    def strip_html(value: Any) -> str:
        """
        Strip HTML tags from string.
        """
        if not value or not isinstance(value, str):
            return ""
        return re.sub(r"<[^>]*>", "", value).strip()

    # ==================================================
    # 22. ADVANCED DATE UTILITIES
    # ==================================================

    @staticmethod
    def time_ago(timestamp: Any) -> str:
        """
        Convert timestamp to relative time ago.
        """
        if not isinstance(timestamp, datetime):
            return ""
        if timestamp.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.now(timestamp.tzinfo)
        diff = now - timestamp
        if diff.total_seconds() < 60:
            return "just now"
        elif diff.total_seconds() < 3600:
            mins = int(diff.total_seconds() / 60)
            return f"{mins} minute{'s' if mins > 1 else ''} ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = diff.days
            return f"{days} day{'s' if days > 1 else ''} ago"

    @staticmethod
    def is_weekend(dt: Any) -> bool:
        """
        Check if date is weekend.
        """
        if not isinstance(dt, (datetime, date)):
            return False
        return dt.weekday() >= 5

    @staticmethod
    def business_days_between(start_date: Any, end_date: Any) -> int:
        """
        Calculate business days excluding weekends.
        """
        if not isinstance(start_date, (datetime, date)) or not isinstance(
            end_date, (datetime, date)
        ):
            return 0
        if start_date > end_date:
            start_date, end_date = end_date, start_date

        days = 0
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:
                days += 1
            current += timedelta(days=1)
        return days

    @staticmethod
    def date_range(start_date: Any, end_date: Any) -> List[date]:
        """
        Return list of dates between start and end.
        """
        if not isinstance(start_date, (datetime, date)) or not isinstance(
            end_date, (datetime, date)
        ):
            return []
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        if start_date > end_date:
            return []

        result = []
        current = start_date
        while current <= end_date:
            result.append(current)
            current += timedelta(days=1)
        return result

    @staticmethod
    def get_financial_year() -> str:
        """
        Get Indian financial year based on current date.
        """
        today = date.today()
        if today.month >= 4:
            return f"{today.year}-{today.year + 1}"
        else:
            return f"{today.year - 1}-{today.year}"

    # ==================================================
    # 23. INDIA SPECIFIC VALIDATORS
    # ==================================================

    @staticmethod
    def validate_aadhaar(number: Any) -> bool:
        """
        Validate Aadhaar format.
        """
        if not number:
            return False
        num = str(number).strip()
        return bool(re.match(r"^\d{12}$", num))

    @staticmethod
    def mask_aadhaar(number: Any) -> str:
        """
        Mask first 8 digits of Aadhaar.
        """
        if not number:
            return ""
        num = str(number).strip()
        if len(num) == 12 and num.isdigit():
            return "XXXXXXXX" + num[-4:]
        return num

    @staticmethod
    def validate_pan(value: Any) -> bool:
        """
        Validate PAN card format.
        """
        if not value or not isinstance(value, str):
            return False
        return bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", value.strip().upper()))

    @staticmethod
    def validate_pincode(value: Any) -> bool:
        """
        Validate Indian pincode format.
        """
        if not value:
            return False
        val = str(value).strip()
        return bool(re.match(r"^[1-9][0-9]{5}$", val))

    @staticmethod
    def validate_blood_group(value: Any) -> bool:
        """
        Validate blood group.
        """
        if not value or not isinstance(value, str):
            return False
        allowed = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
        return value.strip().upper() in allowed

    @staticmethod
    def validate_coordinates(latitude: Any, longitude: Any) -> bool:
        """
        Validate GPS coordinates.
        """
        if latitude is None or longitude is None:
            return False
        try:
            lat = float(latitude)
            lon = float(longitude)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (ValueError, TypeError):
            return False

    # ==================================================
    # 24. ADVANCED FILE UTILITIES
    # ==================================================

    @staticmethod
    def get_file_extension(filename: Any) -> str:
        """
        Get file extension without dot.
        """
        if not filename or not isinstance(filename, str):
            return ""
        parts = filename.strip().split(".")
        if len(parts) > 1:
            return parts[-1].lower()
        return ""

    @staticmethod
    def validate_mime_type(mime_type: Any, allowed_types: List[str]) -> bool:
        """
        Validate mime type.
        """
        if not mime_type or not isinstance(mime_type, str) or not allowed_types:
            return False
        return mime_type.strip().lower() in [t.lower() for t in allowed_types]

    @staticmethod
    def format_file_size(size_bytes: Any) -> str:
        """
        Format file size into human readable string.
        """
        try:
            size = float(size_bytes)
            if size < 0:
                return "0 B"
        except (ValueError, TypeError):
            return "0 B"

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:g} {unit}"
            size /= 1024.0
        return f"{size:g} PB"

    @staticmethod
    def generate_file_hash(file_data: Any) -> str:
        """
        Generate SHA256 hash of file data.
        """
        if not isinstance(file_data, bytes):
            if isinstance(file_data, str):
                file_data = file_data.encode("utf-8")
            else:
                return ""
        return hashlib.sha256(file_data).hexdigest()

    @staticmethod
    def generate_upload_path(institution_id: Any, module: Any, filename: Any) -> str:
        """
        Generate standard upload path.
        """
        if not all([institution_id, module, filename]):
            return ""
        return f"{str(institution_id).strip()}/{str(module).strip()}/{str(filename).strip()}"

    # ==================================================
    # 25. ENCODING AND CHECKSUM
    # ==================================================

    @staticmethod
    def base64_encode(value: Any) -> str:
        """
        Encode string to Base64.
        """
        if not value or not isinstance(value, str):
            return ""
        return base64.b64encode(value.encode("utf-8")).decode("utf-8")

    @staticmethod
    def base64_decode(value: Any) -> str:
        """
        Decode Base64 string.
        """
        if not value or not isinstance(value, str):
            return ""
        try:
            return base64.b64decode(value.encode("utf-8")).decode("utf-8")
        except Exception:
            return ""

    @staticmethod
    def generate_checksum(data: Any) -> str:
        """
        Generate SHA256 checksum of data.
        """
        if data is None:
            return ""
        try:
            if isinstance(data, dict) or isinstance(data, list):
                val = json.dumps(data, sort_keys=True)
            else:
                val = str(data)
            return hashlib.sha256(val.encode("utf-8")).hexdigest()
        except Exception:
            return ""

    @staticmethod
    def verify_checksum(data: Any, checksum: Any) -> bool:
        """
        Verify SHA256 checksum.
        """
        if not checksum or not isinstance(checksum, str):
            return False
        return XSCUtility.generate_checksum(data) == checksum

    # ==================================================
    # 26. COLLECTION UTILITIES
    # ==================================================

    @staticmethod
    def remove_duplicates(lst: Any) -> list:
        """
        Remove duplicates from list preserving order.
        """
        if not isinstance(lst, list):
            return []
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]

    @staticmethod
    def flatten_list(lst: Any) -> list:
        """
        Flatten a nested list.
        """
        if not isinstance(lst, list):
            return []
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(XSCUtility.flatten_list(item))
            else:
                result.append(item)
        return result

    @staticmethod
    def chunk_list(data: Any, size: int) -> list:
        """
        Split list into chunks.
        """
        if not isinstance(data, list) or not isinstance(size, int) or size <= 0:
            return []
        return [data[i : i + size] for i in range(0, len(data), size)]

    # ==================================================
    # 27. API RESPONSE UTILITIES
    # ==================================================

    @staticmethod
    def success_response(message: str = "", data: Any = None, **kwargs) -> dict:
        """
        Generate standard success API response.
        Supports arbitrary keyword arguments to preserve backwards compatibility with custom keys.
        """
        response = {
            "status": "success",
        }
        if message:
            response["message"] = str(message)
        if data is not None:
            response["data"] = data

        response.update(kwargs)
        return response

    @staticmethod
    def error_response(message: str, error_code: Any = None) -> dict:
        """
        Generate standard error API response.
        """
        return {
            "status": "error",
            "message": str(message) if message else "",
            "error_code": str(error_code) if error_code is not None else "",
        }

    @staticmethod
    def generate_request_id() -> str:
        """
        Generate unique request ID.
        """
        return f"REQ-{uuid.uuid4().hex[:8].upper()}"

    # ==================================================
    # 28. AUDIT UTILITIES
    # ==================================================

    @staticmethod
    def generate_audit_payload(user_id: Any, action: Any, metadata: Any = None) -> dict:
        """
        Generate audit log payload.
        """
        return {
            "user_id": str(user_id) if user_id else "",
            "action": str(action) if action else "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata if isinstance(metadata, dict) else {},
        }

    @staticmethod
    def compare_dict_changes(old_data: Any, new_data: Any) -> dict:
        """
        Compare two dictionaries and return changes.
        """
        if not isinstance(old_data, dict) or not isinstance(new_data, dict):
            return {}

        changes = {}
        all_keys = set(old_data.keys()).union(set(new_data.keys()))
        for key in all_keys:
            old_val = old_data.get(key)
            new_val = new_data.get(key)
            if old_val != new_val:
                changes[key] = {"old": old_val, "new": new_val}
        return changes

    # ==================================================
    # 29. TENANT UTILITIES
    # ==================================================

    @staticmethod
    def generate_tenant_code(name: Any) -> str:
        """
        Generate a short tenant code from name.
        """
        if not name or not isinstance(name, str):
            return ""
        words = name.strip().split()
        if not words:
            return ""

        code = ""
        for word in words:
            if word.isupper():
                code += word
            else:
                code += word[0].upper()
        return code

    @staticmethod
    def validate_tenant_status(status: Any) -> bool:
        """
        Validate tenant status.
        """
        if not status or not isinstance(status, str):
            return False
        return status.strip().upper() in {"ACTIVE", "SUSPENDED", "TRIAL", "DISABLED"}

    @staticmethod
    def generate_tenant_url(tenant_code: Any, base_domain: Any) -> str:
        """
        Generate tenant specific URL.
        """
        if not tenant_code or not base_domain:
            return ""
        return f"{str(tenant_code).strip().lower()}.{str(base_domain).strip().lower()}"

    # ==================================================
    # 30. RBAC UTILITIES
    # ==================================================

    @staticmethod
    def build_permission_key(module: Any, submodule: Any, action: Any) -> str:
        """
        Build standard permission key.
        """
        if not all([module, submodule, action]):
            return ""
        return f"{str(module).strip().lower()}.{str(submodule).strip().lower()}.{str(action).strip().lower()}"

    @staticmethod
    def normalize_role(role: Any) -> str:
        """
        Normalize role name.
        """
        if not role or not isinstance(role, str):
            return ""
        return re.sub(r"\s+", "_", role.strip()).upper()

    # ==================================================
    # 31. NOTIFICATION UTILITIES
    # ==================================================

    @staticmethod
    def render_template(template: Any, data: Any) -> str:
        """
        Render string template with dict data.
        """
        if not template or not isinstance(template, str):
            return ""
        if not isinstance(data, dict):
            return template
        try:
            return template.format(**data)
        except KeyError:
            return template

    @staticmethod
    def validate_priority(priority: Any) -> bool:
        """
        Validate notification priority.
        """
        if not priority or not isinstance(priority, str):
            return False
        return priority.strip().upper() in {"LOW", "NORMAL", "HIGH", "CRITICAL"}

    # ==================================================
    # 32. CACHE UTILITIES
    # ==================================================

    @staticmethod
    def generate_cache_key(*args: Any) -> str:
        """
        Generate standard cache key.
        """
        return ":".join([str(a).strip() for a in args if a])

    @staticmethod
    def hash_dict(dictionary: Any) -> str:
        """
        Generate stable hash of dictionary.
        """
        if not isinstance(dictionary, dict):
            return ""
        try:
            json_str = json.dumps(dictionary, sort_keys=True)
            return hashlib.md5(json_str.encode("utf-8")).hexdigest()
        except Exception:
            return ""

    # ==================================================
    # 33. ENVIRONMENT UTILITIES
    # ==================================================

    @staticmethod
    def get_env(key: Any, default: Any = None) -> Any:
        """
        Read environment variables safely.
        """
        if not key or not isinstance(key, str):
            return default
        return os.environ.get(key, default)

    @staticmethod
    def is_production() -> bool:
        """
        Check if environment is production.
        """
        env = os.environ.get("APP_ENV", "").strip().lower()
        return env in {"prod", "production"}

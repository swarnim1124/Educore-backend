"""
File: sch_curriculum.py
Description: Payload validation logic for m_curriculum using standard Python dictionaries
to maintain lightweight framework standards akin to m_AAA.

Author: Siddharth Amdal
App: OneApp

"""


class CurriculumValidator:
    """
    Validates incoming JSON payloads based on the module's API Contract.
    """

    @staticmethod
    def validate_programme_add(payload: dict) -> list[str]:
        errors = []
        required = [
            "institutionId",
            "departmentId",
            "progCode",
            "progName",
            "progTypeId",
            "duration",
            "durationUnitId",
            "totalTerms",
            "totalCredits",
            "statusId",
        ]
        for field in required:
            if not payload.get(field):
                errors.append(f"Missing required field: {field}")
        return errors

    @staticmethod
    def validate_course_definition_add(payload: dict) -> list[str]:
        errors = []
        required = ["crsCode", "crsName", "crsTypeId", "creditValue", "statusId"]
        for field in required:
            if payload.get(field) is None:
                errors.append(f"Missing required field: {field}")
        return errors

    @staticmethod
    def validate_course_definition_update(payload: dict) -> list[str]:
        errors = []
        if not payload.get("courseDefinitionId"):
            errors.append("Missing required field: courseDefinitionId")
        return errors

    @staticmethod
    def validate_course_requisite_add(payload: dict) -> list[str]:
        errors = []
        required = [
            "crsVersionId",
            "requisiteCrsVersionId",
            "requisiteType",
            "statusId",
        ]
        for field in required:
            if payload.get(field) is None:
                errors.append(f"Missing required field: {field}")
        return errors

    @staticmethod
    def validate_course_requisite_delete(payload: dict) -> list[str]:
        errors = []
        if not payload.get("requisiteId"):
            errors.append("Missing required field: requisiteId")
        return errors

    @staticmethod
    def validate_curriculum_add(payload: dict) -> list[str]:
        errors = []
        if not payload.get("progId"):
            errors.append("Missing required field: progId")
        if not payload.get("currName"):
            errors.append("Missing required field: currName")
        if not payload.get("terms") or not isinstance(payload.get("terms"), list):
            errors.append("Missing or invalid terms array")
        return errors

    @staticmethod
    def validate_curriculum_update(payload: dict) -> list[str]:
        errors = []
        if not payload.get("currId"):
            errors.append("Missing required field: currId")
        if payload.get("terms") is not None and not isinstance(
            payload.get("terms"), list
        ):
            errors.append("Invalid terms array")
        return errors

    @staticmethod
    def validate_curriculum_delete(payload: dict) -> list[str]:
        errors = []
        if not payload.get("currId"):
            errors.append("Missing required field: currId")
        return errors

    @staticmethod
    def validate_curriculum_approval(payload: dict) -> list[str]:
        errors = []
        if not payload.get("currVersionId"):
            errors.append("Missing required field: currVersionId")
        return errors

    @staticmethod
    def validate_enrollment_add(payload: dict) -> list[str]:
        errors = []
        required = [
            "studId",
            "progIntakeId",
            "admTypeId",
            "enrollmentDate",
            "expectedGraduationDate",
        ]
        for field in required:
            if payload.get(field) is None:
                errors.append(f"Missing required field: {field}")
        return errors

    @staticmethod
    def validate_enrollment_update(payload: dict) -> list[str]:
        errors = []
        if not payload.get("enrollmentId"):
            errors.append("Missing required field: enrollmentId")
        return errors

    @staticmethod
    def validate_enrollment_delete(payload: dict) -> list[str]:
        errors = []
        if not payload.get("enrollmentId"):
            errors.append("Missing required field: enrollmentId")
        return errors

    @staticmethod
    def validate_semester_registration_add(payload: dict) -> list[str]:
        errors = []
        if not payload.get("studId"):
            errors.append("Missing required field: studId")
        if not payload.get("crsOfferingIds") or not isinstance(
            payload.get("crsOfferingIds"), list
        ):
            errors.append("Missing or invalid crsOfferingIds array")
        return errors

    @staticmethod
    def validate_semester_registration_update(payload: dict) -> list[str]:
        errors = []
        if not payload.get("registrationId"):
            errors.append("Missing required field: registrationId")
        if not payload.get("registrationStatusId"):
            errors.append("Missing required field: registrationStatusId")
        return errors

    @staticmethod
    def validate_semester_registration_delete(payload: dict) -> list[str]:
        errors = []
        if not payload.get("registrationId"):
            errors.append("Missing required field: registrationId")
        return errors

    @staticmethod
    def validate_elective_registration_add(payload: dict) -> list[str]:
        errors = []
        if not payload.get("studId"):
            errors.append("Missing required field: studId")
        if not payload.get("electiveCrsOfferingId"):
            errors.append("Missing required field: electiveCrsOfferingId")
        return errors

    @staticmethod
    def validate_elective_registration_update(payload: dict) -> list[str]:
        errors = []
        if not payload.get("registrationId"):
            errors.append("Missing required field: registrationId")
        if not payload.get("newCrsOfferingId"):
            errors.append("Missing required field: newCrsOfferingId")
        return errors

    @staticmethod
    def validate_elective_registration_delete(payload: dict) -> list[str]:
        errors = []
        if not payload.get("registrationId"):
            errors.append("Missing required field: registrationId")
        return errors

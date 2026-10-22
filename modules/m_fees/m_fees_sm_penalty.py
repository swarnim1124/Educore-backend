"""
File: m_fees_sm_penalty.py
Description: Handler for Penalty configuration.
"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_fees_data import FeePenaltyData
from .sch_fees import FeesValidator

logger = logging.getLogger(__name__)


class sm_penalty:
    @staticmethod
    async def feePenalty(request, context):
        action_type = request.actionType.lower()
        if action_type == "add":
            return await sm_penalty.add(request, context)
        if action_type == "view":
            return await sm_penalty.view(request, context)
        if action_type == "update":
            return await sm_penalty.update(request, context)
        if action_type == "delete":
            return await sm_penalty.delete(request, context)
        return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def add(request, context):
        payload, error = FeesValidator.validate(request.payload, "feePenalty", "add")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            await FeePenaltyData.create_penalty(session, payload)
            await session.commit()
            return XSCUtility.success_response("Penalty configuration saved")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in feePenalty_add: {str(e)}")
            return XSCUtility.error_response("Failed to save penalty rule")
        finally:
            await session.close()

    @staticmethod
    async def view(request, context):
        # structured TODO
        # - Why it cannot be completed: Phase 2 DAL (FeePenaltyData) lacks a `get_penalties` method.
        # - Missing artifact: Phase 2 DAL extension.
        # - Clarification required: Search criteria for penalty configurations.
        # - Architectural assumption: Raw SQL execution in the Business Layer.
        return XSCUtility.success_response("feePenalty view not fully implemented")

    @staticmethod
    async def update(request, context):
        # structured TODO
        # - Why it cannot be completed: The payload for updating a penalty rule is not defined.
        # - Missing artifact: Module Specification for penalty modification.
        # - Clarification required: Does updating an active rule recalculate existing overdue balances, or only apply prospectively?
        # - Architectural assumption: Inventing retroactive financial rules.
        return XSCUtility.success_response("feePenalty update not fully implemented")

    @staticmethod
    async def delete(request, context):
        # structured TODO
        # - Why it cannot be completed: BRS mentions "Removing a penalty rule stops future accruals". DAL lacks `update_penalty` to deactivate.
        # - Missing artifact: Phase 2 DAL implementation for deactivating penalty rules.
        # - Clarification required: Is it a soft delete (is_active = False) or a hard delete?
        # - Architectural assumption: Raw SQL execution in Phase 3.
        return XSCUtility.success_response("feePenalty delete not fully implemented")

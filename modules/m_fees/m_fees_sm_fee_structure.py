"""
File: m_fees_sm_fee_structure.py
Description: Handler for Fee Structure entity in m_fees.
"""

import logging
from xsc_lib.xsc_lib_common.xsc_libc_utility import XSCUtility
from .m_fees_data import FeeStructureData
from .sch_fees import FeesValidator

logger = logging.getLogger(__name__)


class sm_fee_structure:
    @staticmethod
    async def feeStructure(request, context):
        action_type = request.actionType.lower()
        if action_type == "add":
            return await sm_fee_structure.add(request, context)
        if action_type == "view":
            return await sm_fee_structure.view(request, context)
        if action_type == "update":
            return await sm_fee_structure.update(request, context)
        if action_type == "delete":
            return await sm_fee_structure.delete(request, context)
        return XSCUtility.error_response("Invalid actionType")

    @staticmethod
    async def add(request, context):
        payload, error = FeesValidator.validate(request.payload, "feeStructure", "add")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            logger.info("Entering feeStructure_add")
            entity = await FeeStructureData.create_fee_structure(session, payload)
            await session.commit()
            return XSCUtility.success_response(
                "Fee Structure created successfully",
                data={"fee_structure_id": entity.id},
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in feeStructure_add: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Database error occurred.")
        finally:
            await session.close()

    @staticmethod
    async def view(request, context):
        payload, error = FeesValidator.validate(request.payload, "feeStructure", "view")
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            limit = payload.get("limit", 100)
            offset = payload.get("offset", 0)
            records = await FeeStructureData.get_fee_structures(session, limit, offset)
            return XSCUtility.success_response(
                "Data fetched",
                data=[
                    {"fee_structure_id": r.id, "name": r.fee_structure_name}
                    for r in records
                ],
            )
        except Exception as e:
            logger.error(f"Error in feeStructure_view: {str(e)}", exc_info=True)
            return XSCUtility.error_response("Error fetching data")
        finally:
            await session.close()

    @staticmethod
    async def update(request, context):
        payload, error = FeesValidator.validate(
            request.payload, "feeStructure", "update"
        )
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            struct_id = payload.pop("feeStructureId")
            entity = await FeeStructureData.update_fee_structure(
                session, struct_id, payload
            )
            await session.commit()
            return XSCUtility.success_response(
                "Updated successfully", data={"fee_structure_id": entity.id}
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Error in feeStructure_update: {str(e)}")
            return XSCUtility.error_response("Update failed")
        finally:
            await session.close()

    @staticmethod
    async def delete(request, context):
        payload, error = FeesValidator.validate(
            request.payload, "feeStructure", "delete"
        )
        if error:
            return XSCUtility.error_response("Validation failed", error_code=error)

        session = context.postgres.async_session_maker()
        try:
            struct_id = payload.get("feeStructureId")
            entity = await FeeStructureData.update_fee_structure(
                session, struct_id, {"is_active": False}
            )
            await session.commit()
            return XSCUtility.success_response(
                "Deactivated successfully", data={"fee_structure_id": struct_id}
            )
        except Exception:
            await session.rollback()
            return XSCUtility.error_response("Deletion failed")
        finally:
            await session.close()


# Alias for legacy camelCase class reference
sm_feeStructure = sm_fee_structure

"""KYC (Know Your Customer) endpoints for merchant onboarding"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select

from apps.api.core.database import get_db
from apps.api.models.merchant import Merchant, MerchantStatus, KYCStatus

router = APIRouter()


class KYCSubmitRequest(BaseModel):
    """Request to submit KYC documents."""
    document_type: str
    document_number: str


class KYCStatusResponse(BaseModel):
    """KYC status response."""
    kyc_status: str
    documents_submitted: list[dict]
    verification_notes: Optional[str]


class KYBDocument(BaseModel):
    """KYC document metadata."""
    type: str
    url: Optional[str]
    uploaded_at: datetime


@router.post("/kyc/submit", response_model=KYCStatusResponse)
async def submit_kyc(
    request: KYCSubmitRequest,
    merchant: Merchant = Depends(get_current_merchant_for_kyc),
):
    """Submit KYC documents for verification."""
    if merchant.kyc_status == KYCStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already verified",
        )

    import json
    current_docs = merchant.kyc_documents or {}

    new_doc = {
        "type": request.document_type,
        "number": request.document_number,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending_review",
    }

    if "documents" not in current_docs:
        current_docs["documents"] = []

    current_docs["documents"].append(new_doc)
    current_docs["last_submitted"] = datetime.now(timezone.utc).isoformat()

    merchant.kyc_documents = current_docs
    merchant.kyc_status = KYCStatus.SUBMITTED

    async with get_db() as db:
        db.add(merchant)
        await db.commit()

    return KYCStatusResponse(
        kyc_status=merchant.kyc_status,
        documents_submitted=current_docs.get("documents", []),
        verification_notes=None,
    )


@router.get("/kyc/status", response_model=KYCStatusResponse)
async def get_kyc_status(
    merchant: Merchant = Depends(get_current_merchant_for_kyc),
):
    """Get current KYC status."""
    docs = merchant.kyc_documents or {}

    notes = None
    if merchant.kyc_status == KYCStatus.REJECTED:
        notes = docs.get("rejection_reason", "Documents rejected. Please resubmit.")
    elif merchant.kyc_status == KYCStatus.VERIFIED:
        notes = "Verification complete. Your account is fully activated."

    return KYCStatusResponse(
        kyc_status=merchant.kyc_status,
        documents_submitted=docs.get("documents", []),
        verification_notes=notes,
    )


async def get_current_merchant_for_kyc(
    merchant: Merchant = Depends(get_merchant_from_auth),
) -> Merchant:
    """Get merchant from auth - placeholder for actual auth dependency."""
    return merchant


async def get_merchant_from_auth() -> Merchant:
    """Placeholder for merchant authentication - would be replaced by actual auth."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required for KYC",
    )


@router.post("/kyc/verify/{merchant_id}")
async def admin_verify_kyc(
    merchant_id: uuid.UUID,
    approved: bool,
    notes: Optional[str] = None,
    admin_user: str = "admin",
):
    """Admin endpoint to approve/reject KYC documents."""
    async with get_db() as db:
        result = await db.execute(
            select(Merchant).where(Merchant.id == merchant_id)
        )
        merchant = result.scalar_one_or_none()

        if not merchant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Merchant not found",
            )

        if approved:
            merchant.kyc_status = KYCStatus.VERIFIED
            merchant.status = MerchantStatus.ACTIVE
            if "admin_verified" not in (merchant.kyc_documents or {}):
                merchant.kyc_documents = merchant.kyc_documents or {}
                merchant.kyc_documents["admin_verified"] = {
                    "at": datetime.now(timezone.utc).isoformat(),
                    "by": admin_user,
                }
        else:
            merchant.kyc_status = KYCStatus.REJECTED
            merchant.kyc_documents = merchant.kyc_documents or {}
            merchant.kyc_documents["rejection_reason"] = notes or "Documents rejected"

        await db.commit()

        return {
            "merchant_id": str(merchant.id),
            "kyc_status": merchant.kyc_status,
            "approved": approved,
        }


@router.post("/kyc/upload/{document_type}")
async def upload_kyc_document(
    document_type: str,
    file: UploadFile = File(...),
    merchant: Merchant = Depends(get_current_merchant_for_kyc),
):
    """Upload KYC document file."""
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, JPEG, and PNG files are allowed",
        )

    # In production, this would upload to cloud storage (S3, etc.)
    # For now, we just track the metadata
    import json
    docs = merchant.kyc_documents or {}

    upload_record = {
        "type": document_type,
        "filename": file.filename,
        "content_type": file.content_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "status": "uploaded",
    }

    if "uploads" not in docs:
        docs["uploads"] = []

    docs["uploads"].append(upload_record)
    merchant.kyc_documents = docs

    async with get_db() as db:
        db.add(merchant)
        await db.commit()

    return {
        "status": "uploaded",
        "document_type": document_type,
        "filename": file.filename,
    }
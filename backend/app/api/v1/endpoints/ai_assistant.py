from typing import Any, Dict, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.ai_assistant.service import AIAssistantService
from app.services.ai_assistant.schemas import AssistantResponse
from app.services.ai_assistant.reporting_models import AnalystReport, ExecutiveSummary
from app.services.ai_assistant.context_builder import InvestigationContextBuilder
from app.api.deps import get_db, get_current_user, log_activity
from app.db.models.employee import EmployeeRecord

router = APIRouter()
ai_service = AIAssistantService()
context_builder = InvestigationContextBuilder()


class AskQuestionRequest(BaseModel):
    """
    Request body for executing conversational question-answering on an indicator.
    """
    indicator: str = Field(..., description="The indicator URL, domain, or IP")
    query: str = Field(..., description="The analyst's question or prompt")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Unified evidence payload from Stage 5")
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Risk scoring payload from Stage 6")
    campaign_details: Optional[Dict[str, Any]] = Field(None, description="Campaign details from Stage 7")


class ReportGenerationRequest(BaseModel):
    """
    Request body for compiling structured analyst or executive reports.
    """
    indicator: str = Field(..., description="The indicator URL, domain, or IP")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Unified evidence payload from Stage 5")
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Risk scoring payload from Stage 6")
    campaign_details: Optional[Dict[str, Any]] = Field(None, description="Campaign details from Stage 7")


@router.post(
    "/ask",
    response_model=AssistantResponse,
    status_code=status.HTTP_200_OK,
    summary="Query AI Investigation Assistant",
    description="Analyzes structured evidence context using AI reasoning to answer analyst security questions."
)
async def ask_question(
    request: AskQuestionRequest,
    req_obj: Request,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    if not request.indicator.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Indicator cannot be empty.")
    if not request.query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    log_activity(db, current_user.user_id, "ai_assistant_query", req_obj, request.indicator)

    try:
        context = context_builder.build_context(
            indicator=request.indicator,
            evidence=request.evidence,
            risk_assessment=request.risk_assessment,
            campaign_details=request.campaign_details,
        )
        return await ai_service.ask_question(query=request.query, context=context)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing AI assistant query: {str(e)}"
        )


@router.post(
    "/report/analyst",
    response_model=AnalystReport,
    status_code=status.HTTP_200_OK,
    summary="Generate Analyst Technical Report",
    description="Compiles detailed, technical audit trail timelines and containment guidelines for SOC analysts."
)
async def get_analyst_report(
    request: ReportGenerationRequest,
    req_obj: Request,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    if not request.indicator.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Indicator cannot be empty.")

    log_activity(db, current_user.user_id, "report_export", req_obj, request.indicator)

    try:
        context = context_builder.build_context(
            indicator=request.indicator,
            evidence=request.evidence,
            risk_assessment=request.risk_assessment,
            campaign_details=request.campaign_details,
        )
        return await ai_service.get_analyst_report(context=context)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analyst report: {str(e)}"
        )


@router.post(
    "/report/executive",
    response_model=ExecutiveSummary,
    status_code=status.HTTP_200_OK,
    summary="Generate Executive Business Summary",
    description="Compiles high-level, business-oriented impact evaluations and containment timelines for C-level presentation."
)
async def get_executive_summary(
    request: ReportGenerationRequest,
    req_obj: Request,
    db: Session = Depends(get_db),
    current_user: EmployeeRecord = Depends(get_current_user)
) -> Any:
    if not request.indicator.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Indicator cannot be empty.")

    log_activity(db, current_user.user_id, "report_export", req_obj, request.indicator)

    try:
        context = context_builder.build_context(
            indicator=request.indicator,
            evidence=request.evidence,
            risk_assessment=request.risk_assessment,
            campaign_details=request.campaign_details,
        )
        return await ai_service.get_executive_summary(context=context)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating executive summary: {str(e)}"
        )

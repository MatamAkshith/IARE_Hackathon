import logging
from typing import List

from app.services.ai_assistant.base import BaseAIAssistantService
from app.services.ai_assistant.context_builder import InvestigationContextBuilder
from app.services.ai_assistant.schemas import AssistantResponse, AssistantMessage, InvestigationContext
from app.services.ai_assistant.models import ResponseType
from app.services.ai_assistant.reasoning import InvestigationReasoningService
from app.services.ai_assistant.reporting_models import ExecutiveSummary, AnalystReport
from app.services.ai_assistant.report_generator import ReportGeneratorService

logger = logging.getLogger("app.services.ai_assistant.service")


class AIAssistantService(BaseAIAssistantService):
    """
    Service layer orchestrating the AI Investigation Assistant.
    Coordinates prompt construction, deterministic reasoning execution,
    and structured report summaries generation.
    """

    def __init__(self) -> None:
        self.context_builder = InvestigationContextBuilder()
        self.reasoning_service = InvestigationReasoningService()
        self.report_generator = ReportGeneratorService()
        logger.info("AIAssistantService initialized successfully.")

    async def generate_summary(self, context: InvestigationContext) -> AssistantResponse:
        """
        Assembles prompt context and queries the reasoning service to generate a technical investigation report summary.
        """
        logger.info(f"[generate_summary] Invoked for indicator '{context.indicator}'")

        system_prompt = self.context_builder.generate_system_prompt(context)
        logger.debug(f"[generate_summary] Built prompt length: {len(system_prompt)} chars")

        # Route to risk explanation logic for summary
        response = self.reasoning_service.answer_question("Why is this URL risky?", context)
        response.response_type = ResponseType.SUMMARY
        return response

    async def chat(
        self,
        context: InvestigationContext,
        history: List[AssistantMessage],
        message: str,
    ) -> AssistantResponse:
        """
        Continues a conversational dialog with the analyst, referencing historical logs
        and indicator context details.
        """
        logger.info(f"[chat] Invoked for indicator '{context.indicator}' with {len(history)} historical message(s)")

        # Route query through reasoning engine keyword router
        response = self.reasoning_service.answer_question(message, context)
        response.response_type = ResponseType.CHAT
        return response

    def ask_question(self, query: str, context: InvestigationContext) -> AssistantResponse:
        """
        Exposes reasoning engine question routing directly as a synchronous method.
        """
        logger.info(f"[ask_question] Querying reasoning engine for '{query}' on indicator '{context.indicator}'")
        return self.reasoning_service.answer_question(query, context)

    def get_analyst_report(self, context: InvestigationContext) -> AnalystReport:
        """
        Generates a detailed, structured technical report for SOC analyst consumption.
        """
        logger.info(f"[get_analyst_report] Creating analyst report for '{context.indicator}'")
        return self.report_generator.generate_analyst_report(context)

    def get_executive_summary(self, context: InvestigationContext) -> ExecutiveSummary:
        """
        Generates a high-level business risk overview for C-level consumption.
        """
        logger.info(f"[get_executive_summary] Creating executive summary for '{context.indicator}'")
        return self.report_generator.generate_executive_summary(context)

import logging
from typing import List

from app.core.config import settings
from app.services.ai_assistant.base import BaseAIAssistantService
from app.services.ai_assistant.context_builder import InvestigationContextBuilder
from app.services.ai_assistant.schemas import AssistantResponse, AssistantMessage, InvestigationContext
from app.services.ai_assistant.models import ResponseType
from app.services.ai_assistant.reasoning import InvestigationReasoningService
from app.services.ai_assistant.reporting_models import ExecutiveSummary, AnalystReport
from app.services.ai_assistant.report_generator import ReportGeneratorService
from app.integrations.openrouter.provider import OpenRouterProvider

logger = logging.getLogger("app.services.ai_assistant.service")


class AIAssistantService(BaseAIAssistantService):
    """
    Service layer orchestrating the AI Investigation Assistant.
    Coordinates prompt construction, deterministic reasoning,
    and OpenRouter LLM completions with fallback resilience.
    """

    def __init__(self) -> None:
        self.context_builder = InvestigationContextBuilder()
        self.reasoning_service = InvestigationReasoningService()
        self.report_generator = ReportGeneratorService()
        self.openrouter_provider = OpenRouterProvider()
        logger.info("AIAssistantService initialized successfully.")

    async def generate_summary(self, context: InvestigationContext) -> AssistantResponse:
        """
        Assembles prompt context and queries the reasoning service to generate a technical investigation report summary.
        """
        logger.info(f"[generate_summary] Invoked for indicator '{context.indicator}'")

        system_prompt = self.context_builder.generate_system_prompt(context)
        logger.debug(f"[generate_summary] Built prompt length: {len(system_prompt)} chars")

        # Reuse ask_question with a predefined risk query
        return await self.ask_question(query="Why is this URL risky?", context=context)

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

        return await self.ask_question(query=message, context=context)

    async def ask_question(self, query: str, context: InvestigationContext) -> AssistantResponse:
        """
        Queries OpenRouter for conversational Q&A. Fallbacks to the local reasoning engine
        if the API key is not configured or the OpenRouter API fails.
        """
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY is not set. Falling back to local reasoning engine.")
            return self.reasoning_service.answer_question(query, context)

        try:
            return await self.openrouter_provider.ask_question(query, context)
        except Exception as e:
            logger.error(f"OpenRouter ask_question call failed: {e}. Falling back to local reasoning engine.")
            return self.reasoning_service.answer_question(query, context)

    async def get_analyst_report(self, context: InvestigationContext) -> AnalystReport:
        """
        Queries OpenRouter to generate a structured AnalystReport. Fallbacks to the local
        report generator if OpenRouter fails or the API key is missing.
        """
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY is not set. Falling back to local report generator.")
            return self.report_generator.generate_analyst_report(context)

        try:
            return await self.openrouter_provider.get_analyst_report(context)
        except Exception as e:
            logger.error(f"OpenRouter get_analyst_report call failed: {e}. Falling back to local report generator.")
            return self.report_generator.generate_analyst_report(context)

    async def get_executive_summary(self, context: InvestigationContext) -> ExecutiveSummary:
        """
        Queries OpenRouter to generate an ExecutiveSummary. Fallbacks to the local
        report generator if OpenRouter fails or the API key is missing.
        """
        if not settings.OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY is not set. Falling back to local report generator.")
            return self.report_generator.generate_executive_summary(context)

        try:
            return await self.openrouter_provider.get_executive_summary(context)
        except Exception as e:
            logger.error(f"OpenRouter get_executive_summary call failed: {e}. Falling back to local report generator.")
            return self.report_generator.generate_executive_summary(context)

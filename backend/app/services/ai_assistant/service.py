import logging
from datetime import datetime, timezone
from typing import List

from app.services.ai_assistant.base import BaseAIAssistantService
from app.services.ai_assistant.context_builder import InvestigationContextBuilder
from app.services.ai_assistant.schemas import AssistantResponse, AssistantMessage, InvestigationContext
from app.services.ai_assistant.models import ResponseType

logger = logging.getLogger("app.services.ai_assistant.service")


class AIAssistantService(BaseAIAssistantService):
    """
    Service layer orchestrating the AI Investigation Assistant.
    Coordinates prompt construction via the Context Builder and executes AI inference.
    """

    def __init__(self) -> None:
        self.context_builder = InvestigationContextBuilder()
        logger.info("AIAssistantService initialized successfully.")

    async def generate_summary(self, context: InvestigationContext) -> AssistantResponse:
        """
        Assembles prompt context and queries the AI model to generate a technical investigation report.
        Placeholder implementation for Stage 8.2 (LLM calls to be completed in Stage 8.3).
        """
        logger.info(f"[generate_summary] Invoked for indicator '{context.indicator}'")

        # Construct prompt
        system_prompt = self.context_builder.generate_system_prompt(context)
        logger.debug(f"[generate_summary] Built prompt length: {len(system_prompt)} chars")

        # Stub response content
        stub_message = (
            f"**[AI Investigation Assistant Stub]**\n\n"
            f"Successfully built context for indicator `{context.indicator}`. "
            f"Prompt assembly size: {len(system_prompt)} characters.\n\n"
            f"*Disclaimer: Downstream LLM inference execution will be integrated in Stage 8.3.*"
        )

        return AssistantResponse(
            message=AssistantMessage(
                role="assistant",
                content=stub_message,
                timestamp=datetime.now(timezone.utc),
            ),
            suggested_actions=[],
            response_type=ResponseType.SUMMARY,
        )

    async def chat(
        self,
        context: InvestigationContext,
        history: List[AssistantMessage],
        message: str,
    ) -> AssistantResponse:
        """
        Continues a conversational dialog with the analyst, referencing historical logs
        and indicator context details.
        Placeholder implementation for Stage 8.2 (LLM calls to be completed in Stage 8.3).
        """
        logger.info(f"[chat] Invoked for indicator '{context.indicator}' with {len(history)} historical message(s)")

        # Stub response content
        stub_message = (
            f"**[AI Investigation Assistant Chat Stub]**\n\n"
            f"Received user message: *\"{message}\"*\n"
            f"Target context: `{context.indicator}`.\n\n"
            f"*Disclaimer: LLM inference integration will follow in Stage 8.3.*"
        )

        return AssistantResponse(
            message=AssistantMessage(
                role="assistant",
                content=stub_message,
                timestamp=datetime.now(timezone.utc),
            ),
            suggested_actions=[],
            response_type=ResponseType.CHAT,
        )

from abc import ABC, abstractmethod
from typing import List

from app.services.ai_assistant.schemas import AssistantResponse, AssistantMessage, InvestigationContext


class BaseAIAssistantService(ABC):
    """
    Abstract interface for the AI Investigation Assistant service.
    Defines the contract for prompt building and text/conversational inference.
    """

    @abstractmethod
    async def generate_summary(self, context: InvestigationContext) -> AssistantResponse:
        """
        Builds investigation context, queries the LLM for a high-level technical summary,
        verdicts breakdown, and returns the response with suggested analyst actions.
        """
        pass

    @abstractmethod
    async def chat(
        self,
        context: InvestigationContext,
        history: List[AssistantMessage],
        message: str,
    ) -> AssistantResponse:
        """
        Continues a conversational dialog with an analyst, referencing investigation history
        and target context to answer queries and recommend mitigations.
        """
        pass

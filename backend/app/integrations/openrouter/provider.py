import json
import logging
import re
from datetime import datetime, timezone
from typing import Dict, Any

from app.core.config import settings
from app.services.ai_assistant.schemas import AssistantResponse, AssistantMessage, SuggestedAction, InvestigationContext
from app.services.ai_assistant.reporting_models import ExecutiveSummary, AnalystReport
from app.integrations.openrouter.client import OpenRouterClient
from app.services.ai_assistant.context_builder import InvestigationContextBuilder

logger = logging.getLogger("app.integrations.openrouter.provider")


class OpenRouterProvider:
    """
    OpenRouter Provider that builds prompts using context information,
    requests completion payloads via OpenRouterClient, cleans responses,
    and validates them into Pydantic models.
    """

    def __init__(self) -> None:
        self.client = OpenRouterClient()
        self.context_builder = InvestigationContextBuilder()

    async def ask_question(
        self,
        query: str,
        context: InvestigationContext,
    ) -> AssistantResponse:
        """
        Sends the question query alongside the system prompt context to OpenRouter
        and parses the response back into an AssistantResponse model.
        """
        system_prompt = self.context_builder.generate_system_prompt(context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                f"Please answer the following security analyst question based on the investigation context.\n"
                f"Question: '{query}'\n\n"
                f"You must return your response in valid JSON conforming to the following schema:\n"
                f"{{\n"
                f"  \"message\": {{\n"
                f"    \"role\": \"assistant\",\n"
                f"    \"content\": \"Your detailed answer here (can use markdown). Always include a confidence estimation (e.g. 'Confidence Estimation: High') in the first line.\",\n"
                f"    \"timestamp\": \"{datetime.now(timezone.utc).isoformat()}\"\n"
                f"  }},\n"
                f"  \"suggested_actions\": [\n"
                f"    {{\n"
                f"      \"label\": \"Action Button Label\",\n"
                f"      \"action_type\": \"escalate | block | triage | report_registrar | inspect_forms | inspect_tls | block_infra | pivot_campaign\",\n"
                f"      \"payload\": {{}}\n"
                f"    }}\n"
                f"  ],\n"
                f"  \"response_type\": \"chat\"\n"
                f"}}\n"
            )}
        ]

        model = settings.OPENROUTER_DEFAULT_MODEL
        logger.info(f"Invoking OpenRouter model '{model}' for ask_question")
        
        response_text = await self.client.request_completion(
            messages=messages,
            model=model,
            json_mode=True
        )

        try:
            data = self._clean_and_parse_json(response_text)
            return AssistantResponse.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to parse OpenRouter response: {e}. Raw response: {response_text}")
            raise ValueError(f"LLM did not return a valid AssistantResponse JSON: {e}")

    async def get_analyst_report(self, context: InvestigationContext) -> AnalystReport:
        """
        Requests OpenRouter to generate a detailed AnalystReport JSON payload.
        """
        system_prompt = self.context_builder.generate_system_prompt(context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                "Please generate a detailed, structured technical AnalystReport based on the context.\n"
                "You must return your response in valid JSON conforming to the AnalystReport Pydantic schema structure:\n"
                "{\n"
                "  \"indicator\": \"The indicator string\",\n"
                "  \"risk_score\": 0.0,\n"
                "  \"severity\": \"Risk severity string\",\n"
                "  \"risk_assessment_explanation\": \"Main risk explanation\",\n"
                "  \"evidence_summary\": {\n"
                "    \"indicator\": \"...\",\n"
                "    \"overall_confidence\": \"Consensus confidence\",\n"
                "    \"observations_count\": 0,\n"
                "    \"domain_age_days\": null,\n"
                "    \"registrar\": null,\n"
                "    \"ssl_valid\": null,\n"
                "    \"tls_issuer\": null,\n"
                "    \"has_login_form\": null,\n"
                "    \"forms_count\": null,\n"
                "    \"virustotal_verdict\": null,\n"
                "    \"overall_verdict\": null,\n"
                "    \"top_findings\": []\n"
                "  },\n"
                "  \"campaign_id\": null,\n"
                "  \"campaign_members\": [],\n"
                "  \"shared_infrastructure\": [],\n"
                "  \"recommendations\": {\n"
                "    \"immediate_actions\": [],\n"
                "    \"mitigation_steps\": []\n"
                "  },\n"
                "  \"timeline_events\": [],\n"
                "  \"conclusion\": \"Analyst final conclusion summary statement\"\n"
                "}"
            )}
        ]

        model = settings.OPENROUTER_DEFAULT_MODEL
        logger.info(f"Invoking OpenRouter model '{model}' for get_analyst_report")
        
        response_text = await self.client.request_completion(
            messages=messages,
            model=model,
            json_mode=True
        )

        try:
            data = self._clean_and_parse_json(response_text)
            if "created_at" not in data:
                data["created_at"] = datetime.now(timezone.utc).isoformat()
            return AnalystReport.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to parse OpenRouter response: {e}. Raw response: {response_text}")
            raise ValueError(f"LLM did not return a valid AnalystReport JSON: {e}")

    async def get_executive_summary(self, context: InvestigationContext) -> ExecutiveSummary:
        """
        Requests OpenRouter to generate a high-level corporate ExecutiveSummary JSON payload.
        """
        system_prompt = self.context_builder.generate_system_prompt(context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (
                "Please generate a high-level, business-oriented ExecutiveSummary based on the context.\n"
                "You must return your response in valid JSON conforming to the ExecutiveSummary Pydantic schema structure:\n"
                "{\n"
                "  \"indicator\": \"The indicator string\",\n"
                "  \"overall_risk_rating\": \"Risk severity tier\",\n"
                "  \"overall_score\": 0.0,\n"
                "  \"campaign_associated\": false,\n"
                "  \"campaign_name\": null,\n"
                "  \"key_findings\": [],\n"
                "  \"business_impact\": \"Estimated business/brand exposure impact statement\",\n"
                "  \"recommended_action_summary\": \"Remediation requirements action plan\"\n"
                "}"
            )}
        ]

        model = settings.OPENROUTER_DEFAULT_MODEL
        logger.info(f"Invoking OpenRouter model '{model}' for get_executive_summary")
        
        response_text = await self.client.request_completion(
            messages=messages,
            model=model,
            json_mode=True
        )

        try:
            data = self._clean_and_parse_json(response_text)
            if "created_at" not in data:
                data["created_at"] = datetime.now(timezone.utc).isoformat()
            return ExecutiveSummary.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to parse OpenRouter response: {e}. Raw response: {response_text}")
            raise ValueError(f"LLM did not return a valid ExecutiveSummary JSON: {e}")

    def _clean_and_parse_json(self, content: str) -> Dict[str, Any]:
        """
        Strips markdown tags from output and parses the JSON.
        """
        content = content.strip()
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        match = re.search(r"(\{.*\})", content, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        return json.loads(content)

import logging
import asyncio
from typing import Dict, Any, List
import httpx

from app.core.config import settings
from app.integrations.openrouter.config import OPENROUTER_API_URL, get_openrouter_headers

logger = logging.getLogger("app.integrations.openrouter.client")


class OpenRouterClient:
    """
    HTTP client communicating with OpenRouter completions endpoints.
    Handles rate-limiting (429), server timeouts, and model fallback logic.
    """

    async def request_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        json_mode: bool = False,
    ) -> str:
        """
        Sends chat completion payload to OpenRouter, with automatic fallback on failure.
        """
        try:
            return await self._execute_with_retry(messages, model, temperature, max_tokens, json_mode)
        except Exception as e:
            fallback = settings.OPENROUTER_FALLBACK_MODEL
            if fallback and fallback != model:
                logger.warning(
                    f"OpenRouter primary model '{model}' call failed: {e}. "
                    f"Retrying with fallback model '{fallback}'..."
                )
                return await self._execute_with_retry(messages, fallback, temperature, max_tokens, json_mode)
            else:
                logger.error(f"OpenRouter primary call failed and fallback model is identical or missing: {e}")
                raise e

    async def _execute_with_retry(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool,
    ) -> str:
        headers = get_openrouter_headers()
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        retries = 3
        backoff = 1.0

        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        OPENROUTER_API_URL,
                        json=payload,
                        headers=headers,
                    )

                    if response.status_code == 200:
                        res_data = response.json()
                        choices = res_data.get("choices", [])
                        if not choices:
                            raise RuntimeError("OpenRouter response did not contain choices.")
                        return choices[0].get("message", {}).get("content", "")

                    if response.status_code == 429 or response.status_code >= 500:
                        logger.warning(
                            f"OpenRouter returned status {response.status_code} "
                            f"(attempt {attempt + 1}/{retries}): {response.text}"
                        )
                        if attempt < retries - 1:
                            await asyncio.sleep(backoff)
                            backoff *= 2.0
                            continue

                    response.raise_for_status()

            except (httpx.HTTPError, httpx.TimeoutException) as e:
                logger.warning(f"OpenRouter request error on attempt {attempt + 1}/{retries}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue
                raise e

        raise RuntimeError(f"OpenRouter call failed after {retries} retry attempts.")

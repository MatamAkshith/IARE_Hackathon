from app.core.config import settings

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def get_openrouter_headers() -> dict:
    """
    Builds the standard request headers for communicating with the OpenRouter API.
    """
    headers = {
        "Content-Type": "application/json",
    }
    if settings.OPENROUTER_API_KEY:
        headers["Authorization"] = f"Bearer {settings.OPENROUTER_API_KEY}"
    
    # OpenRouter recommends passing these headers for rankings
    headers["HTTP-Referer"] = "https://github.com/MatamAkshith/IARE_Hackathon"
    headers["X-Title"] = "ThreatLens"
    return headers

from enum import Enum


class ResponseType(str, Enum):
    """
    Type of AI response format required by the client or context.
    """
    SUMMARY = "summary"
    RECOMMENDATION = "recommendation"
    CHAT = "chat"


class ConversationStatus(str, Enum):
    """
    Current lifecycle status of an AI-assisted analysis conversation.
    """
    ACTIVE = "active"
    CLOSED = "closed"

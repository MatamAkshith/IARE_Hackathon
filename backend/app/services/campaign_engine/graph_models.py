"""
Graph & Timeline Serialization Models — Stage 7.4

Defines Pydantic structures representing the relationship graph and
chronological timeline of campaign investigation datasets.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Supported graph node classifications."""
    INDICATOR = "indicator"
    IP = "ip"
    CERTIFICATE = "certificate"
    WHOIS = "whois"
    HTML = "html"
    ASN = "asn"
    REGISTRAR = "registrar"


class GraphNode(BaseModel):
    """Represents a vertex in the campaign relationship graph."""
    id: str = Field(description="Unique identifier for the node (e.g., domain URL or IP value).")
    label: str = Field(description="Human-readable label for node display.")
    type: NodeType = Field(description="Classification categorization of the node.")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-value pairs.")


class GraphEdge(BaseModel):
    """Represents a connection between two nodes in the graph."""
    source: str = Field(description="Source vertex node ID.")
    target: str = Field(description="Target vertex node ID.")
    relationship: str = Field(description="Semantics of connection (e.g., 'resolves_to', 'registered_with').")
    weight: float = Field(default=1.0, description="Strength weight score of relation [0.0, 1.0].")


class CampaignGraph(BaseModel):
    """Represents the complete interconnected infrastructure footprint graph."""
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    """Represents a point-in-time milestone event in the campaign lifecycle."""
    timestamp: datetime = Field(description="Event timestamp.")
    event_type: str = Field(description="Classification category (e.g., 'creation', 'detection', 'merge').")
    description: str = Field(description="Human-readable description of what transpired.")
    indicator: str = Field(description="Associated indicator value.")


class CampaignTimeline(BaseModel):
    """Chronologically sorted series of events detailing campaign evolution."""
    events: List[TimelineEvent] = Field(default_factory=list)

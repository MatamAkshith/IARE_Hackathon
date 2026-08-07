"""
Relationship Graph Builder — Stage 7.4

Iterates through campaign members and their resolved observations to build a Pydantic
represented CampaignGraph mapping relationships between indicators and shared infrastructure nodes.
"""

from typing import Dict, Any, List, Set
import logging

from app.services.campaign_engine.models import Campaign
from app.services.campaign_engine.graph_models import (
    CampaignGraph,
    GraphNode,
    GraphEdge,
    NodeType,
)

logger = logging.getLogger("app.services.campaign_engine.graph_builder")


class CampaignGraphBuilder:
    """
    Constructs CampaignGraph representations of indicator footprints,
    mapping nodes for IP addresses, TLS certs, WHOIS registries, and HTML layouts.
    """

    def build_graph(self, campaign: Campaign) -> CampaignGraph:
        """
        Analyzes the campaign members and builds nodes/edges.
        """
        logger.info(f"[build_graph] Creating relationship graph for campaign '{campaign.campaign_id}'")

        nodes_dict: Dict[str, GraphNode] = {}
        edges: List[GraphEdge] = []
        seen_edges: Set[tuple] = set()

        def add_node(node_id: str, label: str, type: NodeType, properties: Dict[str, Any] = None) -> None:
            if not node_id:
                return
            clean_id = node_id.strip()
            if clean_id not in nodes_dict:
                nodes_dict[clean_id] = GraphNode(
                    id=clean_id,
                    label=label.strip(),
                    type=type,
                    properties=properties or {}
                )

        def add_edge(source: str, target: str, relationship: str, weight: float = 1.0) -> None:
            if not source or not target:
                return
            src_clean = source.strip()
            tgt_clean = target.strip()
            edge_key = (src_clean, tgt_clean, relationship)
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                edges.append(GraphEdge(
                    source=src_clean,
                    target=tgt_clean,
                    relationship=relationship,
                    weight=weight
                ))

        # Add root campaign metadata as properties to indicator nodes if wanted,
        # but let's keep nodes focused.
        for member in campaign.members:
            indicator_id = member.indicator
            obs = member.resolved_observations or {}
            
            # 1. Add Indicator Node
            add_node(
                node_id=indicator_id,
                label=indicator_id,
                type=NodeType.INDICATOR,
                properties={
                    "indicator_type": member.indicator_type,
                    "added_at": member.added_at.isoformat() if member.added_at else "",
                    "added_reason": member.added_reason
                }
            )

            # 2. Extract and link IP Node
            ip = obs.get("ip_address") or obs.get("ip")
            if ip:
                ip_str = str(ip)
                add_node(node_id=ip_str, label=f"IP: {ip_str}", type=NodeType.IP)
                add_edge(source=indicator_id, target=ip_str, relationship="resolves_to", weight=1.0)
                
                # Link IP to ASN
                asn = obs.get("asn") or obs.get("autonomous_system_number")
                if asn:
                    asn_str = str(asn)
                    add_node(node_id=asn_str, label=f"ASN: {asn_str}", type=NodeType.ASN)
                    add_edge(source=ip_str, target=asn_str, relationship="hosted_on", weight=0.8)

            # 3. Extract and link Certificate Node
            cert_serial = obs.get("tls_serial") or obs.get("cert_serial")
            if cert_serial:
                cert_str = str(cert_serial)
                cert_node_id = f"CERT-{cert_str}"
                properties = {
                    "issuer": obs.get("tls_issuer") or obs.get("cert_issuer") or "",
                    "subject": obs.get("tls_subject") or obs.get("cert_subject") or ""
                }
                add_node(
                    node_id=cert_node_id,
                    label=f"Cert: {cert_str[:12]}...",
                    type=NodeType.CERTIFICATE,
                    properties=properties
                )
                add_edge(source=indicator_id, target=cert_node_id, relationship="presents_cert", weight=1.0)

            # 4. Extract and link WHOIS nodes (Registrar & Registrant Org)
            registrar = obs.get("registrar")
            if registrar:
                reg_str = str(registrar)
                add_node(node_id=reg_str, label=f"Registrar: {reg_str}", type=NodeType.REGISTRAR)
                add_edge(source=indicator_id, target=reg_str, relationship="registered_with", weight=0.6)

            org = obs.get("registrant_org") or obs.get("org")
            ignored_orgs = {"redacted", "privacy", "not available", "redacted for privacy", "privacy service"}
            is_valid_org = lambda o: o and not any(ign in str(o).lower() for ign in ignored_orgs)
            if is_valid_org(org):
                org_str = str(org)
                add_node(node_id=org_str, label=f"Owner Org: {org_str}", type=NodeType.WHOIS)
                add_edge(source=indicator_id, target=org_str, relationship="registered_by", weight=0.9)

            # 5. Extract HTML traits
            title = obs.get("page_title") or obs.get("title")
            generic_titles = {"welcome", "index", "home", "login", "signin", "error", "404"}
            is_valid_title = lambda t: t and str(t).lower().strip() not in generic_titles and len(str(t)) > 3
            if is_valid_title(title):
                title_str = str(title)
                add_node(node_id=title_str, label=f"Title: {title_str}", type=NodeType.HTML)
                add_edge(source=indicator_id, target=title_str, relationship="renders_title", weight=0.7)

            structure_hash = obs.get("html_structure_hash") or obs.get("structural_hash")
            if structure_hash:
                hash_str = str(structure_hash)
                add_node(node_id=hash_str, label=f"DOM Layout: {hash_str[:10]}", type=NodeType.HTML)
                add_edge(source=indicator_id, target=hash_str, relationship="shares_layout_hash", weight=0.8)

        # Build list of nodes
        nodes = list(nodes_dict.values())
        logger.info(
            f"[build_graph] Graph constructed with {len(nodes)} node(s) and {len(edges)} edge(s) "
            f"for campaign '{campaign.campaign_id}'"
        )

        return CampaignGraph(nodes=nodes, edges=edges)

import logging
from typing import Any, Dict, List, Optional

from app.services.unified_evidence.service import BaseMergeStrategy

logger = logging.getLogger("app.services.unified_evidence.strategy")


class DefaultMergeStrategy(BaseMergeStrategy):
    def merge(
        self,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
        conflict_resolutions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Merges internal evidence and external threat intel data.

        Conflict Resolution Rule: When a key exists in both datasets with differing values,
        the external_data value takes priority and the override is recorded for traceability.

        Deduplication: Identical overlapping key-value pairs are stored only once.
        """
        if conflict_resolutions is None:
            conflict_resolutions = []

        resolved: Dict[str, Any] = {}

        # Seed with all internal evidence
        for k, v in internal_data.items():
            resolved[k] = v
            logger.debug(f"Collected internal key '{k}'.")

        # Overlay external evidence, enforcing external-wins conflict rule
        for k, v in external_data.items():
            if k in resolved:
                if resolved[k] != v:
                    old_val = resolved[k]
                    resolved[k] = v
                    note = (
                        f"Conflict resolved for key '{k}': "
                        f"prioritized external value '{v}' over internal value '{old_val}'"
                    )
                    conflict_resolutions.append(note)
                    logger.debug(note)
                # else: identical value — already deduplicated, no action needed
            else:
                resolved[k] = v
                logger.debug(f"Ingested external key '{k}'.")

        logger.info(
            f"Merge complete: {len(resolved)} keys resolved, "
            f"{len(conflict_resolutions)} conflict(s) encountered."
        )
        return resolved

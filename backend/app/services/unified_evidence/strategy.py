from typing import Dict, Any, List, Optional
from app.services.unified_evidence.service import BaseMergeStrategy

class DefaultMergeStrategy(BaseMergeStrategy):
    def merge(
        self,
        internal_data: Dict[str, Any],
        external_data: Dict[str, Any],
        conflict_resolutions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Merges internal evidence and external threat intel data.
        
        Conflict Resolution Rule: If a key exists in both datasets with different values,
        prioritize the external_data value and record the resolution.
        
        Deduplication: Identical overlapping key-value pairs are stored once.
        """
        resolved = {}
        if conflict_resolutions is None:
            conflict_resolutions = []
            
        # Add all internal data
        for k, v in internal_data.items():
            resolved[k] = v
            
        # Process external data with priority and logging overrides
        for k, v in external_data.items():
            if k in resolved:
                if resolved[k] != v:
                    old_val = resolved[k]
                    resolved[k] = v
                    note = f"Conflict resolved for key '{k}': prioritized external value '{v}' over internal value '{old_val}'"
                    conflict_resolutions.append(note)
                else:
                    # Identical key/value exists, already deduplicated
                    pass
            else:
                resolved[k] = v
                
        return resolved

import logging
import urllib.parse
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("app.services.unified_evidence.normalizer")

# Keys that represent boolean flag fields
_BOOL_KEYS = frozenset({"has_login_form", "ssl_valid", "is_valid", "in_database", "valid"})

# Keys that represent integer count / duration fields
_INT_KEYS = frozenset({"domain_age_days", "age_days", "count", "severity_score",
                        "malicious_count", "suspicious_count"})

# Keys that represent URL / indicator string fields
_URL_KEYS = frozenset({"url", "indicator", "final_url", "redirect_url"})


class EvidenceNormalizer:
    """
    Standardizes raw merged evidence key-value pairs into predictable Python types.

    Rules applied (in priority order per key):
    1. Empty strings → None
    2. Boolean flag keys → True/False/None
    3. Integer count/duration keys → int/None (digits extracted from strings like '30 days')
    4. URL/indicator keys → lowercased scheme+netloc
    5. All other keys → passed through unchanged
    """

    def normalize(
        self, resolved_observations: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Normalizes and standardizes key-value observations.

        Returns:
            A tuple of (normalized_dict, normalization_log_messages).
        """
        normalized: Dict[str, Any] = {}
        logs: List[str] = []

        for k, v in resolved_observations.items():
            try:
                normalized[k], entry_logs = self._normalize_value(k, v)
                logs.extend(entry_logs)
            except Exception as exc:
                # Defensive fallback: preserve original value and log the error
                logger.warning(
                    f"Normalization failed for key '{k}' with value '{v!r}': {exc}. "
                    f"Preserving original value."
                )
                normalized[k] = v

        logger.info(f"Normalization complete: {len(logs)} transform(s) applied to {len(normalized)} key(s).")
        return normalized, logs

    def _normalize_value(self, k: str, v: Any) -> Tuple[Any, List[str]]:
        """Dispatches normalization for a single key-value pair."""
        logs: List[str] = []

        # Rule 1: Empty strings → None (applies to all keys)
        if isinstance(v, str) and not v.strip():
            logs.append(f"Normalized key '{k}': empty string replaced with None")
            return None, logs

        # Rule 2: Boolean flag keys
        if k in _BOOL_KEYS:
            result, entry_logs = self._cast_bool(k, v)
            logs.extend(entry_logs)
            return result, logs

        # Rule 3: Integer count / duration keys
        if k in _INT_KEYS:
            result, entry_logs = self._cast_int(k, v)
            logs.extend(entry_logs)
            return result, logs

        # Rule 4: URL / indicator keys
        if k in _URL_KEYS:
            result, entry_logs = self._standardize_url(k, v)
            logs.extend(entry_logs)
            return result, logs

        # Rule 5: Default — pass through unchanged
        return v, logs

    # ------------------------------------------------------------------ #
    # Private casting helpers                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _cast_bool(k: str, v: Any) -> Tuple[Any, List[str]]:
        logs: List[str] = []
        if isinstance(v, bool):
            return v, logs
        if isinstance(v, int):
            cast = bool(v)
            logs.append(f"Normalized key '{k}' from integer '{v}' to {cast}")
            return cast, logs
        if isinstance(v, str):
            lower_v = v.lower().strip()
            if lower_v in ("true", "yes", "1"):
                logs.append(f"Normalized key '{k}' from string '{v}' to True")
                return True, logs
            if lower_v in ("false", "no", "0"):
                logs.append(f"Normalized key '{k}' from string '{v}' to False")
                return False, logs
            logs.append(f"Normalized key '{k}' from unknown string '{v}' to None")
            return None, logs
        logs.append(f"Normalized key '{k}' of unsupported type to None")
        return None, logs

    @staticmethod
    def _cast_int(k: str, v: Any) -> Tuple[Any, List[str]]:
        logs: List[str] = []
        if isinstance(v, int):
            return v, logs
        if isinstance(v, float):
            cast = int(v)
            logs.append(f"Normalized key '{k}' from float '{v}' to integer '{cast}'")
            return cast, logs
        if isinstance(v, str):
            # Extract leading/trailing digits, supporting formats like '30 days' or '-5'
            cleaned = "".join(c for c in v if c.isdigit() or c == "-")
            if cleaned:
                cast = int(cleaned)
                logs.append(f"Normalized key '{k}' from string '{v}' to integer '{cast}'")
                return cast, logs
            logs.append(f"Normalized key '{k}' from string '{v}' to None (no digits found)")
            return None, logs
        logs.append(f"Normalized key '{k}' of unsupported type to None")
        return None, logs

    @staticmethod
    def _standardize_url(k: str, v: Any) -> Tuple[Any, List[str]]:
        logs: List[str] = []
        if not isinstance(v, str) or not v.strip():
            return v, logs
        stripped = v.strip()
        try:
            parsed = urllib.parse.urlparse(stripped)
            if parsed.scheme:
                standardized = parsed._replace(
                    scheme=parsed.scheme.lower(),
                    netloc=parsed.netloc.lower()
                ).geturl()
                if standardized != stripped:
                    logs.append(
                        f"Standardized URL scheme/netloc for key '{k}' "
                        f"from '{v}' to '{standardized}'"
                    )
                return standardized, logs
        except Exception:
            pass
        return stripped, logs

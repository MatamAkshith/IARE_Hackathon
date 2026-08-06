import urllib.parse
from typing import Dict, Any, List, Tuple

class EvidenceNormalizer:
    def normalize(self, resolved_observations: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Normalizes, casts, and standardizes key-value observations.
        
        Returns a standardized dictionary of observations and a list of logs explaining standardizations.
        """
        normalized = {}
        logs = []

        for k, v in resolved_observations.items():
            # Standardize empty strings to None
            if isinstance(v, str) and not v.strip():
                normalized[k] = None
                logs.append(f"Normalized key '{k}': empty string replaced with None")
                continue

            # Standardize Boolean representations
            if k in ["has_login_form", "ssl_valid", "is_valid", "in_database", "valid"]:
                if isinstance(v, bool):
                    normalized[k] = v
                elif isinstance(v, str):
                    lower_v = v.lower().strip()
                    if lower_v in ["true", "yes", "1"]:
                        normalized[k] = True
                        logs.append(f"Normalized key '{k}' from string '{v}' to True")
                    elif lower_v in ["false", "no", "0"]:
                        normalized[k] = False
                        logs.append(f"Normalized key '{k}' from string '{v}' to False")
                    else:
                        normalized[k] = None
                        logs.append(f"Normalized key '{k}' from unknown string '{v}' to None")
                elif isinstance(v, int):
                    normalized[k] = bool(v)
                    logs.append(f"Normalized key '{k}' from integer '{v}' to {bool(v)}")
                else:
                    normalized[k] = None
                    logs.append(f"Normalized key '{k}' of unsupported type to None")
                continue

            # Standardize Integer representations
            if k in ["domain_age_days", "age_days", "count", "severity_score", "malicious_count", "suspicious_count"]:
                try:
                    if isinstance(v, int):
                        normalized[k] = v
                    elif isinstance(v, float):
                        normalized[k] = int(v)
                        logs.append(f"Normalized key '{k}' from float '{v}' to integer '{int(v)}'")
                    elif isinstance(v, str):
                        # Extract digits if string has '1500 days' or similar
                        cleaned_str = "".join([char for char in v if char.isdigit() or char == "-"])
                        if cleaned_str:
                            normalized[k] = int(cleaned_str)
                            logs.append(f"Normalized key '{k}' from string '{v}' to integer '{int(cleaned_str)}'")
                        else:
                            normalized[k] = None
                            logs.append(f"Normalized key '{k}' from string '{v}' to None")
                    else:
                        normalized[k] = None
                        logs.append(f"Normalized key '{k}' of unsupported type to None")
                except ValueError:
                    normalized[k] = None
                    logs.append(f"Failed to normalize key '{k}' with value '{v}' to integer, set to None")
                continue

            # Standardize URL/domain indicators
            if k in ["url", "indicator", "final_url", "redirect_url"]:
                if isinstance(v, str) and v.strip():
                    stripped_v = v.strip()
                    # Basic lowercase for scheme/host
                    try:
                        parsed = urllib.parse.urlparse(stripped_v)
                        if parsed.scheme:
                            standardized_url = parsed._replace(
                                scheme=parsed.scheme.lower(),
                                netloc=parsed.netloc.lower()
                            ).geturl()
                            normalized[k] = standardized_url
                            if standardized_url != stripped_v:
                                logs.append(f"Standardized URL scheme/netloc for key '{k}' from '{v}' to '{standardized_url}'")
                            else:
                                normalized[k] = stripped_v
                        else:
                            normalized[k] = stripped_v
                    except Exception:
                        normalized[k] = stripped_v
                else:
                    normalized[k] = v
                continue

            # Default fallback for other values
            normalized[k] = v

        return normalized, logs

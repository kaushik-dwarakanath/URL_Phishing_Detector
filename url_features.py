import re
from typing import Dict


FEATURE_COLUMNS = [
    "url_length",
    "n_dots",
    "n_hypens",
    "n_underline",
    "n_slash",
    "n_questionmark",
    "n_equal",
    "n_at",
    "n_and",
    "n_exclamation",
    "n_space",
    "n_tilde",
    "n_comma",
    "n_plus",
    "n_asterisk",
    "n_hastag",
    "n_dollar",
    "n_percent",
    "n_redirection",
]


CHAR_MAP = {
    "n_dots": ".",
    "n_hypens": "-",
    "n_underline": "_",
    "n_slash": "/",
    "n_questionmark": "?",
    "n_equal": "=",
    "n_at": "@",
    "n_and": "&",
    "n_exclamation": "!",
    "n_space": " ",
    "n_tilde": "~",
    "n_comma": ",",
    "n_plus": "+",
    "n_asterisk": "*",
    "n_hastag": "#",
    "n_dollar": "$",
    "n_percent": "%",
}


def extract_features(url: str) -> Dict[str, int]:
    """
    Extract hand-crafted features from a URL that match the columns of
    web-page-phishing.csv (except for the target column 'phishing').
    """
    url = url or ""
    features: Dict[str, int] = {}

    # Basic length feature
    features["url_length"] = len(url)

    # Character occurrence counts
    for feature_name, ch in CHAR_MAP.items():
        features[feature_name] = url.count(ch)

    # Redirection count: number of occurrences of '//' beyond the initial scheme
    # e.g. http://example.com//path → 2 redirections (one is scheme, others are suspicious)
    # We emulate this with a simple heuristic.
    redirection_pattern = re.compile(r"//")
    all_double_slashes = list(redirection_pattern.finditer(url))
    # Discount the first '//' that typically appears after the scheme
    n_redirections = max(0, len(all_double_slashes) - 1)
    features["n_redirection"] = n_redirections

    # Ensure all expected columns exist
    for col in FEATURE_COLUMNS:
        if col not in features:
            features[col] = 0

    return features



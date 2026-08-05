from difflib import SequenceMatcher
from typing import Any, Optional

_MATCH_THRESHOLD = 0.6
_WORD_MATCH_THRESHOLD = 0.7


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _token_coverage(a_tokens: list[str], b_tokens: list[str]) -> float:
    """Share of a_tokens that have a close match (by stem-tolerant ratio) in b_tokens."""
    if not a_tokens or not b_tokens:
        return 0.0
    matched = sum(
        1
        for token in a_tokens
        if max((SequenceMatcher(None, token, other).ratio() for other in b_tokens), default=0)
        >= _WORD_MATCH_THRESHOLD
    )
    return matched / len(a_tokens)


def _similarity(a: str, b: str) -> float:
    """Combines whole-string similarity with word-level coverage so that
    differently-ordered/inflected Russian phrases (AI wording vs price-list
    wording) still match, e.g. "газобетонные стены" vs "кладка стен из газобетона".
    """
    norm_a, norm_b = _normalize(a), _normalize(b)
    char_ratio = SequenceMatcher(None, norm_a, norm_b).ratio()

    a_tokens = [t for t in norm_a.split() if len(t) > 2]
    b_tokens = [t for t in norm_b.split() if len(t) > 2]
    token_score = max(_token_coverage(a_tokens, b_tokens), _token_coverage(b_tokens, a_tokens))

    return max(char_ratio, token_score)


def find_best_price_item(
    work_name: str,
    unit: str,
    price_items: list[dict[str, Any]],
) -> Optional[dict[str, Any]]:
    """Find the closest price-list entry for a work item.

    Prefers items whose unit matches; falls back to best name match regardless
    of unit if nothing matches on unit above the threshold.
    """
    best_same_unit: Optional[tuple[float, dict[str, Any]]] = None
    best_any_unit: Optional[tuple[float, dict[str, Any]]] = None

    for item in price_items:
        score = _similarity(work_name, item["name"])
        if score > (best_any_unit[0] if best_any_unit else -1):
            best_any_unit = (score, item)
        if _normalize(unit) == _normalize(item["unit"]):
            if score > (best_same_unit[0] if best_same_unit else -1):
                best_same_unit = (score, item)

    if best_same_unit and best_same_unit[0] >= _MATCH_THRESHOLD:
        return best_same_unit[1]
    if best_any_unit and best_any_unit[0] >= _MATCH_THRESHOLD:
        return best_any_unit[1]
    return None


def find_top_candidates(
    work_name: str,
    price_items: list[dict[str, Any]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Best-effort suggestions for a work item that didn't clear the match
    threshold — lets a human estimator pick manually instead of the item
    silently costing 0. Ignores the threshold entirely; ranking only."""
    scored = sorted(
        (( _similarity(work_name, item["name"]), item) for item in price_items),
        key=lambda pair: pair[0],
        reverse=True,
    )
    return [item for _, item in scored[:limit]]

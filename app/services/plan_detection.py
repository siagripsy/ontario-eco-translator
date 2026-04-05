from dataclasses import dataclass
import re
from typing import Literal


BillingPlan = Literal["ULO", "TOU", "Tiered", "Unknown"]


@dataclass(slots=True)
class BillingPlanDetectionResult:
    detected_plan: BillingPlan
    confidence: float
    evidence: list[str]


def _normalize_text(text: str) -> str:
    lowered = text.casefold()
    lowered = re.sub(r"[_/\\|]+", " ", lowered)
    lowered = re.sub(r"-+", " ", lowered)
    lowered = re.sub(r"[^\w\s]", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _has_phrase(text: str, *phrases: str) -> bool:
    return any(phrase in text for phrase in phrases)


def detect_billing_plan(text: str) -> BillingPlanDetectionResult:
    normalized = _normalize_text(text)
    if not normalized:
        return BillingPlanDetectionResult(detected_plan="Unknown", confidence=0.0, evidence=[])

    signals: dict[str, list[str]] = {"ULO": [], "TOU": [], "Tiered": []}
    scores: dict[str, float] = {"ULO": 0.0, "TOU": 0.0, "Tiered": 0.0}

    has_on_peak = _has_phrase(normalized, "on peak", "onpeak")
    has_mid_peak = _has_phrase(normalized, "mid peak", "midpeak")
    has_off_peak = _has_phrase(normalized, "off peak", "offpeak")
    has_overnight = "overnight" in normalized

    if _has_phrase(normalized, "ultra low overnight", "ulo"):
        scores["ULO"] += 0.95
        signals["ULO"].append("Found explicit ULO wording.")

    if has_overnight and has_on_peak and has_mid_peak:
        scores["ULO"] += 0.85
        signals["ULO"].append("Found Overnight with On-peak and Mid-peak.")

    if _has_phrase(normalized, "time of use", "time use"):
        scores["TOU"] += 0.9
        signals["TOU"].append("Found explicit Time-of-Use wording.")

    if has_on_peak and has_mid_peak and has_off_peak and not has_overnight:
        scores["TOU"] += 0.8
        signals["TOU"].append("Found On-peak, Mid-peak, and Off-peak without Overnight.")

    has_tier_1 = _has_phrase(normalized, "tier 1", "tier1")
    has_tier_2 = _has_phrase(normalized, "tier 2", "tier2")
    if _has_phrase(normalized, "tiered") or (has_tier_1 and has_tier_2):
        scores["Tiered"] += 0.9
        signals["Tiered"].append("Found Tiered wording or both Tier 1 and Tier 2.")

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_plan, best_score = ranked[0]
    second_score = ranked[1][1]

    if best_score < 0.6:
        evidence = [item for items in signals.values() for item in items]
        return BillingPlanDetectionResult(
            detected_plan="Unknown",
            confidence=0.2 if evidence else 0.0,
            evidence=evidence,
        )

    if second_score >= 0.6 or (best_score - second_score) < 0.2:
        evidence = [item for items in signals.values() for item in items]
        return BillingPlanDetectionResult(
            detected_plan="Unknown",
            confidence=0.35,
            evidence=evidence or ["Conflicting billing-plan signals were found."],
        )

    return BillingPlanDetectionResult(
        detected_plan=best_plan,  # type: ignore[arg-type]
        confidence=min(best_score, 1.0),
        evidence=signals[best_plan],
    )

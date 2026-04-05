from app.services.plan_detection import detect_billing_plan


def test_detects_ulo_from_overnight_on_peak_and_mid_peak() -> None:
    result = detect_billing_plan(
        "Charges include Overnight usage, On-peak usage, and Mid-peak usage on this bill."
    )

    assert result.detected_plan == "ULO"
    assert result.confidence >= 0.8
    assert result.evidence


def test_detects_tou_from_time_of_use_text() -> None:
    result = detect_billing_plan(
        "Time-of-Use - Summer charges show On-peak, Mid-peak, and Off-peak consumption."
    )

    assert result.detected_plan == "TOU"
    assert result.confidence >= 0.8
    assert result.evidence


def test_detects_tiered_from_tier_1_and_tier_2() -> None:
    result = detect_billing_plan("Electricity charges are split into Tier 1 and Tier 2 rates.")

    assert result.detected_plan == "Tiered"
    assert result.confidence >= 0.8
    assert result.evidence


def test_returns_unknown_when_plan_cues_are_weak() -> None:
    result = detect_billing_plan("This page shows account number, billing date, and total amount due.")

    assert result.detected_plan == "Unknown"

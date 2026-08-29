from __future__ import annotations


def humanize_confidence(overall_confidence: float) -> str:
    if overall_confidence >= 0.85:
        return "This is built on solid, verified numbers — you can lean on it."
    elif overall_confidence >= 0.6:
        return "Most of this is solid, but a couple of the numbers behind it are still estimates worth double-checking."
    elif overall_confidence >= 0.35:
        return "Treat this as a starting point, not a final answer — several of the numbers behind it are placeholders, not verified figures."
    else:
        return "This is mostly guesswork right now — good for exploring ideas, not for making a real planting or lending decision yet."


def humanize_crop_recommendation(rec: dict) -> str:
    crop = rec["crop"]
    score = rec["suitability_score"]
    risk = rec["risk_level"].lower()
    profit = rec.get("total_farm_net_profit_kes") or rec.get("net_profit_kes_per_acre")
    breakdown = rec.get("score_breakdown", "")

    fit_word = "a strong fit" if score >= 78 else "a reasonable fit" if score >= 58 else "a risky fit"

    sentence = (
        f"{crop} looks like {fit_word} for this season ({risk} risk), "
        f"with an estimated net profit of about KES {int(profit):,}. "
    )
    if breakdown:
        sentence += f"That's mainly because of {breakdown}."
    return sentence


def humanize_loan_decision(loan: dict) -> str:
    crop = loan["crop"]
    grade = loan["credit_grade"]
    rate = loan["interest_rate_pct"]
    default_rate = loan["expected_default_rate_pct"]
    recommendation = loan["recommendation"]

    core = (
        f"For this {crop} loan, the system estimates {grade}, "
        f"an interest rate around {rate:.1f}%, and roughly a {default_rate:.0f}% chance "
        f"of default under current assumptions. Its suggestion: {recommendation.lower()}."
    )

    provenance = loan.get("provenance", {})
    risk_weights_field = provenance.get("fields", {}).get("risk_weights", {})
    if risk_weights_field.get("provenance") == "assumed":
        core += (
            " Important: the formula behind that rate and default estimate hasn't been "
            "checked against real loan outcomes yet — use it to start the conversation, "
            "not to make the final call."
        )
    return core


def humanize_provenance_report(report: dict) -> list[str]:
    lines = [humanize_confidence(report.get("overall_confidence", 0.0))]
    weakest = report.get("weakest_link")
    if weakest:
        lines.append(f"The shakiest input right now is {weakest['value']} — {weakest.get('note', '')}".strip())
    return lines


if __name__ == "__main__":
    example_rec = {
        "crop": "Sorghum", "suitability_score": 80.3, "risk_level": "Low",
        "net_profit_kes_per_acre": 74000,
        "score_breakdown": "rain fit 91%, temp fit 36%, dry-spell tolerance 100%, onset timing 100%",
    }
    print(humanize_crop_recommendation(example_rec))

    example_loan = {
        "crop": "Maize", "credit_grade": "A (Moderate Risk)", "interest_rate_pct": 14.2,
        "expected_default_rate_pct": 8.9, "recommendation": "Approved with Weather Insurance",
        "provenance": {"fields": {"risk_weights": {"provenance": "assumed"}}},
    }
    print(humanize_loan_decision(example_loan))

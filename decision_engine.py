


def calculate_decision_context(
    goal,
    years_to_goal,
    risk_profile,
    current_fund_value,
    proposed_redemption,
    monthly_sip,
    redemption_reason,
    goal_target_amount=None
):

    # -----------------------------
    # 1. Basic calculations
    # -----------------------------
    redemption_percentage = (
        proposed_redemption / current_fund_value * 100
        if current_fund_value > 0 else 0
    )

    remaining_fund_value = current_fund_value - proposed_redemption

    remaining_percentage = (
        remaining_fund_value / current_fund_value * 100
        if current_fund_value > 0 else 0
    )

    sip_month_equivalent = (
        proposed_redemption / monthly_sip
        if monthly_sip > 0 else None
    )

    # -----------------------------
    # 2. Goal coverage calculations
    # -----------------------------
    if goal_target_amount is not None and goal_target_amount > 0:

        goal_coverage_before = (
            current_fund_value / goal_target_amount * 100
        )

        goal_coverage_after = (
            remaining_fund_value / goal_target_amount * 100
        )

        goal_gap_before = max(
            goal_target_amount - current_fund_value, 0
        )

        goal_gap_after = max(
            goal_target_amount - remaining_fund_value, 0
        )

    else:
        goal_coverage_before = None
        goal_coverage_after = None
        goal_gap_before = None
        goal_gap_after = None

    # -----------------------------
    # 3. Redemption size
    # -----------------------------
    if redemption_percentage >= 75:
        redemption_size = "Very large portion of current holding"
    elif redemption_percentage >= 50:
        redemption_size = "Large portion of current holding"
    elif redemption_percentage >= 25:
        redemption_size = "Moderate portion of current holding"
    else:
        redemption_size = "Smaller portion of current holding"

    # -----------------------------
    # 4. Investment horizon
    # -----------------------------
    if years_to_goal <= 1:
        horizon_type = "Very short-term"
    elif years_to_goal <= 3:
        horizon_type = "Short-to-medium-term"
    elif years_to_goal <= 7:
        horizon_type = "Medium-to-long-term"
    else:
        horizon_type = "Long-term"

    # -----------------------------
    # 5. Goal proximity
    # -----------------------------
    if years_to_goal <= 2:
        goal_proximity = "Close"
    elif years_to_goal <= 5:
        goal_proximity = "Moderately close"
    else:
        goal_proximity = "Longer-term"

    # -----------------------------
    # 6. Decision facts
    # -----------------------------
    decision_facts = [
        f"You are considering redeeming ₹{proposed_redemption:,.0f}.",
        f"This represents {redemption_percentage:.1f}% of your current investment.",
        f"Approximately ₹{remaining_fund_value:,.0f} would remain invested.",
        f"{remaining_percentage:.1f}% of the current investment would remain.",
        f"Your stated goal is {years_to_goal:g} years away.",
        f"Your investment horizon is classified as {horizon_type}.",
        f"The redemption is classified as a {redemption_size.lower()}."
    ]

    if monthly_sip > 0 and sip_month_equivalent is not None:
        decision_facts.append(
            f"The proposed redemption is approximately "
            f"{sip_month_equivalent:.1f} months of your current SIP."
        )

    if goal_coverage_before is not None:
        decision_facts.extend([
            (
                f"This fund currently covers "
                f"{goal_coverage_before:.1f}% of your stated goal "
                f"based on its current value."
            ),
            (
                f"After the proposed redemption, this fund would cover "
                f"{goal_coverage_after:.1f}% of your stated goal."
            ),
            (
                f"The remaining goal gap based on this fund's value "
                f"would change from ₹{goal_gap_before:,.0f} "
                f"to ₹{goal_gap_after:,.0f}."
            )
        ])

    # -----------------------------
    # 7. Goal implication
    # -----------------------------
    if years_to_goal <= 2:
        goal_implication = (
            f"Your goal is relatively close ({years_to_goal:g} years away). "
            f"The amount remaining invested is therefore an important "
            f"part of the decision context."
        )
    elif years_to_goal <= 5:
        goal_implication = (
            f"Your goal is {years_to_goal:g} years away. "
            f"The redemption changes how much capital remains invested "
            f"toward that goal."
        )
    else:
        goal_implication = (
            f"Your goal is {years_to_goal:g} years away. "
            f"The measurable change is the amount of capital remaining "
            f"invested toward that longer-term goal."
        )

    # -----------------------------
    # 8. Risk context
    # -----------------------------
    risk_context = (
        f"Your stated risk profile is {risk_profile}. "
        f"The system uses this as context but does not determine "
        f"whether you should redeem."
    )

    # -----------------------------
    # 9. Factors relevant to reason
    # -----------------------------
    if redemption_reason == "Worried about market":

        relevant_factors = [
            "Historical drawdown and recovery",
            "Fund and market movement during the analyzed period",
            "Amount being removed from the investment",
            "Remaining investment after redemption"
        ]

        reason_implication = (
            "Because your stated reason is concern about the market, "
            "historical volatility and drawdown information are relevant. "
            "However, historical behavior does not predict the future."
        )

        show_market_context = True
        show_drawdown = True
        show_benchmark = False

    elif redemption_reason == "Need money":

        relevant_factors = [
            "Amount of money being withdrawn",
            "Percentage of the current investment being withdrawn",
            "Amount remaining invested",
            "Relationship between the withdrawal and your stated goal horizon"
        ]

        reason_implication = (
            "Because you need money, the key question is how much capital "
            "you are removing and how much remains invested afterward."
        )

        show_market_context = False
        show_drawdown = False
        show_benchmark = False

    elif redemption_reason == "Goal changed":

        relevant_factors = [
            "Updated investment goal",
            "Years remaining for the goal",
            "Amount being withdrawn",
            "Capital remaining after redemption"
        ]

        reason_implication = (
            "Because your goal has changed, the important context is how "
            "the proposed redemption changes the capital still connected "
            "to the new goal."
        )

        show_market_context = False
        show_drawdown = False
        show_benchmark = False

    elif redemption_reason == "Fund underperformance":

        relevant_factors = [
            "Fund historical return",
            "Benchmark historical return",
            "Difference between fund and benchmark",
            "Time period used for the comparison"
        ]

        reason_implication = (
            "Because your stated reason is fund underperformance, "
            "historical fund-versus-benchmark performance is relevant. "
            "It does not establish future performance."
        )

        show_market_context = True
        show_drawdown = False
        show_benchmark = True

    elif redemption_reason == "Found another investment":

        relevant_factors = [
            "Amount leaving the current investment",
            "Percentage of current capital being removed",
            "Capital remaining in the current investment",
            "The system does not assume the alternative investment is better"
        ]

        reason_implication = (
            "Because you found another investment, this tool focuses on "
            "what changes in your current investment. It does not evaluate "
            "or recommend the alternative investment."
        )

        show_market_context = False
        show_drawdown = False
        show_benchmark = False

    else:

        relevant_factors = [
            "Redemption amount",
            "Percentage of investment affected",
            "Remaining investment",
            "Goal and investment horizon"
        ]

        reason_implication = (
            "The system is showing the measurable consequences of "
            "your proposed redemption."
        )

        show_market_context = False
        show_drawdown = False
        show_benchmark = False

    # -----------------------------
    # 10. Decision summary
    # -----------------------------
    decision_summary = (
        f"You are considering redeeming ₹{proposed_redemption:,.0f} "
        f"from a ₹{current_fund_value:,.0f} investment, leaving "
        f"₹{remaining_fund_value:,.0f} invested."
    )

    # -----------------------------
    # 11. Uncertainty
    # -----------------------------
    uncertainty = [
        "The system cannot predict future market or fund performance.",
        "It cannot know whether your financial situation will change later.",
        "It does not know whether the proposed redemption is personally suitable for you.",
        "Historical performance should not be treated as a guarantee of future results."
    ]

    if goal_target_amount is not None and goal_target_amount > 0:
        uncertainty.append(
            "Goal coverage uses only this fund's current value and "
            "does not include other savings, investments, future SIPs, "
            "inflation or future returns."
        )

    # -----------------------------
    # 12. Return structured decision
    # -----------------------------
    return {
        "redemption_percentage": redemption_percentage,
        "remaining_fund_value": remaining_fund_value,
        "remaining_percentage": remaining_percentage,
        "sip_month_equivalent": sip_month_equivalent,

        "goal_target_amount": goal_target_amount,
        "goal_coverage_before": goal_coverage_before,
        "goal_coverage_after": goal_coverage_after,
        "goal_gap_before": goal_gap_before,
        "goal_gap_after": goal_gap_after,

        "redemption_size": redemption_size,
        "horizon_type": horizon_type,
        "goal_proximity": goal_proximity,

        "decision_facts": decision_facts,
        "goal_implication": goal_implication,
        "risk_context": risk_context,

        "relevant_factors": relevant_factors,
        "reason_implication": reason_implication,

        "show_market_context": show_market_context,
        "show_drawdown": show_drawdown,
        "show_benchmark": show_benchmark,

        "decision_summary": decision_summary,
        "uncertainty": uncertainty
    }

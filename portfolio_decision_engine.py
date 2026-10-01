

def get_portfolio_decision_context(
    redemption_reason,
    top_10_concentration,
    top_holding,
    top_holding_exposure,
    largest_sector,
    largest_sector_exposure,
    security_count
):
    """
    Selects portfolio facts that are most relevant
    to the investor's stated decision reason.

    This does not make a recommendation.
    It only determines which facts should be highlighted.
    """

    context = {
        "reason": redemption_reason,
        "facts": [],
        "explanation": ""
    }

    # --------------------------------------------------------
    # WORRIED ABOUT MARKET
    # --------------------------------------------------------

    if redemption_reason == "Worried about market":

        context["facts"] = [
            f"The fund has {security_count} reported equity securities.",
            f"The largest individual holding is {top_holding} "
            f"at {top_holding_exposure:.2f}% of NAV.",
            f"The largest sector is {largest_sector} "
            f"at {largest_sector_exposure:.2f}% of NAV.",
            f"The top 10 holdings together represent "
            f"{top_10_concentration:.2f}% of NAV."
        ]

        context["explanation"] = (
            "These portfolio exposures provide context about "
            "where the fund's equity exposure is concentrated "
            "when considering market-related concerns."
        )

    # --------------------------------------------------------
    # NEED MONEY
    # --------------------------------------------------------

    elif redemption_reason == "Need money":

        context["facts"] = [
            f"The fund currently has exposure across "
            f"{security_count} reported equity securities.",
            f"The top 10 holdings represent "
            f"{top_10_concentration:.2f}% of NAV."
        ]

        context["explanation"] = (
            "For a liquidity-driven decision, portfolio "
            "composition is secondary to the amount being "
            "redeemed and the investment remaining afterward."
        )

    # --------------------------------------------------------
    # GOAL CHANGED
    # --------------------------------------------------------

    elif redemption_reason == "Goal changed":

        context["facts"] = [
            f"The fund has {security_count} reported equity securities.",
            f"The largest sector is {largest_sector} "
            f"at {largest_sector_exposure:.2f}% of NAV.",
            f"The top 10 holdings represent "
            f"{top_10_concentration:.2f}% of NAV."
        ]

        context["explanation"] = (
            "Portfolio composition provides context about "
            "the investment being used toward the goal, "
            "while the goal amount and horizon determine "
            "the direct goal impact."
        )

    # --------------------------------------------------------
    # FUND UNDERPERFORMANCE
    # --------------------------------------------------------

    elif redemption_reason == "Fund underperformance":

        context["facts"] = [
            f"The largest individual holding is {top_holding} "
            f"at {top_holding_exposure:.2f}% of NAV.",
            f"The largest sector is {largest_sector} "
            f"at {largest_sector_exposure:.2f}% of NAV.",
            f"The top 10 holdings represent "
            f"{top_10_concentration:.2f}% of NAV."
        ]

        context["explanation"] = (
            "Portfolio composition can provide context for "
            "understanding what exposures contributed to the "
            "fund's overall structure. It does not by itself "
            "explain future performance."
        )

    # --------------------------------------------------------
    # FOUND ANOTHER INVESTMENT
    # --------------------------------------------------------

    elif redemption_reason == "Found another investment":

        context["facts"] = [
            f"The fund has {security_count} reported equity securities.",
            f"The top 10 holdings represent "
            f"{top_10_concentration:.2f}% of NAV.",
            f"The largest sector is {largest_sector} "
            f"at {largest_sector_exposure:.2f}% of NAV."
        ]

        context["explanation"] = (
            "These facts describe what exposure would remain "
            "in the current fund if part of the investment "
            "were redeemed."
        )

    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    else:

        context["facts"] = [
            f"The fund has {security_count} reported equity securities.",
            f"The top 10 holdings represent "
            f"{top_10_concentration:.2f}% of NAV.",
            f"The largest individual holding is {top_holding} "
            f"at {top_holding_exposure:.2f}% of NAV.",
            f"The largest sector is {largest_sector} "
            f"at {largest_sector_exposure:.2f}% of NAV."
        ]

        context["explanation"] = (
            "These portfolio facts provide general context "
            "about the structure of the fund."
        )

    return context

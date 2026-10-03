
# ============================================================
# DECISORA DECISION COPILOT
# Fresh native Streamlit UI
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import importlib


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Decisora Decision Copilot",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# IMPORT EXISTING ENGINES
# ============================================================

import decision_engine
import portfolio_decision_engine
import answer_engine

importlib.reload(decision_engine)
importlib.reload(portfolio_decision_engine)
importlib.reload(answer_engine)


# ============================================================
# FILE LOCATION HELPER
# Works in Colab and later in Streamlit Cloud
# ============================================================

def find_file(filename):

    candidates = [
        Path("/content/data") / filename,
        Path("/content") / filename,
        Path("data") / filename,
        Path(filename)
    ]

    for path in candidates:

        if path.exists():
            return path

    return None


# ============================================================
# LOAD MARKET DATA
# ============================================================

@st.cache_data
def load_market_data():

    hdfc_path = find_file(
        "HDFC_Large_Cap_2025.csv"
    )

    nifty_path = find_file(
        "NIFTY_100_TRI_2025.csv"
    )

    if hdfc_path is None:
        raise FileNotFoundError(
            "HDFC_Large_Cap_2025.csv was not found. "
            "Place it inside the data folder."
        )

    if nifty_path is None:
        raise FileNotFoundError(
            "NIFTY_100_TRI_2025.csv was not found. "
            "Place it inside the data folder."
        )

    fund = pd.read_csv(hdfc_path)
    nifty = pd.read_csv(nifty_path)

    fund["Date"] = pd.to_datetime(fund["Date"])
    nifty["Date"] = pd.to_datetime(nifty["Date"])

    fund = fund.sort_values("Date")
    nifty = nifty.sort_values("Date")

    merged = pd.merge(
        fund,
        nifty,
        on="Date",
        how="inner"
    )

    return fund, nifty, merged


fund_data, nifty_data, comparison = load_market_data()


# ============================================================
# MARKET CALCULATIONS
# ============================================================

start_nav = float(
    comparison.iloc[0]["Net Asset Value"]
)

end_nav = float(
    comparison.iloc[-1]["Net Asset Value"]
)

start_nifty = float(
    comparison.iloc[0]["Total Returns Index"]
)

end_nifty = float(
    comparison.iloc[-1]["Total Returns Index"]
)


fund_return = (
    (end_nav / start_nav) - 1
) * 100


benchmark_return = (
    (end_nifty / start_nifty) - 1
) * 100


performance_difference = (
    fund_return - benchmark_return
)


# ============================================================
# DRAWDOWN
# ============================================================

comparison["Fund Peak"] = (
    comparison["Net Asset Value"]
    .cummax()
)

comparison["Drawdown"] = (
    comparison["Net Asset Value"]
    / comparison["Fund Peak"]
    - 1
) * 100


max_drawdown = float(
    comparison["Drawdown"].min()
)

drawdown_row = comparison.loc[
    comparison["Drawdown"].idxmin()
]

drawdown_date = pd.Timestamp(
    drawdown_row["Date"]
)

peak_before_drawdown = float(
    drawdown_row["Fund Peak"]
)


# ============================================================
# RECOVERY
# ============================================================

future_after_drawdown = comparison[
    comparison["Date"] > drawdown_date
]

recovery_date = None

for _, row in future_after_drawdown.iterrows():

    if row["Net Asset Value"] >= peak_before_drawdown:

        recovery_date = pd.Timestamp(
            row["Date"]
        )

        break


if recovery_date is not None:

    recovery_days = (
        recovery_date - drawdown_date
    ).days

else:

    recovery_days = None


# ============================================================
# PORTFOLIO DATA
# ============================================================

MONTHLY_FILES = [
    "Monthly HDFC Large Cap Fund - 31 January 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 28 February 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 31 March 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 30 April 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 31 May 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 30 June 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 31 July 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 31 August 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 30 September 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 31 October 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 30 November 2025.xlsx",
    "Monthly HDFC Large Cap Fund - 31 December 2025.xlsx"
]


def read_portfolio_snapshot(filename):

    path = find_file(filename)

    if path is None:
        return None

    raw = pd.read_excel(
        path,
        sheet_name="HDFCT2",
        header=None
    )

    # Existing HDFC portfolio files use the relevant
    # columns around the actual holdings table.
    df = raw.iloc[:, [1, 3, 4, 5, 6, 7]].copy()

    df.columns = [
        "ISIN",
        "Instrument",
        "Industry",
        "Quantity",
        "Market_Value_Lacs",
        "Percent_to_NAV"
    ]

    # Remove an unwanted pound symbol from instrument names.
    # This is a display cleanup only; portfolio values
    # and calculations remain unchanged.
    df["Instrument"] = (
        df["Instrument"]
        .astype("string")
        .str.replace("£", "", regex=False)
        .str.strip()
    )

    df["ISIN"] = df["ISIN"].astype(str)

    df["Percent_to_NAV"] = pd.to_numeric(
        df["Percent_to_NAV"],
        errors="coerce"
    )

    # Equity holdings
    equity = df[
        df["ISIN"].str.startswith(
            "INE",
            na=False
        )
    ].copy()

    equity = equity.dropna(
        subset=["Percent_to_NAV"]
    )

    if equity.empty:
        return None

    equity = equity.sort_values(
        "Percent_to_NAV",
        ascending=False
    )

    top10 = (
        equity.head(10)["Percent_to_NAV"]
        .sum()
    )

    top_holding = equity.iloc[0]

    sector = (
        equity.groupby("Industry")[
            "Percent_to_NAV"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    largest_sector = sector.index[0]

    largest_sector_exposure = float(
        sector.iloc[0]
    )

    return {
        "security_count": int(
            len(equity)
        ),
        "top_10_concentration": float(
            top10
        ),
        "top_holding": str(
            top_holding["Instrument"]
        ),
        "top_holding_exposure": float(
            top_holding["Percent_to_NAV"]
        ),
        "largest_sector": str(
            largest_sector
        ),
        "largest_sector_exposure": (
            largest_sector_exposure
        ),
        "equity": equity
    }


@st.cache_data
def load_portfolio_history():

    records = []

    for filename in MONTHLY_FILES:

        snapshot = read_portfolio_snapshot(
            filename
        )

        if snapshot is None:
            continue

        date_text = filename.split(
            " - "
        )[-1].replace(
            ".xlsx",
            ""
        )

        month_date = pd.to_datetime(
            date_text
        )

        record = {
            "Date": month_date,
            "security_count":
                snapshot["security_count"],
            "top_10_concentration":
                snapshot["top_10_concentration"],
            "top_holding":
                snapshot["top_holding"],
            "top_holding_exposure":
                snapshot["top_holding_exposure"],
            "largest_sector":
                snapshot["largest_sector"],
            "largest_sector_exposure":
                snapshot["largest_sector_exposure"]
        }

        records.append(record)

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(
        records
    ).sort_values("Date")


portfolio_history = load_portfolio_history()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 💰 Decisora")

    st.caption(
        "Decision Copilot"
    )

    st.divider()

    st.markdown(
        "### Investor profile"
    )

    current_fund_value = st.number_input(
        "Current investment (₹)",
        min_value=0.0,
        value=300000.0,
        step=10000.0
    )

    redemption_amount = st.number_input(
        "Proposed redemption (₹)",
        min_value=0.0,
        value=150000.0,
        step=10000.0
    )

    monthly_sip = st.number_input(
        "Monthly SIP (₹)",
        min_value=0.0,
        value=10000.0,
        step=1000.0
    )

    goal = st.selectbox(
        "Investment goal",
        [
            "Long-term wealth creation",
            "Home purchase",
            "Emergency liquidity"
        ]
    )

    years_to_goal = st.number_input(
        "Years to goal",
        min_value=0.0,
        value=12.0,
        step=1.0
    )

    risk_profile = st.selectbox(
        "Risk profile",
        [
            "Conservative",
            "Moderate",
            "Aggressive"
        ]
    )

    redemption_reason = st.selectbox(
        "Why are you considering redemption?",
        [
            "Worried about market",
            "Need money",
            "Fund underperformance",
            "Goal changed",
            "Found another investment",
            "Other"
        ]
    )

    goal_amount = st.number_input(
        "Estimated goal amount (₹)",
        min_value=0.0,
        value=1000000.0,
        step=50000.0
    )

    st.divider()

    st.caption(
        "This prototype provides decision-support "
        "information. It does not execute transactions."
    )


# ============================================================
# INPUT VALIDATION
# ============================================================

if redemption_amount > current_fund_value:

    st.error(
        "The proposed redemption cannot exceed "
        "the current investment."
    )

    st.stop()


remaining_fund_value = (
    current_fund_value
    - redemption_amount
)


redemption_percentage = (
    redemption_amount /
    current_fund_value * 100
    if current_fund_value > 0
    else 0
)


remaining_percentage = (
    remaining_fund_value /
    current_fund_value * 100
    if current_fund_value > 0
    else 0
)


sip_month_equivalent = (
    redemption_amount /
    monthly_sip
    if monthly_sip > 0
    else None
)


# ============================================================
# DECISION ENGINE
# ============================================================

decision = (
    decision_engine.calculate_decision_context(
        goal=goal,
        years_to_goal=years_to_goal,
        risk_profile=risk_profile,
        current_fund_value=current_fund_value,
        proposed_redemption=redemption_amount,
        monthly_sip=monthly_sip,
        redemption_reason=redemption_reason
    )
)


# ============================================================
# GOAL CALCULATIONS
# ============================================================

if goal_amount > 0:

    current_goal_coverage = (
        current_fund_value /
        goal_amount
    ) * 100

    remaining_goal_coverage = (
        remaining_fund_value /
        goal_amount
    ) * 100

    coverage_change = (
        remaining_goal_coverage -
        current_goal_coverage
    )

else:

    current_goal_coverage = None
    remaining_goal_coverage = None
    coverage_change = None


# ============================================================
# PORTFOLIO CONTEXT
# ============================================================

if not portfolio_history.empty:

    latest_portfolio = (
        portfolio_history
        .sort_values("Date")
        .iloc[-1]
    )

    security_count = int(
        latest_portfolio["security_count"]
    )

    top_10_concentration = float(
        latest_portfolio[
            "top_10_concentration"
        ]
    )

    top_holding = str(
        latest_portfolio["top_holding"]
    )

    top_holding_exposure = float(
        latest_portfolio[
            "top_holding_exposure"
        ]
    )

    largest_sector = str(
        latest_portfolio["largest_sector"]
    )

    largest_sector_exposure = float(
        latest_portfolio[
            "largest_sector_exposure"
        ]
    )

    portfolio_decision = (
        portfolio_decision_engine
        .get_portfolio_decision_context(
            redemption_reason,
            top_10_concentration,
            top_holding,
            top_holding_exposure,
            largest_sector,
            largest_sector_exposure,
            security_count
        )
    )

else:

    security_count = 0
    top_10_concentration = 0
    top_holding = "Unavailable"
    top_holding_exposure = 0
    largest_sector = "Unavailable"
    largest_sector_exposure = 0

    portfolio_decision = {
        "facts": [],
        "explanation":
            "Portfolio data unavailable."
    }


# ============================================================
# HEADER
# ============================================================

st.caption(
    "DECISORA  ·  DECISION CHECKPOINT"
)

st.title(
    "Understand the impact before you act."
)

st.write(
    "Review the measurable consequences of your "
    "proposed redemption before making the decision."
)


# ============================================================
# HERO DECISION
# ============================================================

with st.container(border=True):

    st.markdown(
        "### 🔎 Decision under review"
    )

    st.markdown(
        f"## Redeem ₹{redemption_amount:,.0f}"
    )

    st.write(
        f"This represents **{redemption_percentage:.1f}%** "
        f"of your current ₹{current_fund_value:,.0f} investment."
    )

    st.caption(
        f"Reason: {redemption_reason}"
    )


# ============================================================
# AT A GLANCE
# ============================================================

st.markdown(
    "### Decision at a glance"
)

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "Current investment",
        f"₹{current_fund_value:,.0f}"
    )

with c2:

    st.metric(
        "Redeeming",
        f"₹{redemption_amount:,.0f}"
    )

with c3:

    st.metric(
        "Remaining",
        f"₹{remaining_fund_value:,.0f}"
    )

with c4:

    st.metric(
        "Remaining %",
        f"{remaining_percentage:.1f}%"
    )


# ============================================================
# TABS
# ============================================================

tab_decision, tab_goal, tab_evidence, tab_ai = st.tabs(
    [
        "🎯 Decision impact",
        "📊 Goal impact",
        "🔎 Evidence",
        "🤖 Ask Decisora"
    ]
)


# ============================================================
# TAB 1 — DECISION IMPACT
# ============================================================

with tab_decision:

    st.subheader(
        "What changes?"
    )

    st.caption(
        "These are mechanical consequences of "
        "the proposed action."
    )

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Investment before",
            f"₹{current_fund_value:,.0f}"
        )

        st.metric(
            "Investment after",
            f"₹{remaining_fund_value:,.0f}"
        )

    with c2:

        if sip_month_equivalent is not None:

            st.metric(
                "Redemption / SIP equivalent",
                f"{sip_month_equivalent:.1f} months"
            )

        st.metric(
            "Amount removed",
            f"₹{redemption_amount:,.0f}"
        )


    st.divider()

    st.markdown(
        "### Why this information matters"
    )

    st.info(
        decision["reason_implication"]
    )

    st.markdown(
        "### Decision facts"
    )

    for fact in decision["decision_facts"]:

        st.write(
            f"• {fact}"
        )


# ============================================================
# TAB 2 — GOAL IMPACT
# ============================================================

with tab_goal:

    st.subheader(
        "Goal impact"
    )

    if goal_amount <= 0:

        st.warning(
            "Enter a goal amount to calculate "
            "current-value goal coverage."
        )

    else:

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Coverage before",
                f"{current_goal_coverage:.1f}%"
            )

        with c2:

            st.metric(
                "Coverage after",
                f"{remaining_goal_coverage:.1f}%"
            )

        with c3:

            st.metric(
                "Change",
                f"{coverage_change:.1f} pp"
            )


        st.markdown(
            "#### Current-value goal coverage"
        )

        before_after = pd.DataFrame(
            {
                "Goal coverage": [
                    current_goal_coverage,
                    remaining_goal_coverage
                ]
            },
            index=[
                "Before redemption",
                "After redemption"
            ]
        )

        st.bar_chart(
            before_after
        )


        if coverage_change < 0:

            st.warning(
                f"The proposed redemption reduces the "
                f"current-value goal coverage by "
                f"{abs(coverage_change):.1f} percentage points."
            )


        st.caption(
            "This is a current-value calculation. "
            "It does not forecast future investment returns."
        )


    st.divider()

    st.markdown(
        "### Your goal context"
    )

    st.write(
        decision["goal_implication"]
    )


# ============================================================
# TAB 3 — EVIDENCE
# ============================================================

with tab_evidence:

    st.subheader(
        "Evidence relevant to this decision"
    )

    st.caption(
        "Only evidence relevant to the selected reason "
        "is emphasized."
    )


    # --------------------------------------------------------
    # PORTFOLIO
    # --------------------------------------------------------

    st.markdown(
        "### Portfolio structure"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Equity securities",
            security_count
        )

    with c2:

        st.metric(
            "Top 10 concentration",
            f"{top_10_concentration:.2f}%"
        )

    with c3:

        st.metric(
            "Largest holding",
            top_holding
        )

    with c4:

        st.metric(
            "Largest sector",
            largest_sector
        )


    c1, c2 = st.columns(2)

    with c1:

        st.write(
            f"**Largest holding exposure:** "
            f"{top_holding_exposure:.2f}% of NAV"
        )

    with c2:

        st.write(
            f"**Largest sector exposure:** "
            f"{largest_sector_exposure:.2f}% of NAV"
        )


    if portfolio_decision.get("facts"):

        with st.expander(
            "View portfolio evidence"
        ):

            for fact in portfolio_decision["facts"]:

                st.write(
                    f"• {fact}"
                )


    # --------------------------------------------------------
    # MARKET EVIDENCE
    # --------------------------------------------------------

    if decision["show_market_context"]:

        st.divider()

        st.markdown(
            "### Historical market evidence"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "Fund return",
                f"{fund_return:.2f}%"
            )

        with c2:

            st.metric(
                "NIFTY 100 TRI",
                f"{benchmark_return:.2f}%"
            )

        with c3:

            st.metric(
                "Difference",
                f"{performance_difference:.2f} pp"
            )


        st.caption(
            "Common period: "
            f"{comparison.iloc[0]['Date'].strftime('%d %b %Y')} "
            "to "
            f"{comparison.iloc[-1]['Date'].strftime('%d %b %Y')}"
        )


        if decision["show_drawdown"]:

            st.markdown(
                "### Historical drawdown"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Maximum drawdown",
                    f"{max_drawdown:.2f}%"
                )

            with c2:

                st.metric(
                    "Drawdown date",
                    drawdown_date.strftime(
                        "%d %b %Y"
                    )
                )

            with c3:

                if recovery_days is not None:

                    st.metric(
                        "Recovery time",
                        f"{recovery_days} days"
                    )

                else:

                    st.metric(
                        "Recovery time",
                        "Not observed"
                    )


            chart_data = comparison[
                [
                    "Date",
                    "Net Asset Value"
                ]
            ].copy()

            chart_data = chart_data.set_index(
                "Date"
            )

            st.line_chart(
                chart_data
            )


            st.caption(
                "Historical market behavior is descriptive "
                "and does not predict future performance."
            )


    # --------------------------------------------------------
    # UNDERPERFORMANCE CONTEXT
    # --------------------------------------------------------

    if decision["show_benchmark"]:

        st.divider()

        st.info(
            "Because the stated reason is fund underperformance, "
            "the fund-versus-benchmark comparison is shown. "
            "Historical relative performance does not establish "
            "future performance."
        )


# ============================================================
# HISTORICAL DECISION REPLAY
# ============================================================

st.divider()

st.subheader(
    "🕰️ Historical decision replay"
)

st.caption(
    "A historical example showing what information was "
    "available at a past decision point. Future information "
    "is not used to construct the decision context."
)


decision_date = pd.Timestamp(
    "2025-03-04"
)

available_history = comparison[
    comparison["Date"] <= decision_date
].copy()


if not available_history.empty:

    replay_row = (
        available_history.iloc[-1]
    )

    replay_nav = float(
        replay_row["Net Asset Value"]
    )

    replay_start_nav = float(
        available_history.iloc[0]["Net Asset Value"]
    )

    replay_return = (
        replay_nav /
        replay_start_nav
        - 1
    ) * 100

    replay_peak = (
        available_history[
            "Net Asset Value"
        ].max()
    )

    replay_drawdown = (
        replay_nav /
        replay_peak
        - 1
    ) * 100


    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Decision date",
            decision_date.strftime(
                "%d %b %Y"
            )
        )

    with c2:

        st.metric(
            "Fund return to decision",
            f"{replay_return:.2f}%"
        )

    with c3:

        st.metric(
            "Drawdown from prior peak",
            f"{replay_drawdown:.2f}%"
        )


    if not portfolio_history.empty:

        historical_portfolios = (
            portfolio_history[
                portfolio_history["Date"]
                <= decision_date
            ]
        )

        if not historical_portfolios.empty:

            historical_snapshot = (
                historical_portfolios
                .iloc[-1]
            )

            st.markdown(
                "#### Portfolio information available "
                "at that point"
            )

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Securities",
                    int(
                        historical_snapshot[
                            "security_count"
                        ]
                    )
                )

            with c2:

                st.metric(
                    "Top 10 concentration",
                    f"{historical_snapshot['top_10_concentration']:.2f}%"
                )

            with c3:

                st.metric(
                    "Largest sector",
                    str(
                        historical_snapshot[
                            "largest_sector"
                        ]
                    )
                )


# ============================================================
# UNCERTAINTY
# ============================================================

st.divider()

st.subheader(
    "⚠️ What this system cannot know"
)

with st.container(border=True):

    for item in decision["uncertainty"]:

        st.write(
            f"• {item}"
        )


# ============================================================
# DECISION CHECKPOINT
# ============================================================

st.divider()

st.subheader(
    "Your decision"
)

st.write(
    "What would you like to do after reviewing "
    "the information?"
)


decision_choice = st.radio(
    "Decision checkpoint",
    [
        "Review the information again",
        "Change the proposed action",
        "Continue with the proposed action",
        "Do not proceed right now"
    ],
    horizontal=True
)


if decision_choice == "Review the information again":

    st.info(
        "Review the goal impact, relevant evidence, "
        "historical context and uncertainty above."
    )

elif decision_choice == "Change the proposed action":

    st.info(
        "Change the proposed redemption amount in the "
        "sidebar and review the consequences again."
    )

elif decision_choice == "Continue with the proposed action":

    st.success(
        "You selected to continue. "
        "This prototype does not execute transactions."
    )

else:

    st.info(
        "No transaction is executed. "
        "You remain in control."
    )


# ============================================================
# STRUCTURED DECISION FOR AI
# ============================================================

ai_structured_decision = {

    "goal": goal,

    "years_to_goal": years_to_goal,

    "risk_profile": risk_profile,

    "current_fund_value": current_fund_value,

    "proposed_redemption": redemption_amount,

    "redemption_percentage": redemption_percentage,

    "remaining_fund_value": remaining_fund_value,

    "remaining_percentage": remaining_percentage,

    "monthly_sip": monthly_sip,

    "sip_month_equivalent": sip_month_equivalent,

    "current_goal_coverage":
        current_goal_coverage,

    "remaining_goal_coverage":
        remaining_goal_coverage,

    "coverage_change":
        coverage_change,

    "redemption_reason":
        redemption_reason,

    "relevant_evidence":
        portfolio_decision.get(
            "facts",
            []
        ),

    "uncertainty":
        decision["uncertainty"]
}


# ============================================================
# AI EXPLANATION
# ============================================================

st.divider()

st.subheader(
    "🤖 Ask Decisora about this decision"
)

st.write(
    "Ask a question about the proposed redemption. "
    "The explanation is generated from the structured "
    "facts already calculated by the system."
)


st.caption(
    "Try: "
    "How much will remain invested? · "
    "What changes for my goal? · "
    "Why is this information relevant? · "
    "Should I redeem?"
)


user_question = st.text_input(
    "Your question",
    placeholder="Ask about this decision..."
)


if st.button(
    "Explain this decision",
    type="primary"
):

    if not user_question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        with st.spinner(
            "Preparing explanation..."
        ):

            ai_result = (
                answer_engine.answer_question(
                    ai_structured_decision,
                    user_question
                )
            )


        st.markdown(
            "### Explanation"
        )

        st.info(
            ai_result["answer"]
        )

        st.caption(
            f"Explanation source: "
            f"{ai_result['provider']}"
        )

        st.caption(
            "The explanation provides information about "
            "the decision and its consequences. It does "
            "not recommend whether you should proceed."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Decisora Decision Copilot · "
    "Prototype decision-support system · "
    "Historical information is descriptive, "
    "not a prediction or investment recommendation."
)

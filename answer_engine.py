

import os
import json
import re


def get_secret(name):
    value = os.environ.get(name)

    if value:
        return value

    # Streamlit Cloud secrets
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass

    # Google Colab secrets
    try:
        from google.colab import userdata
        return userdata.get(name)
    except Exception:
        return None


SYSTEM_PROMPT = """
You are the explanation layer of a financial decision-support system.

You are NOT the financial decision engine.

Your job is to explain structured facts already calculated
by the Python decision engine.

STRICT RULES:

1. Never calculate new financial numbers.
2. Never change or contradict supplied numbers.
3. Never invent financial facts.
4. Never predict future market or fund performance.
5. Never recommend buying, holding, redeeming, switching, or investing.
6. Never say one investment is better than another.
7. Never evaluate an alternative investment.
8. Never make a suitability judgment.
9. Clearly distinguish facts from uncertainty.
10. Keep the investor in control.
11. Use simple language.
12. If information is unavailable, say so.
13. The supplied structured decision is the source of truth.

Explain the information. Do not make the decision.
"""


def build_prompt(structured_decision, user_question):

    decision_json = json.dumps(
        structured_decision,
        indent=2,
        ensure_ascii=False,
        default=str
    )

    return f"""
USER QUESTION:

{user_question}

STRUCTURED DECISION DATA:

{decision_json}

Answer the user's question using ONLY the structured decision data.

If the question cannot be answered from the supplied data,
clearly say that the system does not have enough information.

Do not provide an investment recommendation.

Keep the answer concise and easy to understand.
"""


def deterministic_answer(structured_decision, user_question):

    question = user_question.lower().strip()

    current = structured_decision.get(
        "current_fund_value", 0
    )

    redemption = structured_decision.get(
        "proposed_redemption", 0
    )

    remaining = structured_decision.get(
        "remaining_fund_value", 0
    )

    redemption_percentage = structured_decision.get(
        "redemption_percentage", 0
    )

    remaining_percentage = structured_decision.get(
        "remaining_percentage", 0
    )

    reason = structured_decision.get(
        "redemption_reason", ""
    )

    goal = structured_decision.get(
        "goal", ""
    )

    years = structured_decision.get(
        "years_to_goal", None
    )

    current_coverage = structured_decision.get(
        "current_goal_coverage", None
    )

    remaining_coverage = structured_decision.get(
        "remaining_goal_coverage", None
    )

    coverage_change = structured_decision.get(
        "coverage_change", None
    )


    # --------------------------------------------------------
    # Direct decision questions
    # --------------------------------------------------------

    if any(word in question for word in [
        "should i",
        "should i redeem",
        "should i continue",
        "should i proceed",
        "is it better",
        "what should i do"
    ]):

        return (
            "The system does not determine whether you should "
            "redeem or continue. It provides the measurable "
            "consequences and relevant evidence so that you "
            "can make the decision."
        )


    # --------------------------------------------------------
    # Remaining investment
    # --------------------------------------------------------

    if (
        "how much" in question
        and (
            "remain" in question
            or "left" in question
        )
    ):

        return (
            f"If you redeem ₹{redemption:,.0f}, "
            f"approximately ₹{remaining:,.0f} would remain "
            f"invested."
        )


    # --------------------------------------------------------
    # Redemption percentage
    # --------------------------------------------------------

    if (
        "percent" in question
        or "%" in question
        or "portion" in question
    ):

        return (
            f"The proposed redemption is "
            f"{redemption_percentage:.1f}% of your current "
            f"₹{current:,.0f} investment."
        )


    # --------------------------------------------------------
    # Goal impact
    # --------------------------------------------------------

    if (
        "goal" in question
        and (
            "impact" in question
            or "change" in question
            or "affect" in question
            or "relevant" in question
        )
    ):

        if (
            current_coverage is not None
            and remaining_coverage is not None
        ):

            return (
                f"Your current-value goal coverage changes "
                f"from {current_coverage:.1f}% to "
                f"{remaining_coverage:.1f}% after the proposed "
                f"redemption, a change of "
                f"{coverage_change:.1f} percentage points. "
                f"Your stated goal is {years:g} years away. "
                f"This is a current-value calculation and does "
                f"not forecast future returns."
            )

        return (
            f"The proposed redemption changes the amount of "
            f"capital remaining toward your stated goal, "
            f"'{goal}'. The system does not forecast future "
            f"returns."
        )


    # --------------------------------------------------------
    # Why is this relevant?
    # --------------------------------------------------------

    if (
        "why" in question
        and (
            "relevant" in question
            or "matter" in question
            or "important" in question
        )
    ):

        if reason == "Found another investment":

            return (
                "Because your stated reason is that you found "
                "another investment, the relevant information "
                "is what changes in your current investment: "
                f"₹{redemption:,.0f} would be removed, "
                f"₹{remaining:,.0f} would remain invested, "
                f"and {redemption_percentage:.1f}% of the "
                "current investment would be redeemed. "
                "The system does not evaluate or recommend "
                "the alternative investment."
            )

        if reason == "Worried about market":

            return (
                "Because your stated reason is concern about "
                "the market, historical market and fund "
                "movement can provide context. Historical "
                "performance is descriptive and does not "
                "predict what will happen in the future."
            )

        if reason == "Need money":

            return (
                "Because your stated reason is that you need "
                "money, the most directly relevant facts are "
                f"the ₹{redemption:,.0f} being withdrawn and "
                f"the ₹{remaining:,.0f} that would remain "
                "invested."
            )

        if reason == "Goal changed":

            return (
                "Because your goal has changed, the relevant "
                "information is how the proposed redemption "
                "changes the capital remaining toward the "
                "stated goal."
            )

        if reason == "Fund underperformance":

            return (
                "Because your stated reason is fund "
                "underperformance, historical fund-versus-"
                "benchmark performance is relevant evidence. "
                "It does not establish future performance."
            )

        return (
            "The information is relevant because it shows "
            "the measurable consequences of the proposed "
            "redemption without deciding whether you should "
            "proceed."
        )


    # --------------------------------------------------------
    # General explanation
    # --------------------------------------------------------

    return (
        f"You are considering redeeming "
        f"₹{redemption:,.0f} from a "
        f"₹{current:,.0f} investment. This represents "
        f"{redemption_percentage:.1f}% of the current "
        f"investment and would leave approximately "
        f"₹{remaining:,.0f} invested. "
        f"Your stated reason is '{reason}'. "
        "The system provides these consequences as "
        "information; it does not determine whether you "
        "should proceed."
    )


def ask_gemini(prompt):

    api_key = get_secret("GEMINI_API_KEY")

    if not api_key:
        return None

    try:

        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,
                max_output_tokens=800
            )
        )

        if response.text:
            return response.text.strip()

    except Exception as e:

        print(
            "Gemini unavailable:",
            str(e)
        )

    return None


def ask_groq(prompt):

    api_key = get_secret("GROQ_API_KEY")

    if not api_key:
        return None

    try:

        from groq import Groq

        client = Groq(
            api_key=api_key
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=800
        )

        text = response.choices[0].message.content

        if text:
            return text.strip()

    except Exception as e:

        print(
            "Groq unavailable:",
            str(e)
        )

    return None


def ask_openrouter(prompt):

    api_key = get_secret(
        "OPENROUTER_API_KEY"
    )

    if not api_key:
        return None

    try:

        import requests

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization":
                    f"Bearer {api_key}",
                "Content-Type":
                    "application/json"
            },
            json={
                "model":
                    "openai/gpt-oss-20b:free",
                "messages": [
                    {
                        "role":
                            "system",
                        "content":
                            SYSTEM_PROMPT
                    },
                    {
                        "role":
                            "user",
                        "content":
                            prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 800
            },
            timeout=15
        )

        if response.status_code != 200:

            print(
                "OpenRouter unavailable:",
                response.status_code
            )

            return None

        data = response.json()

        text = data[
            "choices"
        ][0][
            "message"
        ][
            "content"
        ]

        if text:
            return text.strip()

    except Exception as e:

        print(
            "OpenRouter unavailable:",
            str(e)
        )

    return None


def answer_question(
    structured_decision,
    user_question
):

    # First use deterministic logic for questions
    # that can be answered directly from known facts.

    direct_keywords = [
        "how much",
        "how many",
        "what percent",
        "what percentage",
        "what changes",
        "should i",
        "why is",
        "why does",
        "why this",
        "how does"
    ]

    question_lower = (
        user_question.lower()
    )

    # For deterministic questions, use Python first.
    if any(
        keyword in question_lower
        for keyword in direct_keywords
    ):

        answer = deterministic_answer(
            structured_decision,
            user_question
        )

        return {
            "answer": answer,
            "provider":
                "Deterministic Engine",
            "fallback": False
        }


    # LLM explanation for questions that benefit
    # from natural-language explanation.

    prompt = build_prompt(
        structured_decision,
        user_question
    )

    answer = ask_gemini(prompt)

    if answer:
        return {
            "answer": answer,
            "provider": "Gemini",
            "fallback": False
        }

    answer = ask_groq(prompt)

    if answer:
        return {
            "answer": answer,
            "provider": "Groq",
            "fallback": False
        }

    answer = ask_openrouter(prompt)

    if answer:
        return {
            "answer": answer,
            "provider": "OpenRouter",
            "fallback": False
        }

    answer = deterministic_answer(
        structured_decision,
        user_question
    )

    return {
        "answer": answer,
        "provider":
            "Deterministic Engine",
        "fallback": True
    }

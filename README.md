# Decisora – FinLit Decision Copilot

**An explainable financial decision-support prototype that helps investors understand the potential impact of a mutual fund redemption before making a decision.**

[**Live Demo**](https://decisora-finlit-decision-copilot-mcndhmwrdwk8nek6mdg3vg.streamlit.app/) ·
---

## Overview

Decisora is a financial literacy and decision-support application designed to help investors examine the measurable consequences of redeeming a mutual fund investment.

Instead of predicting market movements or telling users whether to redeem or hold, Decisora presents relevant financial information, goal coverage, portfolio structure, historical market evidence, and uncertainty in a structured format.

The goal is to make financial decisions more transparent, understandable, and evidence-based while keeping the final decision with the investor.

## Problem Statement

Investors may consider redeeming mutual fund investments because of market volatility, fund underperformance, changing financial goals, or an immediate need for liquidity.

However, they may not clearly understand:

* How much of their investment they are proposing to redeem.
* How much investment value would remain afterward.
* How a redemption changes current-value coverage of a financial goal.
* How changing a goal's target amount or timeline affects the comparison.
* What historical fund and benchmark data can—and cannot—tell them.

Decisora addresses these information gaps through a structured decision-analysis workflow.

## Key Features

* **Redemption Impact Analysis:** Calculates the proposed redemption amount, redemption percentage, remaining investment value, and equivalent monthly SIP amount.
* **Goal Impact Analysis:** Compares current-value goal coverage and the remaining goal gap before and after a proposed redemption.
* **Goal Change Analysis:** Allows users to compare an original goal with a revised goal, including target amount, goal type, and time to goal.
* **Portfolio Structure Analysis:** Displays portfolio characteristics such as the number of equity securities, top-10 concentration, largest holding, and largest sector exposure, based on available portfolio data.
* **Historical Market Evidence:** Presents historical fund returns, NIFTY 100 TRI comparison, performance difference, maximum drawdown, and recovery time for the available period.
* **Historical Decision Replay:** Illustrates a past decision point using market and portfolio information available up to that date, avoiding the use of later observations in that historical context.
* **Ask FinLit:** Provides question-based explanations using structured decision information through the application's answer engine.
* **Decision Checkpoint:** Lets users review the information, change the proposed action, continue with their proposed action, or choose not to proceed. The application does not execute transactions.

## How It Works

1. **Enter investor context:** Provide investment value, proposed redemption, monthly SIP, goal, time to goal, risk profile, redemption reason, and estimated goal amount.
2. **Calculate the impact:** The decision engine calculates the direct financial consequences of the proposed redemption.
3. **Review goal changes:** Compare original and revised goal details to understand differences in current-value coverage and goal gaps.
4. **Examine evidence:** Review relevant portfolio structure and historical market information.
5. **Understand uncertainty:** Review factors that cannot be determined from the available data.
6. **Ask questions:** Use Ask FinLit to explore the structured information.
7. **Make your own decision:** Use the information as context; the application does not recommend or execute a transaction.

## Data Used

The prototype uses historical data for **HDFC Large Cap Fund – Direct Plan – Growth Option** and the **NIFTY 100 TRI** for 2025, along with monthly portfolio disclosures for the fund.

The application uses these datasets to calculate and display historical observations. Historical returns and portfolio characteristics are descriptive and should not be interpreted as forecasts.

> Update this section if you change the fund, benchmark, period, or underlying datasets.

## Technology Stack

* **Python** – Core application logic and calculations
* **Streamlit** – Interactive web application
* **Pandas** – Data loading, processing, and analysis
* **NumPy** – Numerical operations
* **Excel and CSV** – Historical NAV, benchmark, and portfolio data
* **Decision Engine** – Deterministic financial impact calculations
* **Portfolio Decision Engine** – Portfolio context and evidence
* **Answer Engine** – Question-based explanations from structured decision information
* **Streamlit Community Cloud** – Application deployment

## Project Structure

```text
FinLit-Decision-Copilot/
│
├── app.py
├── financial_data.py
├── decision_engine.py
├── scenario_engine.py
├── portfolio_context.py
├── portfolio_decision_engine.py
├── historical_portfolio.py
├── historical_replay.py
├── decision_structure.py
├── explainable_ai.py
├── answer_engine.py
│
├── data/
│   ├── HDFC_Large_Cap_2025.csv
│   ├── NIFTY_100_TRI_2025.csv
│   └── Monthly portfolio files
│
├── requirements.txt
└── README.md
```

*The listed structure represents the project's intended organization. Keep only files and modules that are actually present in your repository.*

## Run Locally

### 1. Clone the repository

```bash
git clone PASTE_YOUR_GITHUB_REPOSITORY_URL_HERE
cd FinLit-Decision-Copilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add the data files

Place the required CSV and monthly portfolio files in the `data/` folder, following the filenames and structure expected by the application.

### 5. Run the application

```bash
streamlit run app.py
```

Streamlit will provide a local URL to open the application in your browser.

## Design Principles

* **Explainability:** Present calculations and evidence in a way that users can inspect.
* **Transparency:** Distinguish historical observations, calculated consequences, and uncertainty.
* **No market prediction:** Do not present historical performance as a prediction of future returns.
* **User agency:** Provide decision-support information without making the decision for the investor.
* **Evidence-based context:** Use the available historical datasets and disclose where information is incomplete.

## Limitations

* The application is a prototype for financial literacy and decision support, not a registered investment advisory service.
* Historical data does not predict future market performance.
* Goal coverage is a current-value comparison and does not automatically account for inflation, future contributions, taxes, exit loads, or future returns.
* Portfolio context depends on the completeness and accuracy of the available portfolio disclosures.
* The application does not evaluate every investor-specific circumstance or execute any financial transaction.
* Any AI-generated explanation may have limitations and should be checked against the displayed calculations and evidence.

## Future Improvements

* Add support for more mutual funds and benchmarks.
* Expand historical analysis to additional years.
* Improve data validation and automated dataset updates.
* Add more interactive scenario comparisons.
* Improve the traceability of explanations to the underlying calculations and evidence.
* Expand testing for calculation accuracy and data edge cases.

## Disclaimer

Decisora is an educational financial decision-support prototype. It is not financial, investment, tax, or legal advice, and it does not recommend buying, holding, or selling any investment. Users should independently evaluate their circumstances and consult a qualified professional when appropriate. No transactions are executed by this application.

## Author

Tushar Kumar Mishra


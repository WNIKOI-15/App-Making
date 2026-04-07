import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------
# Page setup
# ---------------------------
st.set_page_config(page_title="Sustainable Portfolio Optimizer", layout="wide")
st.title("🌱 Sustainable Portfolio Optimizer")
st.write("Build a personalised portfolio based on financial risk and ESG preferences.")

# ---------------------------
# Sidebar inputs
# ---------------------------
st.sidebar.header("Asset Names")
asset1_name = st.sidebar.text_input("Asset 1 Name", value="Asset 1")
asset2_name = st.sidebar.text_input("Asset 2 Name", value="Asset 2")

st.sidebar.header("Asset Data")

r_h = st.sidebar.number_input(f"{asset1_name} Expected Return (%)", value=5.0) / 100
sd_h = st.sidebar.number_input(f"{asset1_name} Standard Deviation (%)", value=9.0) / 100

r_f = st.sidebar.number_input(f"{asset2_name} Expected Return (%)", value=12.0) / 100
sd_f = st.sidebar.number_input(f"{asset2_name} Standard Deviation (%)", value=20.0) / 100

rho_hf = st.sidebar.number_input("Correlation", min_value=-1.0, max_value=1.0, value=-0.2)
r_free = st.sidebar.number_input("Risk-Free Rate (%)", value=2.0) / 100

st.sidebar.header("Sustainability Inputs")
esg1 = st.sidebar.slider(f"{asset1_name} ESG Score", min_value=0, max_value=100, value=75)
esg2 = st.sidebar.slider(f"{asset2_name} ESG Score", min_value=0, max_value=100, value=55)

st.sidebar.header("Investor Preferences")
gamma = st.sidebar.slider("Risk Aversion (γ)", min_value=0.1, max_value=10.0, value=5.0, step=0.1)
lambda_esg = st.sidebar.slider("ESG Preference (λ)", min_value=0.0, max_value=1.0, value=0.3, step=0.1)

run_optimization = st.sidebar.button("Optimize Portfolio")

# ---------------------------
# Functions
# ---------------------------
def portfolio_ret(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(
        w1**2 * sd1**2 +
        (1 - w1)**2 * sd2**2 +
        2 * rho * w1 * (1 - w1) * sd1 * sd2
    )

def portfolio_esg(w1, esg_1, esg_2):
    return w1 * esg_1 + (1 - w1) * esg_2

def portfolio_utility(ret, risk, esg, gamma_value, lambda_value):
    return ret + lambda_value * (esg / 100) - 0.5 * gamma_value * (risk ** 2)

# ---------------------------
# App execution
# ---------------------------
if run_optimization:

    # Generate portfolio combinations
    weights = np.linspace(0, 1, 1000)

    portfolio_returns = []
    portfolio_risks = []
    portfolio_esg_scores = []
    portfolio_utilities = []

    for w in weights:
        ret = portfolio_ret(w, r_h, r_f)
        risk = portfolio_sd(w, sd_h, sd_f, rho_hf)
        esg = portfolio_esg(w, esg1, esg2)
        utility = portfolio_utility(ret, risk, esg, gamma, lambda_esg)

        portfolio_returns.append(ret)
        portfolio_risks.append(risk)
        portfolio_esg_scores.append(esg)
        portfolio_utilities.append(utility)

    # Convert to arrays
    portfolio_returns = np.array(portfolio_returns)
    portfolio_risks = np.array(portfolio_risks)
    portfolio_esg_scores = np.array(portfolio_esg_scores)
    portfolio_utilities = np.array(portfolio_utilities)

    # Find optimal portfolio
    best_idx = np.argmax(portfolio_utilities)

    w1_optimal = weights[best_idx]
    w2_optimal = 1 - w1_optimal

    ret_optimal = portfolio_returns[best_idx]
    sd_optimal = portfolio_risks[best_idx]
    esg_optimal = portfolio_esg_scores[best_idx]
    utility_optimal = portfolio_utilities[best_idx]

    # Sharpe ratio of recommended portfolio
    if sd_optimal > 0:
        sharpe_optimal = (ret_optimal - r_free) / sd_optimal
    else:
        sharpe_optimal = 0

    # Results table
    recommended_weights = pd.DataFrame({
        "Asset": [asset1_name, asset2_name],
        "Weight (%)": [w1_optimal * 100, w2_optimal * 100],
        "Expected Return (%)": [r_h * 100, r_f * 100],
        "Standard Deviation (%)": [sd_h * 100, sd_f * 100],
        "ESG Score": [esg1, esg2]
    })

    # Interpretation text
    if esg_optimal > 70:
        esg_text = "high ESG quality"
    elif esg_optimal > 50:
        esg_text = "moderate ESG quality"
    else:
        esg_text = "lower ESG quality"

    if gamma >= 7:
        risk_text = "a relatively risk-averse investor"
    elif gamma >= 4:
        risk_text = "a moderately risk-averse investor"
    else:
        risk_text = "a relatively risk-tolerant investor"

    summary_text = (
        f"The recommended portfolio allocates {w1_optimal*100:.2f}% to {asset1_name} "
        f"and {w2_optimal*100:.2f}% to {asset2_name}. "
        f"It offers an expected return of {ret_optimal*100:.2f}%, "
        f"risk of {sd_optimal*100:.2f}%, and an ESG score of {esg_optimal:.2f}. "
        f"Given your preferences, the model identifies this as the highest-utility portfolio. "
        f"This reflects {esg_text} and is suited to {risk_text}."
    )

    # Tabs
    tab1, tab2 = st.tabs(["📊 Results", "📈 Graph"])

    with tab1:
        st.header("Recommended Portfolio")
        st.info(summary_text)

        st.subheader("Recommended Asset Weights")
        st.dataframe(recommended_weights, use_container_width=True)

        st.subheader("Portfolio Characteristics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Expected Return", f"{ret_optimal*100:.2f}%")
        col2.metric("Risk (Std Dev)", f"{sd_optimal*100:.2f}%")
        col3.metric("Portfolio ESG Score", f"{esg_optimal:.2f}")

        col4, col5 = st.columns(2)
        col4.metric("Utility", f"{utility_optimal:.4f}")
        col5.metric("Sharpe Ratio", f"{sharpe_optimal:.3f}")

        st.subheader("Investor Preference Summary")
        pref_col1, pref_col2 = st.columns(2)
        pref_col1.metric("Risk Aversion (γ)", f"{gamma:.1f}")
        pref_col2.metric("ESG Preference (λ)", f"{lambda_esg:.1f}")

    with tab2:
        st.header("ESG-Aware Portfolio Frontier")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot frontier
        ax.plot(
            portfolio_risks,
            portfolio_returns,
            linewidth=2,
            label="Portfolio Frontier"
        )

        # Highlight optimal portfolio
        ax.scatter(
            sd_optimal,
            ret_optimal,
            s=180,
            marker='D',
            zorder=5,
            label="Recommended Portfolio"
        )

        # Optional: show individual assets
        ax.scatter(sd_h, r_h, s=120, marker='o', zorder=5, label=asset1_name)
        ax.scatter(sd_f, r_f, s=120, marker='o', zorder=5, label=asset2_name)

        # Optional: show risk-free asset
        ax.scatter(0, r_free, s=120, marker='s', zorder=5, label="Risk-Free Asset")

        ax.set_xlabel("Risk (Standard Deviation)")
        ax.set_ylabel("Expected Return")
        ax.set_title("Portfolio Risk-Return Frontier")

        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        ax.legend()
        ax.grid(True, alpha=0.3)

        st.pyplot(fig)

        st.caption(
            "The highlighted diamond represents the portfolio that maximizes the investor's utility, "
            "taking into account return, risk, and ESG preference."
        )

else:
    st.warning("Adjust the inputs in the sidebar and click 'Optimize Portfolio' to generate your recommended portfolio.")


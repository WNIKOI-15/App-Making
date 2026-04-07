import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ---------------------------------
# PAGE CONFIG
# ---------------------------------
st.set_page_config(
    page_title="GreenVest Portfolio Optimizer",
    page_icon="🌿",
    layout="wide"
)

# ---------------------------------
# CUSTOM CSS STYLING
# ---------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f4fbf6 0%, #e8f5e9 100%);
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1b5e20;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1.05rem;
        color: #2e7d32;
        margin-bottom: 1.2rem;
    }

    .section-card {
        background-color: white;
        border: 1px solid #d0e8d4;
        border-radius: 18px;
        padding: 18px 22px;
        box-shadow: 0 4px 14px rgba(27, 94, 32, 0.08);
        margin-bottom: 16px;
    }

    .quiz-box {
        background: #f1f8f4;
        border-left: 6px solid #43a047;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 10px;
    }

    .small-note {
        color: #4e6e56;
        font-size: 0.92rem;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dceedd;
        padding: 14px;
        border-radius: 16px;
        box-shadow: 0 3px 10px rgba(27, 94, 32, 0.05);
    }

    .stButton > button {
        background: linear-gradient(90deg, #2e7d32, #43a047);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        padding: 0.6rem 1rem;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #1b5e20, #2e7d32);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# HEADER
# ---------------------------------
st.markdown('<div class="main-title">🌿 GreenVest Portfolio Optimizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Build a personalised investment portfolio based on financial risk and ESG preferences.</div>',
    unsafe_allow_html=True
)

# ---------------------------------
# FUNCTIONS
# ---------------------------------
def portfolio_ret(w1, r1, r2):
    return w1 * r1 + (1 - w1) * r2

def portfolio_sd(w1, sd1, sd2, rho):
    return np.sqrt(
        w1**2 * sd1**2
        + (1 - w1)**2 * sd2**2
        + 2 * rho * w1 * (1 - w1) * sd1 * sd2
    )

def portfolio_esg(w1, esg1, esg2):
    return w1 * esg1 + (1 - w1) * esg2

def portfolio_utility(ret, risk, esg, gamma, lambda_esg):
    return ret + lambda_esg * (esg / 100) - 0.5 * gamma * (risk ** 2)

def quiz_to_lambda(score, max_score):
    return round(score / max_score, 2)

# ---------------------------------
# SIDEBAR INPUTS
# ---------------------------------
st.sidebar.header("Portfolio Setup")

asset1_name = st.sidebar.text_input("Asset 1 Name", value="Green Bond Fund")
asset2_name = st.sidebar.text_input("Asset 2 Name", value="Global Equity Fund")

r1 = st.sidebar.number_input(f"{asset1_name} Expected Return (%)", value=5.0) / 100
sd1 = st.sidebar.number_input(f"{asset1_name} Standard Deviation (%)", value=9.0) / 100
esg1 = st.sidebar.slider(f"{asset1_name} ESG Rating", 0, 100, 80)

r2 = st.sidebar.number_input(f"{asset2_name} Expected Return (%)", value=12.0) / 100
sd2 = st.sidebar.number_input(f"{asset2_name} Standard Deviation (%)", value=20.0) / 100
esg2 = st.sidebar.slider(f"{asset2_name} ESG Rating", 0, 100, 55)

rho = st.sidebar.number_input("Correlation", min_value=-1.0, max_value=1.0, value=-0.2)
r_free = st.sidebar.number_input("Risk-Free Rate (%)", value=2.0) / 100
gamma = st.sidebar.slider("Risk Aversion (γ)", 0.1, 10.0, 5.0, 0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("ESG Preference Method")
pref_method = st.sidebar.radio(
    "Choose how to set ESG preference:",
    ["Use ESG Quiz", "Set Manually"]
)

# ---------------------------------
# ESG QUIZ
# ---------------------------------
lambda_esg = 0.3

if pref_method == "Use ESG Quiz":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("ESG Preference Quiz")
    st.markdown(
        '<div class="quiz-box">Answer these quick questions to estimate how strongly sustainability matters in your investment decisions.</div>',
        unsafe_allow_html=True
    )

    q1 = st.radio(
        "1. When choosing between two investments with similar returns, how important is the more sustainable option?",
        [
            "Not important",
            "Slightly important",
            "Moderately important",
            "Very important"
        ],
        key="q1"
    )

    q2 = st.radio(
        "2. Would you accept slightly lower returns for a portfolio with higher ESG quality?",
        [
            "No, returns come first",
            "Only a little",
            "Yes, to some extent",
            "Yes, definitely"
        ],
        key="q2"
    )

    q3 = st.radio(
        "3. How much do environmental and social issues influence your investment decisions?",
        [
            "Very little",
            "Somewhat",
            "Quite a lot",
            "A great deal"
        ],
        key="q3"
    )

    q4 = st.radio(
        "4. Which statement best describes you?",
        [
            "I mainly care about financial performance",
            "I care about ESG, but finance comes first",
            "I want a balance between finance and ESG",
            "I strongly prioritise responsible investing"
        ],
        key="q4"
    )

    answer_map = {
        0: 0.10,
        1: 0.35,
        2: 0.65,
        3: 1.00
    }

    score = (
        answer_map[
            [
                "Not important",
                "Slightly important",
                "Moderately important",
                "Very important"
            ].index(q1)
        ]
        + answer_map[
            [
                "No, returns come first",
                "Only a little",
                "Yes, to some extent",
                "Yes, definitely"
            ].index(q2)
        ]
        + answer_map[
            [
                "Very little",
                "Somewhat",
                "Quite a lot",
                "A great deal"
            ].index(q3)
        ]
        + answer_map[
            [
                "I mainly care about financial performance",
                "I care about ESG, but finance comes first",
                "I want a balance between finance and ESG",
                "I strongly prioritise responsible investing"
            ].index(q4)
        ]
    )

    lambda_esg = round(score / 4, 2)

    st.success(f"Estimated ESG Preference (λ): {lambda_esg:.2f}")
    st.markdown(
        '<div class="small-note">Higher values mean the investor places more weight on sustainability in the utility function.</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

else:
    lambda_esg = st.sidebar.slider("Manual ESG Preference (λ)", 0.0, 1.0, 0.3, 0.05)

# ---------------------------------
# RUN BUTTON
# ---------------------------------
run_optimization = st.sidebar.button("Optimize Portfolio")

# ---------------------------------
# MAIN LOGIC
# ---------------------------------
if run_optimization:
    weights = np.linspace(0, 1, 1000)

    portfolio_returns = []
    portfolio_risks = []
    portfolio_esg_scores = []
    portfolio_utilities = []

    for w in weights:
        ret = portfolio_ret(w, r1, r2)
        risk = portfolio_sd(w, sd1, sd2, rho)
        esg = portfolio_esg(w, esg1, esg2)
        utility = portfolio_utility(ret, risk, esg, gamma, lambda_esg)

        portfolio_returns.append(ret)
        portfolio_risks.append(risk)
        portfolio_esg_scores.append(esg)
        portfolio_utilities.append(utility)

    portfolio_returns = np.array(portfolio_returns)
    portfolio_risks = np.array(portfolio_risks)
    portfolio_esg_scores = np.array(portfolio_esg_scores)
    portfolio_utilities = np.array(portfolio_utilities)

    best_idx = np.argmax(portfolio_utilities)

    w1_optimal = weights[best_idx]
    w2_optimal = 1 - w1_optimal
    ret_optimal = portfolio_returns[best_idx]
    risk_optimal = portfolio_risks[best_idx]
    esg_optimal = portfolio_esg_scores[best_idx]
    utility_optimal = portfolio_utilities[best_idx]

    if risk_optimal > 0:
        sharpe_optimal = (ret_optimal - r_free) / risk_optimal
    else:
        sharpe_optimal = 0

    weights_table = pd.DataFrame({
        "Asset": [asset1_name, asset2_name],
        "Weight (%)": [round(w1_optimal * 100, 2), round(w2_optimal * 100, 2)],
        "Expected Return (%)": [round(r1 * 100, 2), round(r2 * 100, 2)],
        "Risk (%)": [round(sd1 * 100, 2), round(sd2 * 100, 2)],
        "ESG Rating": [esg1, esg2]
    })

    if esg_optimal >= 75:
        esg_label = "high sustainability orientation"
    elif esg_optimal >= 60:
        esg_label = "balanced sustainability profile"
    else:
        esg_label = "return-oriented sustainability profile"

    summary_text = (
        f"The app recommends allocating {w1_optimal*100:.2f}% to {asset1_name} and "
        f"{w2_optimal*100:.2f}% to {asset2_name}. This portfolio has an expected return "
        f"of {ret_optimal*100:.2f}%, risk of {risk_optimal*100:.2f}%, and an ESG score "
        f"of {esg_optimal:.2f}. Based on your risk aversion and ESG preference, this is "
        f"the portfolio with the highest utility and a {esg_label}."
    )

    tab1, tab2, tab3 = st.tabs(["📊 Results", "📈 Visualisation", "🧠 Preference Profile"])

    # ---------------------------------
    # TAB 1 - RESULTS
    # ---------------------------------
    with tab1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Recommended Portfolio")
        st.info(summary_text)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Expected Return", f"{ret_optimal*100:.2f}%")
        col2.metric("Risk", f"{risk_optimal*100:.2f}%")
        col3.metric("ESG Score", f"{esg_optimal:.2f}")
        col4.metric("Utility", f"{utility_optimal:.4f}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Recommended Weights")
        st.dataframe(weights_table, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Performance Snapshot")
        perf1, perf2, perf3 = st.columns(3)
        perf1.metric("Sharpe Ratio", f"{sharpe_optimal:.3f}")
        perf2.metric("Risk Aversion (γ)", f"{gamma:.2f}")
        perf3.metric("ESG Preference (λ)", f"{lambda_esg:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------
    # TAB 2 - GRAPH
    # ---------------------------------
    with tab2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Portfolio Frontier")

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("#fbfffc")

        ax.plot(
            portfolio_risks,
            portfolio_returns,
            color="#2e7d32",
            linewidth=2.8,
            label="Portfolio Frontier"
        )

        ax.scatter(
            sd1,
            r1,
            color="#81c784",
            s=130,
            label=asset1_name,
            zorder=5
        )

        ax.scatter(
            sd2,
            r2,
            color="#388e3c",
            s=130,
            label=asset2_name,
            zorder=5
        )

        ax.scatter(
            risk_optimal,
            ret_optimal,
            color="#1b5e20",
            s=220,
            marker="D",
            label="Recommended Portfolio",
            zorder=6
        )

        ax.scatter(
            0,
            r_free,
            color="#a5d6a7",
            s=130,
            marker="s",
            label="Risk-Free Asset",
            zorder=5
        )

        ax.set_title("Risk-Return Frontier", fontsize=14, color="#1b5e20", fontweight="bold")
        ax.set_xlabel("Risk (Standard Deviation)")
        ax.set_ylabel("Expected Return")

        ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

        ax.grid(True, alpha=0.25)
        ax.legend(frameon=True)

        st.pyplot(fig)

        st.caption(
            "The dark green diamond shows the recommended portfolio that maximizes utility "
            "based on both financial and ESG preferences."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------
    # TAB 3 - PREFERENCE PROFILE
    # ---------------------------------
    with tab3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("Investor Preference Profile")

        if lambda_esg >= 0.75:
            pref_text = "Strongly sustainability-focused investor"
        elif lambda_esg >= 0.50:
            pref_text = "Balanced investor with meaningful ESG interest"
        elif lambda_esg >= 0.25:
            pref_text = "Moderately ESG-aware investor"
        else:
            pref_text = "Primarily financially focused investor"

        st.write(f"**Investor Type:** {pref_text}")
        st.write(f"**Estimated ESG Preference (λ):** {lambda_esg:.2f}")
        st.write(f"**Risk Aversion (γ):** {gamma:.2f}")

        profile_df = pd.DataFrame({
            "Preference Dimension": ["Risk Aversion", "ESG Preference"],
            "Value": [gamma, lambda_esg]
        })
        st.dataframe(profile_df, use_container_width=True)

        st.markdown(
            '<div class="small-note">This profile helps explain why the optimizer selected the final portfolio.</div>',
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("How to use this app")
    st.write("1. Enter two assets and their financial/ESG characteristics in the sidebar.")
    st.write("2. Choose your risk aversion level.")
    st.write("3. Either complete the ESG quiz or set ESG preference manually.")
    st.write("4. Click **Optimize Portfolio** to generate your recommended allocation.")
    st.markdown("</div>", unsafe_allow_html=True)


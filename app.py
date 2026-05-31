import os
from kz_simulator import generate_all_profiles

# Generate KZ data if not exists
if not os.path.exists('kz_transactions.csv'):
    generate_all_profiles(months=12)






import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from groq import Groq
import os
from dotenv import load_dotenv

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="PFM AI Assistant",
    page_icon="💰",
    layout="wide"
)

# ── Groq client ───────────────────────────────────────────
load_dotenv()
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# ── Load data ─────────────────────────────────────────────
@st.cache_data
def load_data(source):
    if source == '🇰🇿 Kazakhstan (Simulated)':
        if not os.path.exists('kz_transactions.csv'):
            from kz_simulator import generate_all_profiles
            generate_all_profiles(months=12)
        df = pd.read_csv('kz_transactions.csv', parse_dates=['DATE'])
    else:
        df = pd.read_csv('bank_transactions_clean.csv', parse_dates=['DATE'])
    return df

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

data_source = st.sidebar.radio(
    "📂 Dataset",
    ['🇰🇿 Kazakhstan (Simulated)', '🇮🇳 India (Real)']
)

currency = '₸' if '🇰🇿' in data_source else '₹'
df = load_data(data_source)

accounts = ['All'] + sorted(df['Account No'].unique().tolist())
selected_account = st.sidebar.selectbox("Select Account", accounts)

min_date = df['DATE'].min()
max_date = df['DATE'].max()
start_date, end_date = st.sidebar.date_input(
    "Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

trans_type = st.sidebar.radio(
    "Transaction Type",
    ['All', 'DEBIT', 'CREDIT']
)

# ── Apply filters ─────────────────────────────────────────
filtered = df.copy()

if selected_account != 'All':
    filtered = filtered[filtered['Account No'] == selected_account]

filtered = filtered[
    (filtered['DATE'] >= pd.Timestamp(start_date)) &
    (filtered['DATE'] <= pd.Timestamp(end_date))
]

if trans_type != 'All':
    filtered = filtered[filtered['TYPE'] == trans_type]

# ── Header ────────────────────────────────────────────────
st.title("💰 Personal Finance Manager")
if '🇰🇿' in data_source:
    st.caption("AI-powered spending insights | Kaspi-style PFM analytics 🇰🇿")
else:
    st.caption("AI-powered spending insights for your bank transactions 🇮🇳")

# ── KPI Cards ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_income = filtered[filtered['TYPE'] == 'CREDIT']['AMOUNT'].sum()
total_spent = abs(filtered[filtered['TYPE'] == 'DEBIT']['AMOUNT'].sum())
net_balance = total_income - total_spent
total_tx = len(filtered)

with col1:
    st.metric("💵 Total Income", f"{currency}{total_income:,.0f}")
with col2:
    st.metric("💸 Total Spent", f"{currency}{total_spent:,.0f}")
with col3:
    st.metric(
        "📊 Net Balance",
        f"{currency}{net_balance:,.0f}",
        delta=f"{'Positive' if net_balance > 0 else 'Negative'}"
    )
with col4:
    st.metric("🔢 Transactions", f"{total_tx:,}")

st.divider()

# ── Charts Row 1 ──────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Spending by Category")
    debit_by_cat = (
        filtered[filtered['TYPE'] == 'DEBIT']
        .groupby('CATEGORY')['AMOUNT']
        .sum()
        .abs()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig_pie = px.pie(
        debit_by_cat,
        values='AMOUNT',
        names='CATEGORY',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("📈 Monthly Spending Trend")
    filtered['MONTH'] = filtered['DATE'].dt.to_period('M').astype(str)
    monthly = (
        filtered[filtered['TYPE'] == 'DEBIT']
        .groupby('MONTH')['AMOUNT']
        .sum()
        .abs()
        .reset_index()
    )
    fig_line = px.line(
        monthly,
        x='MONTH',
        y='AMOUNT',
        markers=True,
        color_discrete_sequence=['#FF6B6B']
    )
    fig_line.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_line, use_container_width=True)

# ── Charts Row 2 ──────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Income vs Expenses by Month")
    monthly_flow = filtered.groupby(
        [filtered['DATE'].dt.to_period('M').astype(str), 'TYPE']
    )['AMOUNT'].sum().abs().reset_index()
    monthly_flow.columns = ['MONTH', 'TYPE', 'AMOUNT']
    fig_bar = px.bar(
        monthly_flow,
        x='MONTH',
        y='AMOUNT',
        color='TYPE',
        barmode='group',
        color_discrete_map={
            'CREDIT': '#2ECC71',
            'DEBIT': '#E74C3C'
        }
    )
    fig_bar.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Spending Categories")
    top_cats = (
        filtered[filtered['TYPE'] == 'DEBIT']
        .groupby('CATEGORY')['AMOUNT']
        .sum()
        .abs()
        .sort_values(ascending=True)
        .tail(10)
        .reset_index()
    )
    fig_h = px.bar(
        top_cats,
        x='AMOUNT',
        y='CATEGORY',
        orientation='h',
        color='AMOUNT',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_h, use_container_width=True)

st.divider()

# ── Recent Transactions ───────────────────────────────────
st.subheader("📋 Recent Transactions")
recent = (
    filtered
    .sort_values('DATE', ascending=False)
    .head(20)[['DATE', 'TRANSACTION DETAILS', 'CATEGORY', 'TYPE', 'AMOUNT']]
)
st.dataframe(recent, use_container_width=True)

st.divider()

st.divider()

# ── Budget Tracker ────────────────────────────────────────
st.subheader("🎯 Budget Tracker")
st.caption("Set monthly limits per category and track your progress")

from budget_tracker import (load_budgets, save_budgets,
                             calculate_spending_vs_budget)

budgets = load_budgets()

# ── Budget Setup ──────────────────────────────────────────
with st.expander("⚙️ Set Monthly Budgets", expanded=False):
    st.write("Set your monthly spending limit for each category:")

    # Get all real categories
    real_categories = [
        c for c in filtered['CATEGORY'].unique()
        if c not in ['Transfer', 'ATM & Cash', 'Other']
    ]

    cols = st.columns(2)
    new_budgets = {}

    for i, category in enumerate(sorted(real_categories)):
        with cols[i % 2]:
            current_budget = budgets.get(category, 0)
            new_budget = st.number_input(
                f"{category}",
                min_value=0,
                max_value=10_000_000,
                value=int(current_budget),
                step=1000,
                key=f"budget_{category}"
            )
            if new_budget > 0:
                new_budgets[category] = new_budget

    if st.button("💾 Save Budgets", type="primary"):
        save_budgets(new_budgets)
        st.success("✅ Budgets saved!")
        st.rerun()

# ── Budget vs Actual ──────────────────────────────────────
if budgets:
    budget_df = calculate_spending_vs_budget(
        filtered, budgets, currency
    )

    if not budget_df.empty:

        # Summary KPIs
        over_budget = budget_df[
            budget_df['Status'] == '🔴 Over Budget'
        ]
        on_track = budget_df[
            budget_df['Status'].isin(['🟢 Good', '🟡 On Track'])
        ]

        b1, b2, b3 = st.columns(3)
        with b1:
            st.metric(
                "🔴 Over Budget",
                len(over_budget),
                delta=f"{len(over_budget)} categories need attention"
                if len(over_budget) > 0 else "All good!"
            )
        with b2:
            st.metric("🟢 On Track", len(on_track))
        with b3:
            total_budget = budget_df['Budget'].sum()
            total_actual = budget_df['Actual'].sum()
            overall_pct = (
                total_actual / total_budget * 100
                if total_budget > 0 else 0
            )
            st.metric(
                "📊 Overall Budget Used",
                f"{overall_pct:.1f}%",
                delta=f"{currency}{total_actual:,.0f} of {currency}{total_budget:,.0f}"
            )

        st.subheader("📊 Budget Progress by Category")

        # Progress bars for each category
        for _, row in budget_df.iterrows():
            if row['Budget'] > 0:
                col1, col2 = st.columns([3, 1])

                with col1:
                    pct = min(row['Used %'], 100)
                    color = (
                        'red' if row['Used %'] > 100 else
                        'orange' if row['Used %'] > 80 else
                        'green'
                    )
                    st.write(f"**{row['Category']}** {row['Status']}")
                    st.progress(pct / 100)

                with col2:
                    st.write(
                        f"{currency}{row['Actual']:,.0f} / "
                        f"{currency}{row['Budget']:,.0f}"
                    )
                    if row['Remaining'] >= 0:
                        st.caption(
                            f"✅ {currency}{row['Remaining']:,.0f} left"
                        )
                    else:
                        st.caption(
                            f"❌ {currency}{abs(row['Remaining']):,.0f} over!"
                        )

        # Full table
        st.subheader("📋 Budget Summary Table")
        display_df = budget_df.copy()
        display_df['Budget'] = display_df['Budget'].apply(
            lambda x: f"{currency}{x:,.0f}"
        )
        display_df['Actual'] = display_df['Actual'].apply(
            lambda x: f"{currency}{x:,.0f}"
        )
        display_df['Remaining'] = display_df['Remaining'].apply(
            lambda x: f"{currency}{x:,.0f}"
        )
        display_df['Used %'] = display_df['Used %'].apply(
            lambda x: f"{x:.1f}%"
        )
        st.dataframe(display_df, use_container_width=True)

else:
    st.info(
        "👆 Click **Set Monthly Budgets** above to set your spending limits!"
    )

# ── Anomaly Detection ─────────────────────────────────────
st.subheader("🚨 Anomaly Detection")
st.caption("Automatically flags suspicious transactions using Z-Score, Velocity Check and pattern analysis")

from anomaly_detector import detect_anomalies, get_anomaly_summary

sensitivity = st.slider(
    "Detection Sensitivity",
    min_value=1.0,
    max_value=4.0,
    value=2.0,
    step=0.5,
    help="Lower = more sensitive (more flags), Higher = less sensitive (fewer flags)"
)

if st.button("🔍 Detect Anomalies", type="secondary"):
    with st.spinner("Scanning transactions for suspicious patterns..."):

        df_anomalies = detect_anomalies(filtered, sensitivity=sensitivity)
        summary = get_anomaly_summary(df_anomalies)

        st.subheader("📊 Detection Summary")
        a1, a2, a3, a4 = st.columns(4)

        with a1:
            st.metric(
                "🚨 Total Flagged",
                summary['total_anomalies'],
                delta=f"{summary['anomaly_rate']:.1f}% of transactions"
            )
        with a2:
            st.metric("🔴 High Risk", summary['high_risk'])
        with a3:
            st.metric("🟠 Medium Risk", summary['medium_risk'])
        with a4:
            st.metric("🟡 Low Risk", summary['low_risk'])

        st.warning(
            f"⚠️ Total amount in flagged transactions: "
            f"**{currency}{summary['total_anomaly_amount']:,.0f}**"
        )

        # Scatter chart
        st.subheader("📈 Normal vs Anomalous Transactions")
        df_anomalies['STATUS'] = df_anomalies['ANOMALY'].map(
            {True: '🚨 Anomaly', False: '✅ Normal'}
        )
        fig_scatter = px.scatter(
            df_anomalies[df_anomalies['TYPE'] == 'DEBIT'],
            x='DATE',
            y='AMOUNT',
            color='STATUS',
            color_discrete_map={
                '🚨 Anomaly': '#E74C3C',
                '✅ Normal': '#2ECC71'
            },
            hover_data=['TRANSACTION DETAILS', 'CATEGORY',
                        'RISK_LEVEL', 'ANOMALY_REASON'],
            title='Transaction Timeline — Anomalies Highlighted'
        )
        fig_scatter.update_traces(marker=dict(size=8, opacity=0.7))
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Flagged transactions table
        st.subheader("🔴 Flagged Transactions")
        flagged = (
             df_anomalies[df_anomalies['ANOMALY'] == True]
            [['DATE', 'TRANSACTION DETAILS', 'CATEGORY',
            'AMOUNT', 'RISK_LEVEL', 'ANOMALY_REASON']]
             .head(20)
        )
        

        if len(flagged) > 0:
            st.dataframe(flagged, use_container_width=True)
        else:
            st.success("✅ No anomalies detected at this sensitivity level!")

st.divider()

# ── Spending Forecast ─────────────────────────────────────
st.subheader("🔮 Spending Forecast — Next 3 Months")
st.caption("Prophet ML model predicts future spending based on historical patterns")

from forecaster import (prepare_forecast_data, run_forecast,
                        build_forecast_chart, get_forecast_insights)

forecast_categories = ['All Categories'] + [
    c for c in filtered['CATEGORY'].unique()
    if c not in ['Transfer', 'ATM & Cash', 'Other']
]
selected_forecast_cat = st.selectbox(
    "Forecast for category:",
    forecast_categories
)

if st.button("🔮 Run Forecast", type="secondary"):
    with st.spinner("Training Prophet model on your spending history..."):

        monthly_data = prepare_forecast_data(
            filtered, category=selected_forecast_cat
        )

        if len(monthly_data) < 3:
            st.warning("⚠️ Need at least 3 months of history for forecast.")
        else:
            model, forecast = run_forecast(monthly_data, periods=3)

            if forecast is not None:
                fig_forecast = build_forecast_chart(
                    monthly_data, forecast, currency
                )
                st.plotly_chart(fig_forecast, use_container_width=True)

                insights = get_forecast_insights(
                    monthly_data, forecast, currency
                )

                if insights:
                    st.subheader("📊 Forecast Summary")
                    fc1, fc2, fc3 = st.columns(3)

                    with fc1:
                        st.metric(
                            f"🗓️ {insights['next_month_date']}",
                            f"{currency}{insights['next_month_predicted']:,.0f}",
                            delta=f"{insights['pct_change']:+.1f}% vs avg"
                        )
                    with fc2:
                        st.metric(
                            "📉 Lower Bound (80%)",
                            f"{currency}{insights['next_month_lower']:,.0f}"
                        )
                    with fc3:
                        st.metric(
                            "📈 Upper Bound (80%)",
                            f"{currency}{insights['next_month_upper']:,.0f}"
                        )

                    if insights['trend'] == 'increasing':
                        st.warning(
                            f"⚠️ **Spending is trending UP** — "
                            f"next month predicted {insights['pct_change']:+.1f}% "
                            f"above your average of "
                            f"{currency}{insights['avg_actual']:,.0f}."
                        )
                    elif insights['trend'] == 'decreasing':
                        st.success(
                            f"✅ **Spending is trending DOWN** — "
                            f"next month predicted {insights['pct_change']:+.1f}% "
                            f"below your average. Great financial discipline!"
                        )
                    else:
                        st.info(
                            f"📊 **Spending is STABLE** — "
                            f"next month predicted around "
                            f"{currency}{insights['next_month_predicted']:,.0f}."
                        )

st.divider()

# ── AI Financial Advisor ──────────────────────────────────
st.subheader("🤖 AI Financial Advisor")
if '🇰🇿' in data_source:
    st.caption("Powered by Llama 3 — analyzing your spending in Kazakhstani Tenge (₸) context")
else:
    st.caption("Powered by Llama 3 — analyzes your spending and gives personalized advice")

if st.button("💡 Generate AI Insights", type="primary"):
    with st.spinner("Analyzing your spending patterns..."):

        EXCLUDE_CATEGORIES = ['Transfer', 'ATM & Cash', 'Other']
        real_spending = filtered[
            (filtered['TYPE'] == 'DEBIT') &
            (~filtered['CATEGORY'].isin(EXCLUDE_CATEGORIES))
        ]

        debit_summary = (
            real_spending
            .groupby('CATEGORY')['AMOUNT']
            .agg(['sum', 'count'])
            .abs()
            .round(2)
            .reset_index()
        )
        debit_summary.columns = ['Category', 'Total Spent', 'Transactions']
        debit_summary = debit_summary.sort_values('Total Spent', ascending=False)

        real_total_spent = real_spending['AMOUNT'].abs().sum()
        savings_rate = (
            (total_income - real_total_spent) / total_income * 100
            if total_income > 0 else 0
        )

        top_merchant = (
            real_spending
            .groupby('TRANSACTION DETAILS')['AMOUNT']
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(3)
            .reset_index()
        )

        if '🇰🇿' in data_source:
            context = "Kazakhstan (₸ Tenge)"
            bank_context = "Kaspi Bank, Halyk Bank, Freedom Bank, Jusan Bank"
            local_tips = """
Local context for Kazakhstan:
- Average salary in Almaty: ₸350,000-500,000/month
- Kaspi RED card is widely used for installments
- Popular delivery: Glovo, Wolt
- Popular transport: inDrive, Yandex Go
"""
        else:
            context = "India (₹ Rupee)"
            bank_context = "SBI, HDFC, ICICI, Axis Bank"
            local_tips = ""

        prompt = f"""You are a personal finance advisor for a {context} bank customer.
Amounts are in {currency}.
Local banks for reference: {bank_context}.
{local_tips}

INCOME: {currency}{total_income:,.0f}
REAL SPENDING (excl. transfers & ATM): {currency}{real_total_spent:,.0f}
NET BALANCE: {currency}{net_balance:,.0f}
SAVINGS RATE: {savings_rate:.1f}%
TOTAL TRANSACTIONS: {total_tx}
SELECTED ACCOUNT: {selected_account}

SPENDING BY CATEGORY (real expenses only):
{debit_summary.to_string(index=False)}

TOP 3 MERCHANTS BY SPENDING:
{top_merchant.to_string(index=False)}

Please provide:
1. 📊 SPENDING ANALYSIS — key observations
2. ⚠️ WARNING SIGNS — concerning patterns
3. 💡 TOP 3 RECOMMENDATIONS — specific actionable advice
4. 🎯 SAVINGS GOAL — realistic monthly target

Be specific with numbers. Keep concise and practical."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert personal finance advisor for {context}. Give specific actionable advice based on real transaction data."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )

        insight = response.choices[0].message.content

        st.success("✅ Analysis complete!")
        st.markdown(insight)

        st.subheader("💰 Savings Rate")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=savings_rate,
            title={'text': "Savings Rate %"},
            delta={'reference': 20},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#2ECC71"},
                'steps': [
                    {'range': [0, 10], 'color': "#E74C3C"},
                    {'range': [10, 20], 'color': "#F39C12"},
                    {'range': [20, 100], 'color': "#2ECC71"}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 20
                }
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("🎯 Financial advisors recommend saving at least 20% of income")
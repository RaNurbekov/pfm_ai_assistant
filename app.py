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
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Load data ─────────────────────────────────────────────
@st.cache_data
def load_data(source):
    if source == '🇰🇿 Kazakhstan (Simulated)':
        df = pd.read_csv('kz_transactions.csv', parse_dates=['DATE'])
    else:
        df = pd.read_csv('bank_transactions_clean.csv', parse_dates=['DATE'])
    return df

# ── Sidebar ───────────────────────────────────────────────
st.sidebar.title("🔍 Filters")

# Dataset selector
data_source = st.sidebar.radio(
    "📂 Dataset",
    ['🇰🇿 Kazakhstan (Simulated)', '🇮🇳 India (Real)']
)

# Currency based on dataset
currency = '₸' if '🇰🇿' in data_source else '₹'

# Load data
df = load_data(data_source)

# Account selector
accounts = ['All'] + sorted(df['Account No'].unique().tolist())
selected_account = st.sidebar.selectbox("Select Account", accounts)

# Date range
min_date = df['DATE'].min()
max_date = df['DATE'].max()
start_date, end_date = st.sidebar.date_input(
    "Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Transaction type
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
    st.caption("AI-powered spending insights | Powered by Kaspi-style PFM analytics 🇰🇿")
else:
    st.caption("AI-powered spending insights for your bank transactions 🇮🇳")

# ── KPI Cards ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_income = filtered[filtered['TYPE'] == 'CREDIT']['AMOUNT'].sum()
total_spent = abs(filtered[filtered['TYPE'] == 'DEBIT']['AMOUNT'].sum())
net_balance = total_income - total_spent
total_tx = len(filtered)

with col1:
    st.metric("💵 Total Income",
              f"{currency}{total_income:,.0f}")
with col2:
    st.metric("💸 Total Spent",
              f"{currency}{total_spent:,.0f}")
with col3:
    st.metric("📊 Net Balance",
              f"{currency}{net_balance:,.0f}",
              delta=f"{'Positive' if net_balance > 0 else 'Negative'}")
with col4:
    st.metric("🔢 Transactions",
              f"{total_tx:,}")

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
recent = (filtered
          .sort_values('DATE', ascending=False)
          .head(20)[['DATE', 'TRANSACTION DETAILS',
                      'CATEGORY', 'TYPE', 'AMOUNT']])
st.dataframe(recent, use_container_width=True)

st.divider()

# ── AI Insights ───────────────────────────────────────────
st.subheader("🤖 AI Financial Advisor")
if '🇰🇿' in data_source:
    st.caption("Powered by Llama 3 — analyzing your spending in Kazakhstani Tenge (₸) context")
else:
    st.caption("Powered by Llama 3 — analyzes your spending and gives personalized advice")

if st.button("💡 Generate AI Insights", type="primary"):
    with st.spinner("Analyzing your spending patterns..."):

        # ── Exclude non-real spending ─────────────────────
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

        savings_rate = ((total_income - real_total_spent) / total_income * 100
                        if total_income > 0 else 0)

        top_merchant = (
            real_spending
            .groupby('TRANSACTION DETAILS')['AMOUNT']
            .sum()
            .abs()
            .sort_values(ascending=False)
            .head(3)
            .reset_index()
        )

        # ── Context based on dataset ──────────────────────
        if '🇰🇿' in data_source:
            context = "Kazakhstan (₸ Tenge)"
            bank_context = "Kaspi Bank, Halyk Bank, Freedom Bank, Jusan Bank"
            local_tips = """
Local context for Kazakhstan:
- Average salary in Almaty: ₸350,000-500,000/month
- Kaspi RED card is widely used for installments
- Common apps: Kaspi.kz, Halyk Home, Freedom Bank
- Popular delivery: Glovo, Wolt
- Popular transport: inDrive, Yandex Go
"""
        else:
            context = "India (₹ Rupee)"
            bank_context = "SBI, HDFC, ICICI, Axis Bank"
            local_tips = ""

        # ── Build prompt ───────────────────────────────────
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
1. 📊 SPENDING ANALYSIS — key observations about spending patterns
2. ⚠️ WARNING SIGNS — any concerning patterns (overspending, unusual activity)
3. 💡 TOP 3 RECOMMENDATIONS — specific actionable advice to save money
4. 🎯 SAVINGS GOAL — suggest a realistic monthly savings target

Be specific with numbers. Keep response concise and practical.
Format with clear sections and bullet points."""

        # ── Call Llama 3 ───────────────────────────────────
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert personal finance advisor for {context}. Give specific, actionable advice based on real transaction data."
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

        # ── Display insights ───────────────────────────────
        st.success("✅ Analysis complete!")
        st.markdown(insight)

        # ── Savings rate gauge ─────────────────────────────
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
        st.caption("Target: Save at least 20% of income every month")
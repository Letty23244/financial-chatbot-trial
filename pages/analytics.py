import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("📊 Transaction Analytics")

# ─── Load data safely ───
@st.cache_data
def load_data():
    df = pd.read_csv("aml_practice_dataset.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df = load_data()

# ─── Auto-detect columns ───
fraud_col  = next((c for c in ["is_laundering", "is_fraud", "fraud", "label"] if c in df.columns), None)
amount_col = next((c for c in ["amount", "amount_paid", "transaction_amount"] if c in df.columns), None)
type_col   = next((c for c in ["transaction_type", "type", "payment_format"] if c in df.columns), None)
hour_col   = next((c for c in ["hour", "transaction_hour"] if c in df.columns), None)
currency_col = next((c for c in ["currency", "payment_currency", "currency_type"] if c in df.columns), None)

# ─── Sidebar filters ───
st.sidebar.header("🔧 Filters")

if fraud_col:
    show_fraud = st.sidebar.multiselect(
        "Transaction Label",
        options=[0, 1],
        default=[0, 1],
        format_func=lambda x: "🚨 Suspicious" if x == 1 else "✅ Normal"
    )
    df = df[df[fraud_col].isin(show_fraud)]

if amount_col:
    max_amt = float(df[amount_col].max())
    min_amt = float(df[amount_col].min())
    amt_range = st.sidebar.slider(
        "Amount Range",
        min_value=min_amt,
        max_value=max_amt,
        value=(min_amt, max_amt)
    )
    df = df[df[amount_col].between(*amt_range)]

st.sidebar.markdown(f"**Showing:** {len(df):,} transactions")

# ─── Top KPI metrics ───
st.subheader("📈 Overview")

col1, col2, col3, col4 = st.columns(4)

total = len(df)
fraud_count  = int(df[fraud_col].sum())  if fraud_col  else 0
avg_amount   = df[amount_col].mean()     if amount_col else 0
total_amount = df[amount_col].sum()      if amount_col else 0

col1.metric("Total Transactions", f"{total:,}")
col2.metric("Suspicious",         f"{fraud_count:,}",
            delta=f"{fraud_count/total*100:.1f}% rate" if total else None,
            delta_color="inverse")
col3.metric("Avg Amount",         f"{avg_amount:,.2f}")
col4.metric("Total Volume",       f"{total_amount:,.0f}")

st.divider()

# ─── Row 1: Transaction Types + Fraud Split ───
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("🔄 Transaction Types")
    if type_col:
        type_counts = df[type_col].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        fig = px.bar(type_counts, x="Type", y="Count",
                     color="Count", color_continuous_scale="Blues",
                     text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transaction type column found.")

with col_b:
    st.subheader("🔴 Fraud vs Normal")
    if fraud_col:
        fraud_counts = df[fraud_col].value_counts().reset_index()
        fraud_counts.columns = ["Label", "Count"]
        fraud_counts["Label"] = fraud_counts["Label"].map({0: "✅ Normal", 1: "🚨 Suspicious"})
        fig = px.pie(fraud_counts, names="Label", values="Count",
                     color_discrete_sequence=["#2ecc71", "#e74c3c"],
                     hole=0.4)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No fraud label column found.")

# ─── Row 2: Amount Distribution + Currency ───
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("💰 Amount Distribution")
    if amount_col:
        fig = px.histogram(df, x=amount_col, nbins=50,
                           color_discrete_sequence=["#3498db"])
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No amount column found.")

with col_d:
    st.subheader("💱 Currency Breakdown")
    if currency_col:
        curr_counts = df[currency_col].value_counts().reset_index()
        curr_counts.columns = ["Currency", "Count"]
        fig = px.bar(curr_counts, x="Currency", y="Count",
                     color="Count", color_continuous_scale="Purples",
                     text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No currency column found.")

# ─── Row 3: Fraud by Hour + Amount by Type ───
col_e, col_f = st.columns(2)

with col_e:
    st.subheader("🕐 Suspicious Transactions by Hour")
    if hour_col and fraud_col:
        hourly = df.groupby(hour_col)[fraud_col].sum().reset_index()
        hourly.columns = ["Hour", "Suspicious Count"]
        fig = px.bar(hourly, x="Hour", y="Suspicious Count",
                     color="Suspicious Count", color_continuous_scale="Reds")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Hour or fraud column not found.")

with col_f:
    st.subheader("💸 Avg Amount by Transaction Type")
    if type_col and amount_col:
        avg_by_type = df.groupby(type_col)[amount_col].mean().reset_index()
        avg_by_type.columns = ["Type", "Avg Amount"]
        fig = px.bar(avg_by_type, x="Type", y="Avg Amount",
                     color="Avg Amount", color_continuous_scale="Greens",
                     text_auto=".2f")
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Transaction type or amount column not found.")

# ─── Top suspicious transactions table ───
st.divider()
st.subheader("🚨 Top 10 Highest-Amount Suspicious Transactions")

if fraud_col and amount_col:
    top_fraud = (
        df[df[fraud_col] == 1]
        .sort_values(amount_col, ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    if len(top_fraud) > 0:
        st.dataframe(top_fraud, use_container_width=True)
    else:
        st.info("No suspicious transactions in current filter.")
else:
    st.info("Fraud or amount column not detected.")

# ─── Download filtered data ───
st.divider()
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_transactions.csv",
    mime="text/csv"
)
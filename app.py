import os
import sys
import streamlit as st
import pandas as pd

# ─── MUST be the very first Streamlit call ───
st.set_page_config(
    page_title="AI Financial Assistant",
    page_icon="🏦",
    layout="wide"
)

# ─── Custom CSS ───
st.markdown("""
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: white;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #1c1f26;
        border: 1px solid #2a2d35;
        padding: 15px;
        border-radius: 12px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }

    .stButton>button:hover {
        background-color: #45a049;
    }

    /* Input box */
    input {
        border-radius: 10px !important;
    }

    /* Titles */
    h1, h2, h3 {
        color: #ffffff;
    }

    </style>
""", unsafe_allow_html=True)

# ─── Import chatbot ───
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pages.chatbot import FinancialChatbot

# ─── Load data ───
@st.cache_data
def load_data():
    df = pd.read_csv("aml_practice_dataset.csv")
    # Normalize column names (strip spaces, lowercase)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df = load_data()

# ─── Detect fraud/laundering column automatically ───
fraud_col = None
for candidate in ["is_laundering", "is_fraud", "fraud", "laundering", "label"]:
    if candidate in df.columns:
        fraud_col = candidate
        break

# ─── Detect amount column automatically ───
amount_col = None
for candidate in ["amount", "amount_paid", "amount_received", "transaction_amount"]:
    if candidate in df.columns:
        amount_col = candidate
        break

# ─── Init chatbot ───
bot = FinancialChatbot()

# ─── Title ───
st.title("🏦 AI Financial Assistant Dashboard")

# ─── Metrics ───
total_transactions = len(df)
suspicious         = int(df[fraud_col].sum())         if fraud_col  else "N/A"
average_amount     = round(df[amount_col].mean(), 2)  if amount_col else "N/A"

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.metric("📊 Total Transactions", f"{total_transactions:,}")

with col2:
    st.metric("⚠️ Suspicious / Laundering", suspicious)

with col3:
    st.metric("💰 Average Amount", f"{average_amount:,}" if amount_col else "N/A")

# ─── Description ───
st.write("""
This dashboard analyzes financial transactions
and detects suspicious activity using Machine Learning.
""")

# ─── Optional: show raw data ───
with st.expander("📄 View Raw Transaction Data"):
    st.dataframe(df.head(100), use_container_width=True)

# ─── Chatbot section ───
st.divider()
st.subheader("💬 AI Financial Chatbot")

# Keep chat history across reruns using session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display existing chat history
for msg in st.session_state.chat_history:
    st.chat_message(msg["role"]).write(msg["content"])

# Input form
with st.form("chat_form", clear_on_submit=True):
    user_question = st.text_input("Ask a financial question:", placeholder="e.g. What is money laundering?")
    submitted = st.form_submit_button("Ask AI")

if submitted:
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        # Get response
        response = bot.get_response(user_question)

        # Save to history
        st.session_state.chat_history.append({"role": "user",      "content": user_question})
        st.session_state.chat_history.append({"role": "assistant",  "content": response})

        # Show immediately
        st.chat_message("user").write(user_question)
        st.chat_message("assistant").write(response)
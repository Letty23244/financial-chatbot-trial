import streamlit as st
import joblib
import pandas as pd
import os

# ─── Load model safely ───
@st.cache_resource
def load_model():
    path = "aml_model.pkl"
    if not os.path.exists(path):
        return None
    return joblib.load(path)

model = load_model()

# ─── Page header ───
st.title("🔍 Fraud Detection")
st.write("Analyze a single transaction or upload a CSV for bulk detection.")

if model is None:
    st.error("❌ `aml_model.pkl` not found. Please train the model first.")
    st.stop()

# ─── Tabs: Single vs Bulk ───
tab1, tab2 = st.tabs(["🔎 Single Transaction", "📂 Bulk CSV Upload"])


# ════════════════════════════════════════════
# TAB 1 — Single Transaction
# ════════════════════════════════════════════
with tab1:

    with st.form("fraud_form"):
        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input("💰 Amount", min_value=0.0, step=100.0)

            transaction_type = st.selectbox(
                "🔄 Transaction Type",
                options=[0, 1, 2, 3],
                format_func=lambda x: {
                    0: "0 — Cash In",
                    1: "1 — Cash Out",
                    2: "2 — Debit",
                    3: "3 — Transfer"
                }[x]
            )

            hour = st.slider("🕐 Transaction Hour", 0, 23, 12)

        with col2:
            sender_bank = st.selectbox(
                "🏦 Sender Bank",
                options=[0, 1, 2, 3],
                format_func=lambda x: f"Bank {x}"
            )

            receiver_bank = st.selectbox(
                "🏦 Receiver Bank",
                options=[0, 1, 2, 3],
                format_func=lambda x: f"Bank {x}"
            )

            currency = st.selectbox(
                "💱 Currency",
                options=[0, 1, 2, 3],
                format_func=lambda x: {
                    0: "0 — UGX",
                    1: "1 — USD",
                    2: "2 — EUR",
                    3: "3 — KES"
                }[x]
            )

        submitted = st.form_submit_button("🔍 Analyze Transaction", use_container_width=True)

    if submitted:
        sample = pd.DataFrame({
            "amount":           [amount],
            "transaction_type": [transaction_type],
            "sender_bank":      [sender_bank],
            "receiver_bank":    [receiver_bank],
            "currency":         [currency],
            "hour":             [hour],
        })

        try:
            prediction   = model.predict(sample)[0]
            fraud_prob   = model.predict_proba(sample)[0][1]
            legit_prob   = 1 - fraud_prob

            st.divider()

            # ─── Metrics row ───
            c1, c2, c3 = st.columns(3)
            c1.metric("🔴 Fraud Probability",  f"{fraud_prob * 100:.1f}%")
            c2.metric("🟢 Legit Probability",  f"{legit_prob * 100:.1f}%")
            c3.metric("💰 Amount",             f"{amount:,.2f}")

            # ─── Result banner ───
            if prediction == 1:
                st.error(
                    "🚨 **Suspicious Transaction Detected**\n\n"
                    f"This transaction has a **{fraud_prob*100:.1f}% fraud probability**. "
                    "Do not proceed — flag for manual review."
                )
            else:
                st.success(
                    "✅ **Normal Transaction**\n\n"
                    f"Low fraud probability ({fraud_prob*100:.1f}%). Safe to process."
                )

            # ─── Red flags ───
            flags = []
            if amount > 10_000:
                flags.append(f"💰 High amount: **{amount:,.2f}**")
            if hour < 6:
                flags.append(f"🌙 Night-time transaction: **{hour}:00**")
            if sender_bank == receiver_bank:
                flags.append("🔄 Sender and receiver on same bank")
            if transaction_type in [1, 3]:
                flags.append("📤 High-risk transaction type (Cash Out / Transfer)")

            if flags:
                st.subheader("⚠️ Risk Factors")
                for f in flags:
                    st.markdown(f"- {f}")

        except Exception as e:
            st.error(f"❌ Prediction error: {e}")


# ════════════════════════════════════════════
# TAB 2 — Bulk CSV Upload
# ════════════════════════════════════════════
with tab2:
    st.write("Upload a CSV with the same columns used during training.")
    st.caption("Required columns: `amount`, `transaction_type`, `sender_bank`, `receiver_bank`, `currency`, `hour`")

    uploaded = st.file_uploader("📂 Upload CSV", type=["csv"])

    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            st.write(f"Loaded **{len(df):,} transactions**")

            required = ["amount", "transaction_type", "sender_bank", "receiver_bank", "currency", "hour"]
            missing  = [c for c in required if c not in df.columns]

            if missing:
                st.error(f"❌ Missing columns: {missing}")
                st.stop()

            X = df[required]
            df["fraud_probability"] = model.predict_proba(X)[:, 1].round(4)
            df["prediction"]        = model.predict(X)
            df["result"]            = df["prediction"].map({0: "✅ Normal", 1: "🚨 Suspicious"})

            # ─── Summary metrics ───
            total     = len(df)
            n_fraud   = int(df["prediction"].sum())
            fraud_pct = n_fraud / total * 100

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Transactions", f"{total:,}")
            m2.metric("Suspicious Detected", f"{n_fraud:,}")
            m3.metric("Fraud Rate", f"{fraud_pct:.1f}%")

            # ─── Results table ───
            st.subheader("📋 Results")
            st.dataframe(
                df.sort_values("fraud_probability", ascending=False),
                use_container_width=True
            )

            # ─── Download flagged only ───
            flagged = df[df["prediction"] == 1]
            if len(flagged) > 0:
                csv = flagged.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"⬇️ Download {len(flagged)} Flagged Transactions",
                    data=csv,
                    file_name="flagged_transactions.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"❌ Error processing file: {e}")
import streamlit as st
import pandas as pd
import joblib
import os

# ─── Load model safely ───
@st.cache_resource
def load_model():
    path = "fraud_model.pkl"
    if not os.path.exists(path):
        return None
    return joblib.load(path)

model = load_model()

# ─── Page header ───
st.title("🛡️ Risk Assessment (AI Powered)")
st.write("Enter transaction details below to calculate the fraud risk score.")

if model is None:
    st.error("❌ Model file `fraud_model.pkl` not found. Please train the model first.")
    st.stop()

# ─── Input form ───
with st.form("risk_form"):
    st.subheader("📋 Transaction Details")

    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input("💰 Transaction Amount", min_value=0.0, step=100.0,
                                  help="Total amount being transferred")

        transaction_type = st.selectbox(
            "🔄 Transaction Type",
            options=[0, 1, 2, 3],
            format_func=lambda x: {
                0: "0 — Cash In",
                1: "1 — Cash Out",
                2: "2 — Debit",
                3: "3 — Transfer"
            }[x],
            help="Type of financial transaction"
        )

        hour = st.slider("🕐 Transaction Hour", 0, 23, 12,
                         help="Hour of day the transaction occurred (24hr)")

        currency = st.number_input("💱 Currency Type (encoded)", min_value=0, step=1,
                                    help="Encoded currency identifier from your dataset")

    with col2:
        sender_bank   = st.number_input("🏦 Sender Bank ID",   min_value=0, step=1)
        receiver_bank = st.number_input("🏦 Receiver Bank ID", min_value=0, step=1)

        st.markdown("**Origin Account Balances**")
        oldbalanceOrg  = st.number_input("Old Balance (Origin)",  min_value=0.0, step=100.0)
        newbalanceOrig = st.number_input("New Balance (Origin)",  min_value=0.0, step=100.0)

        st.markdown("**Destination Account Balances**")
        oldbalanceDest = st.number_input("Old Balance (Destination)", min_value=0.0, step=100.0)
        newbalanceDest = st.number_input("New Balance (Destination)", min_value=0.0, step=100.0)

    submitted = st.form_submit_button("🔍 Calculate Risk", use_container_width=True)

# ─── Prediction ───
if submitted:
    # Derived features (same as training)
    balance_diff_orig = oldbalanceOrg - newbalanceOrig
    balance_diff_dest = newbalanceDest - oldbalanceDest

    sample = pd.DataFrame({
        "amount":            [amount],
        "transaction_type":  [transaction_type],
        "sender_bank":       [sender_bank],
        "receiver_bank":     [receiver_bank],
        "currency":          [currency],
        "hour":              [hour],
        "oldbalanceOrg":     [oldbalanceOrg],
        "newbalanceOrig":    [newbalanceOrig],
        "oldbalanceDest":    [oldbalanceDest],
        "newbalanceDest":    [newbalanceDest],
    })

    try:
        risk = model.predict_proba(sample)[0][1]

        st.divider()
        st.subheader("📊 Assessment Result")

        # ─── Risk score + gauge ───
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("Risk Score", f"{risk * 100:.2f}%")

        with col_b:
            level = "🔴 HIGH" if risk > 0.7 else "🟡 MEDIUM" if risk > 0.3 else "🟢 LOW"
            st.metric("Risk Level", level)

        with col_c:
            st.metric("Transaction Amount", f"{amount:,.2f}")

        # ─── Risk banner ───
        if risk > 0.7:
            st.error(
                "🚨 **High Risk Transaction Detected**\n\n"
                "This transaction shows strong indicators of fraud. "
                "Do NOT proceed without manual review. Contact your compliance team immediately."
            )
        elif risk > 0.3:
            st.warning(
                "⚠️ **Medium Risk Transaction**\n\n"
                "This transaction has some suspicious characteristics. "
                "Review the details carefully before approving."
            )
        else:
            st.success(
                "✅ **Low Risk — Transaction Appears Safe**\n\n"
                "No strong fraud indicators detected. Standard processing can proceed."
            )

        # ─── Red flags ───
        st.subheader("🔍 Risk Factors Detected")
        flags = []

        if amount > 10_000:
            flags.append(f"💰 Large transaction amount: **{amount:,.2f}**")
        if hour < 6:
            flags.append(f"🌙 Unusual transaction hour: **{hour}:00 (night-time)**")
        if newbalanceOrig == 0 and oldbalanceOrg > 0:
            flags.append("🏦 Origin account fully drained after transaction")
        if balance_diff_orig != amount:
            flags.append("⚖️ Origin balance change doesn't match transaction amount")
        if sender_bank == receiver_bank:
            flags.append("🔄 Sender and receiver use the same bank ID")
        if transaction_type in [1, 3]:
            flags.append("📤 Transaction type is Cash Out or Transfer (higher risk types)")

        if flags:
            for flag in flags:
                st.markdown(f"- {flag}")
        else:
            st.markdown("- No specific red flags identified.")

        # ─── Transaction summary ───
        with st.expander("📄 View Full Transaction Summary"):
            st.dataframe(sample.T.rename(columns={0: "Value"}), use_container_width=True)

    except Exception as e:
        st.error(f"❌ Prediction failed: {e}")
        st.info("Make sure your model was trained with the same features shown above.")
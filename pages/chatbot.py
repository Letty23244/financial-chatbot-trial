import streamlit as st

# ─── Only run Streamlit config when run directly ───
if __name__ == "__main__":
    st.set_page_config(
        page_title="Financial Chatbot",
        page_icon="🤖",
        layout="centered"
    )


# ─────────────────────────────────────────────────────
# CHATBOT LOGIC
# ─────────────────────────────────────────────────────

def chatbot(q: str) -> str:
    q = q.lower()

    if "fraud" in q:
        return (
            "⚠️ **Fraud** refers to unauthorized or suspicious financial activity. "
            "It often involves deception to gain money illegally.\n\n"
            "**Warning signs:**\n"
            "- Transactions at unusual hours (midnight–5 AM)\n"
            "- Large transfers to unknown accounts\n"
            "- Pressure to act quickly\n\n"
            "If you suspect fraud, freeze your account and contact your bank immediately."
        )

    elif "money laundering" in q:
        return (
            "💰 **Money laundering** is the process of hiding illegally obtained money "
            "to make it appear legitimate.\n\n"
            "It typically happens in 3 stages:\n"
            "1. **Placement** — dirty money enters the financial system\n"
            "2. **Layering** — complex transactions hide the trail\n"
            "3. **Integration** — money re-enters the economy appearing clean"
        )

    elif "risk" in q:
        return (
            "📊 **Transaction Risk Levels:**\n\n"
            "- 🟢 **Low (0–30%)** — Normal transaction, safe to process\n"
            "- 🟡 **Medium (30–70%)** — Review carefully before approving\n"
            "- 🔴 **High (70–100%)** — Flag immediately, do not proceed\n\n"
            "Use the **Risk Assessment** page to analyze a specific transaction."
        )

    elif "save money" in q or "saving" in q:
        return (
            "💰 **Saving Tips:**\n\n"
            "- Use the **50/30/20 rule**: 50% needs, 30% wants, 20% savings\n"
            "- Pay yourself first — transfer to savings before spending\n"
            "- Build a 3–6 month emergency fund\n"
            "- Automate savings via standing order\n"
            "- Avoid lifestyle inflation as income grows"
        )

    elif "budget" in q:
        return (
            "📊 **Budgeting Guide:**\n\n"
            "1. List your total monthly income\n"
            "2. List all fixed expenses (rent, utilities, transport)\n"
            "3. Set limits for variable spending (food, entertainment)\n"
            "4. Track every expense for 30 days\n"
            "5. Review and adjust weekly\n\n"
            "💡 Tip: Use the **Analytics** page to see your spending patterns."
        )

    elif "bank" in q or "safe" in q:
        return (
            "🔐 **Banking Safety Tips:**\n\n"
            "- Never share your PIN, OTP, or password with anyone\n"
            "- Always verify the recipient before sending money\n"
            "- Enable transaction alerts on your phone\n"
            "- Use two-factor authentication\n"
            "- Check your balance regularly for unauthorized charges"
        )

    elif "transaction" in q:
        return (
            "💳 **About Transactions:**\n\n"
            "A transaction is the movement of money between accounts. Types include:\n\n"
            "- **Cash In** — depositing money\n"
            "- **Cash Out** — withdrawing money\n"
            "- **Transfer** — sending to another account\n"
            "- **Debit** — payment from your account\n\n"
            "Use the **Fraud Detection** page to analyze any transaction."
        )

    elif "invest" in q:
        return (
            "📈 **Investment Basics:**\n\n"
            "Beginner options:\n"
            "- 🏛️ **Treasury Bills** — low risk, government-backed\n"
            "- 🤝 **Unit Trusts** — pooled, managed investments\n"
            "- 🏘️ **Real estate** — long-term land/property\n"
            "- 📊 **Stocks (USE)** — Uganda Securities Exchange\n\n"
            "⚠️ Never invest money you can't afford to lose. Diversify always."
        )

    elif "loan" in q or "borrow" in q or "debt" in q:
        return (
            "🏦 **Loan Guidance:**\n\n"
            "Before borrowing:\n"
            "- Compare interest rates from multiple lenders\n"
            "- Keep Debt-to-Income ratio below 40%\n"
            "- Understand ALL fees (processing, insurance, penalties)\n\n"
            "Repayment tips:\n"
            "- Pay more than the minimum each month\n"
            "- Pay highest-interest loans first\n"
            "- Never take a new loan to repay another"
        )

    elif "hello" in q or "hi" in q or "hey" in q:
        return (
            "👋 Hello! I'm your **AI Financial Assistant**.\n\n"
            "I can help you with:\n"
            "- 🔍 Fraud detection & suspicious activity\n"
            "- 💰 Budgeting & saving strategies\n"
            "- 📊 Risk analysis & transaction safety\n"
            "- 🏦 Loans, investments & banking tips\n\n"
            "What would you like to know?"
        )

    else:
        return (
            "🤖 I'm not sure about that. Try asking about:\n\n"
            "- **fraud** or **money laundering**\n"
            "- **budgeting** or **saving money**\n"
            "- **risk** or **transactions**\n"
            "- **loans** or **investments**\n"
            "- **banking safety**"
        )


class FinancialChatbot:
    def get_response(self, question: str) -> str:
        return chatbot(question)

    def predict_fraud(self, transaction: dict) -> dict:
        amount   = transaction.get("amount_paid", 0)
        hour     = transaction.get("hour", 12)
        mismatch = transaction.get("currency_mismatch", 0)

        score = 0
        if amount > 10_000: score += 2
        if hour < 6:        score += 2
        if mismatch:        score += 3

        risk = "HIGH" if score >= 5 else "MEDIUM" if score >= 2 else "LOW"
        advice = {
            "LOW":    "✅ Transaction looks normal.",
            "MEDIUM": "⚠️ Review this transaction carefully.",
            "HIGH":   "🚨 High risk! Contact your bank immediately.",
        }
        return {
            "risk_level":        risk,
            "fraud_probability": min(score / 7, 1.0),
            "advice":            advice[risk],
        }


# ─────────────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────────────

SUGGESTED_QUESTIONS = [
    "What is fraud?",
    "How do I save money?",
    "What is money laundering?",
    "How do I create a budget?",
    "What are safe banking tips?",
    "What is a high risk transaction?",
]

def run_streamlit_ui():
    st.title("🤖 AI Financial Assistant")
    st.caption("Ask me anything about fraud, budgeting, risk, or financial safety.")

    # ─── Init session state ───
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hello! I'm your AI Financial Assistant.\n\n"
                    "I can help with fraud detection, budgeting, saving, "
                    "investments, and banking safety.\n\n"
                    "What would you like to know?"
                )
            }
        ]

    # ─── Suggested questions ───
    st.write("**💡 Quick questions:**")
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        if cols[i % 3].button(q, key=f"suggest_{i}", use_container_width=True):
            # Add to messages and respond
            st.session_state.messages.append({"role": "user",      "content": q})
            st.session_state.messages.append({"role": "assistant", "content": chatbot(q)})
            st.rerun()

    st.divider()

    # ─── Chat history ───
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # ─── Input ───
    user_input = st.chat_input("Type your financial question here...")

    if user_input:
        if user_input.strip() == "":
            st.warning("Please enter a question.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)

            response = chatbot(user_input)

            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})

    # ─── Clear chat button ───
    if len(st.session_state.messages) > 1:
        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [st.session_state.messages[0]]
            st.rerun()


if __name__ == "__main__":
    run_streamlit_ui()
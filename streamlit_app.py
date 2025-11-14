import streamlit as st
import json
from agent.agent_v0 import analyze_message

st.set_page_config(page_title="Smart WhatsApp Agent", layout="centered")
st.title("Smart WhatsApp Agent — Chat")
st.write("This chat uses `inputs/warehouse_records.json` for stock lookups. Messages are sent live to the agent; `inputs/messages.json` is not required.")

if "history" not in st.session_state:
    st.session_state.history = []

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here", key="user_input")
    submitted = st.form_submit_button("Send")

if submitted and user_input:
    # Analyze and get reply
    try:
        record = analyze_message(user_input, sender="customer")
    except Exception as e:
        st.error(f"Error invoking agent: {e}")
        record = {"reply": "Sorry, I couldn't process that right now.", "intent": None, "item": None}

    st.session_state.history.append({"sender": "customer", "text": user_input})
    st.session_state.history.append({"sender": "agent", "text": record.get("reply", ""), "intent": record.get("intent"), "item": record.get("item")})
    # Auto-save conversation after each exchange
    def _save_history(path: str = "streamlit_output.json"):
        out = []
        i = 0
        while i < len(st.session_state.history):
            u = st.session_state.history[i]
            b = st.session_state.history[i + 1] if i + 1 < len(st.session_state.history) else {}
            out.append({
                "sender": u.get("sender"),
                "text": u.get("text"),
                "intent": b.get("intent"),
                "item": b.get("item"),
                "reply": b.get("text", "")
            })
            i += 2

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=4, ensure_ascii=False)
        except Exception:
            # Avoid breaking the UI on save errors; show a non-blocking message
            st.warning(f"Could not auto-save conversation to {path}.")

    _save_history()

# Display chat history
for msg in st.session_state.history:
    if msg["sender"] == "customer":
        st.markdown(f"**You:** {msg['text']}")
    else:
        st.markdown(f"**Agent:** {msg['text']}")
        meta = []
        if msg.get("intent"):
            meta.append(f"Intent: {msg.get('intent')}")
        if msg.get("item"):
            meta.append(f"Item: {msg.get('item')}")
        if meta:
            st.caption("  •  ".join(meta))

st.write("---")

# Save conversation
if st.button("Save conversation to `output.json`"):
    out = []
    i = 0
    while i < len(st.session_state.history):
        u = st.session_state.history[i]
        b = st.session_state.history[i + 1] if i + 1 < len(st.session_state.history) else {}
        out.append({
            "sender": u.get("sender"),
            "text": u.get("text"),
            "intent": b.get("intent"),
            "item": b.get("item"),
            "reply": b.get("text", "")
        })
        i += 2

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=4, ensure_ascii=False)

    st.success("Conversation saved to `output.json`")

st.sidebar.header("Info")
st.sidebar.write("- Warehouse data: `inputs/warehouse_records.json`")
st.sidebar.write("- To run: `streamlit run streamlit_app.py`")

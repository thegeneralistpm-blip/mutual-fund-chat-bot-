import streamlit as st
import httpx
import time

import os

# --- Constants & Config ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_URL = f"{BACKEND_URL}/chat"

st.set_page_config(
    page_title="Zerodha MF Assistant",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    # Adding a welcome message by default
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your Zerodha Mutual Fund Assistant. How can I help you today?"}
    ]

# --- Sidebar: User Personalization (Phase 2) ---
with st.sidebar:
    st.header("👤 Auth / Personalization")
    st.markdown("Select a user to simulate their logged-in context.")
    selected_user = st.selectbox(
        "Current User",
        ["Guest (No Auth)", "user_1 (Alice - High Risk)", "user_2 (Bob - Low Risk)"]
    )
    
    # Map selection to actual user_id
    if selected_user.startswith("user_1"):
        user_id = "user_1"
    elif selected_user.startswith("user_2"):
        user_id = "user_2"
    else:
        user_id = None

# --- UI Setup ---
st.title("🛡️ Zerodha MF Assistant")
st.markdown("### Your Zerodha Mutual Fund Guide")
st.markdown("---")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display sources if present
        if "sources" in msg and msg["sources"]:
            st.markdown("**📎 Sources:**")
            for source in msg["sources"]:
                score_pct = int(source['score'] * 100)
                st.caption(f"- {source['fund_name']} ({score_pct}%)")
                
        # Display disclaimer if present
        if "disclaimer" in msg and msg["disclaimer"]:
            st.warning(f"⚠️ {msg['disclaimer']}")

# --- Chat Input ---
if user_query := st.chat_input("Type your question here..."):
    # 1. Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # 2. Add to session state
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # 3. Call API and show loading state
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*(Thinking...)*")
        
        try:
            with httpx.Client(timeout=60.0) as client:
                req_payload = {"query": user_query}
                if user_id:
                    req_payload["user_id"] = user_id
                    
                response = client.post(API_URL, json=req_payload)
                
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer provided.")
                sources = data.get("sources", [])
                disclaimer = data.get("disclaimer", "")
                
                # Display Answer
                message_placeholder.markdown(answer)
                
                # Display Sources
                if sources:
                    st.markdown("**📎 Sources:**")
                    for source in sources:
                        score_pct = int(source['score'] * 100)
                        st.caption(f"- {source['fund_name']} ({score_pct}%)")
                
                # Display Disclaimer
                if disclaimer:
                    st.warning(f"⚠️ {disclaimer}")
                    
                # Append to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "disclaimer": disclaimer
                })
                
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
        except httpx.ConnectError:
            error_msg = "Could not connect to the backend API. Please ensure the server is running on localhost:8000."
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

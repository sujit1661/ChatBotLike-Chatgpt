import streamlit as st
import google.generativeai as genai
import re

# ✅ Secure API key from secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Load the Gemini chat model
model = genai.GenerativeModel("gemini-1.5-pro")
chat_session = model.start_chat(history=[])

# Page configuration
st.set_page_config(page_title="GEN AI-S", page_icon="🤖", layout="centered")

# Title
st.title("🤖 GEN AI Chatbot")

# Initialize chat history if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to extract and format code blocks
def extract_code_blocks(response_text):
    """
    Detects code blocks in the response and separates them.
    Returns a list of (text, is_code) tuples.
    """
    code_blocks = []
    pattern = re.compile(r"```(\w+)?\n(.*?)\n```", re.DOTALL)
    last_index = 0

    for match in pattern.finditer(response_text):
        start, end = match.span()
        lang = match.group(1) or "python"  # Default to Python
        code = match.group(2)

        # Append text before the code block
        if last_index < start:
            code_blocks.append((response_text[last_index:start], False))

        # Append the extracted code block
        code_blocks.append((code, True))
        last_index = end

    # Append any remaining text
    if last_index < len(response_text):
        code_blocks.append((response_text[last_index:], False))

    return code_blocks

# Display previous messages (excluding the latest input)
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]

    with st.chat_message(role):
        for block, is_code in extract_code_blocks(content):
            if is_code:
                st.code(block, language="python")
            else:
                st.markdown(block)

# User input
user_input = st.chat_input("Type your message...")

if user_input and "last_user_input" not in st.session_state:
    # Prevent duplicate input processing
    st.session_state.last_user_input = user_input  

    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(f"**You**: {user_input}")

    # Show thinking message
    with st.chat_message("bot"):
        placeholder = st.empty()
        placeholder.markdown("_GEN AI is thinking..._")

    # Get AI response using chat history
    response = chat_session.send_message(user_input)
    bot_response = response.text.strip()

    # Store bot message
    st.session_state.messages.append({"role": "bot", "content": bot_response})

    # Remove placeholder and show response
    placeholder.empty()
    with st.chat_message("bot"):
        for block, is_code in extract_code_blocks(bot_response):
            if is_code:
                st.code(block, language="python")
            else:
                st.markdown(block)

    # Clear last input tracking to allow the next message
    del st.session_state.last_user_input

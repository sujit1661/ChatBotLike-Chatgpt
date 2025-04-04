import streamlit as st
import google.generativeai as genai
import re

# ✅ Secure API key from secrets (No functionality changed)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# Page configuration
st.set_page_config(page_title="GEN AI Chatbot", page_icon="🤖", layout="centered")

# Title
st.title("🤖 GEN AI Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to detect if response contains code
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

# Display previous messages
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

if user_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(f"**You**: {user_input}")

    # Show thinking message
    with st.chat_message("bot"):
        placeholder = st.empty()
        placeholder.markdown("_GEN AI is thinking..._")

    # Build context from previous messages
    context = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    full_prompt = f"Conversation history:\n{context}\n\nUSER: {user_input}\n\nAnswer based on the full conversation history, maintaining context and referencing previous messages when relevant."

    # Get AI response
    response = model.generate_content(full_prompt)
    bot_response = response.text

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

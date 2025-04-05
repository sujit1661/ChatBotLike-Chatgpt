import streamlit as st
import google.generativeai as genai
import re

# ✅ Must be the first Streamlit command
st.set_page_config(page_title="GEN AI Chatbot", page_icon="🤖", layout="centered")

# ✅ Google Analytics
st.markdown("""
    <!-- Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-28VFMD1H97"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-28VFMD1H97');
    </script>
""", unsafe_allow_html=True)

# ⚠️ API Key (consider using secrets for production)
API_KEY = "AIzaSyBcalMKa-rIwnRGYLWFKOZAaHjl_AJ4HFc"
genai.configure(api_key=API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# Title
st.title("🤖 GEN AI Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to extract code blocks
def extract_code_blocks(response_text):
    code_blocks = []
    pattern = re.compile(r"```(\w+)?\n(.*?)\n```", re.DOTALL)
    last_index = 0

    for match in pattern.finditer(response_text):
        start, end = match.span()
        lang = match.group(1) or "python"
        code = match.group(2)

        if last_index < start:
            code_blocks.append((response_text[last_index:start], False))
        code_blocks.append((code, True))
        last_index = end

    if last_index < len(response_text):
        code_blocks.append((response_text[last_index:], False))

    return code_blocks

# Display past chat
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role):
        for block, is_code in extract_code_blocks(content):
            st.code(block, language="python") if is_code else st.markdown(block)

# Input box
user_input = st.chat_input("Type your message...")

# Track and handle new input
if user_input and (st.session_state.get("last_input") != user_input):
    st.session_state.last_input = user_input  # Prevent duplicate processing

    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"**You:** {user_input}")

    # Show "thinking" message
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_GEN AI is thinking..._")

    # Prepare full prompt with history
    context = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[:-1]])
    prompt = f"Conversation history:\n{context}\n\nUSER: {user_input}\n\nReply as GEN AI while maintaining context."

    # Generate response
    response = model.generate_content(prompt)
    bot_response = response.text.strip()

    placeholder.empty()

    if bot_response:
        # Store and display response
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            for block, is_code in extract_code_blocks(bot_response):
                st.code(block, language="python") if is_code else st.markdown(block)

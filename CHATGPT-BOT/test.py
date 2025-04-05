import streamlit as st
import google.generativeai as genai
import re

# ✅ Inject Google Analytics tracking
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

# ⚠️ Direct API key (For production, use secrets)
API_KEY = "AIzaSyBcalMKa-rIwnRGYLWFKOZAaHjl_AJ4HFc"

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Load the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# Page configuration
st.set_page_config(page_title="GEN AI Chatbot", page_icon="🤖", layout="centered")

# Title
st.title("🤖 GEN AI Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to detect and extract code blocks
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

    # Display user message instantly
    with st.chat_message("user"):
        st.markdown(f"**You:** {user_input}")

    # Show "GEN AI is thinking..." before response appears
    with st.chat_message("GEN AI"):
        placeholder = st.empty()
        placeholder.markdown("_GEN AI is thinking..._")

    # Contextualize conversation history
    context = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[:-1]])
    full_prompt = f"Conversation history:\n{context}\n\nUSER: {user_input}\n\nReply as GEN AI while maintaining context."

    # Generate AI response
    response = model.generate_content(full_prompt)
    bot_response = response.text.strip()  # Ensure no empty responses

    # Remove placeholder and update chat
    placeholder.empty()

    # Store and display bot response
    if bot_response:
        st.session_state.messages.append({"role": "GEN AI", "content": bot_response})

        with st.chat_message("GEN AI"):
            for block, is_code in extract_code_blocks(bot_response):
                if is_code:
                    st.code(block, language="python")
                else:
                    st.markdown(block)

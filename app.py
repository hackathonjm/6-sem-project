import streamlit as st
import os
import json
from datetime import datetime
from student_bot import get_bot_response  # Your AI function here
import speech_recognition as sr
from fpdf import FPDF

st.set_page_config(page_title="Edusphere AI", layout="centered")

# --- Initialize Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_name" not in st.session_state:
    st.session_state.chat_name = "Chat 1"

# --- Load Saved Chats ---
chat_file = "chat_history.json"
if os.path.exists(chat_file):
    with open(chat_file, "r", encoding='utf-8') as f:
        saved_chats = json.load(f)
else:
    saved_chats = {}

# --- Theme Selection ---
with st.sidebar.expander("🎨 Theme", expanded=False):
    theme_option = st.radio("Select Theme", ["Default", "Light Mode", "Dark Mode"], index=0)

def apply_theme(theme_choice):
    if theme_choice == "Dark Mode":
        st.markdown("""
        <style>
        .stApp { background-color: #635985 !important; color: white !important; }
        section[data-testid="stSidebar"] > div { background-color: #18122B !important; color: white !important; }
        section[data-testid="stSidebar"] * { color: white !important; }
        .stButton > button { background-color: #443C68 !important; color: white !important; border-radius: 8px; }
        .stTextInput > div > div > input { background-color: #6D5D6E !important; color: white !important; }
        </style>
        """, unsafe_allow_html=True)

    elif theme_choice == "Light Mode":
        st.markdown("""
        <style>
        .stApp { background-color: #EFD595 !important; color: black !important; }
        section[data-testid="stSidebar"] > div { background-color: #C08261 !important; color: white !important; }
        section[data-testid="stSidebar"] * { color: white !important; }
        .stButton > button { background-color: #9A3B3B !important; color: white !important; border-radius: 8px; }
        .stTextInput > div > div > input { background-color: #EF9595 !important; color: black !important; }
        </style>
        """, unsafe_allow_html=True)

    elif theme_choice == "Default":
        st.markdown("""
        <style>
        .stApp { background-color: #B5A8D5 !important; color: black !important; }
        section[data-testid="stSidebar"] > div { background-color: #211C84 !important; color: white !important; }
        section[data-testid="stSidebar"] * { color: white !important; }
        .stButton > button { background-color: #4D55CC !important; color: white !important; border-radius: 8px; }
        .stTextInput > div > div > input { background-color: #7A73D1 !important; color: white !important; }
        </style>
        """, unsafe_allow_html=True)

apply_theme(theme_option)

# --- Expander Hover Behavior ---
st.markdown("""
    <style>
    .st-expander:hover summary { display: block !important; cursor: pointer; }
    .st-expander summary:focus { display: block !important; }
    .st-expander select { display: none; }
    </style>
""", unsafe_allow_html=True)



# --- Avatar Selection ---
avatar_dict = {
    "Graduate Cap": "🎓",
    "Robot": "🤖",
    "Alien": "👽",
    "Cat": "🐱",
    "Ninja": "🥷"
}

# Options for dropdown display
avatar_display_options = list(avatar_dict.values())
reverse_avatar_dict = {v: k for k, v in avatar_dict.items()}

with st.sidebar.expander("🎭 Pick an Avatar for Bot", expanded=False):
    avatar_choice_display = st.selectbox(
        " ", avatar_display_options, index=None, placeholder="Choose here",
    )


st.markdown("""
    <style>
    div[data-baseweb="select"] > div {
        background-color: transparent !important;
        color: white !important;
        border-radius: 8px;
        padding: 8px;
    }
    div[data-baseweb="select"] svg {
        color: white !important;
    }
    div[data-baseweb="select"] span {
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

if avatar_choice_display:
    avatar_name = reverse_avatar_dict[avatar_choice_display]
    avatar_emoji = avatar_choice_display

# --- New Chat Button ---
with st.sidebar.expander("💬 Chat Options", expanded=True):
    if st.button("➕ New Chat", key="new_chat_button"):
        # Clear the chat history and start a new chat session
        st.session_state.chat_history = []
        st.session_state.chat_name = f"Chat {len(saved_chats) + 1}"  # Unique chat name

        # Save new chat to history
        saved_chats[st.session_state.chat_name] = st.session_state.chat_history
        with open(chat_file, "w", encoding='utf-8') as f:
            json.dump(saved_chats, f, indent=2, ensure_ascii=False)

        # Rerun the app to reflect the changes immediately
        st.rerun()

# --- Collapsible Chat History Section ---
with st.sidebar.expander("📜 Chat History", expanded=False):
    sorted_chat_names = sorted(saved_chats.keys(), key=lambda x: int(x.split()[1]) if x.split()[1].isdigit() else float('inf'))

    # --- Dropdown to Select Chat ---
    if sorted_chat_names:
        selected_chat = st.selectbox("Select a Chat", options=sorted_chat_names, key="chat_selector")
        if selected_chat:
            st.session_state.chat_history = saved_chats[selected_chat]
            st.session_state.chat_name = selected_chat

        # --- Delete Selected Chat Button ---
        if st.button("❌ Delete Selected Chat", key="delete_selected_chat"):
            del saved_chats[selected_chat]
            if st.session_state.chat_name == selected_chat:
                st.session_state.chat_history = []
                st.session_state.chat_name = "Chat 1"
            with open(chat_file, "w", encoding='utf-8') as f:
                json.dump(saved_chats, f, indent=2, ensure_ascii=False)
            st.rerun()
    else:
        st.info("No chats available.")

    # --- Clear All Chats Styled as Option (Not Button) ---
    if st.button("🧹 Clear All Chats", key="clear_all_chats"):
        saved_chats = {}
        with open(chat_file, "w", encoding='utf-8') as f:
            json.dump(saved_chats, f)
        st.session_state.chat_history = []
        st.session_state.chat_name = "Chat 1"
        st.success("All chat history cleared.")
        st.rerun()

    # --- Style 'Clear All Chats' Button to Look Like Text ---
    st.markdown("""
        <style>
        button[data-testid="button-clear_all_chats"] {
            background-color: transparent !important;
            color: #f87171 !important;
            border: none !important;
            font-size: 14px !important;
            text-align: left !important;
            padding: 6px 0px;
        }
        button[data-testid="button-clear_all_chats"]:hover {
            color: #facc15 !important;  /* Hover color */
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

# --- Main Chat Area ---
col1, col2 = st.columns([1, 2])

with col2:
    st.title("Edusphere AI")

    col_inp1, col_inp2 = st.columns([10, 1])
    with col_inp1:
        user_input = st.text_input("Type your message here:", key="user_input")
    with col_inp2:
        if st.button("🎤", key="speak_button", help="Speak"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening...")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    audio_text = recognizer.recognize_google(audio)
                    st.success(f"You said: {audio_text}")
                    user_input = audio_text
                except sr.UnknownValueError:
                    st.error("Could not understand the audio.")
                except sr.RequestError:
                    st.error("Request failed. Check internet.")
                except sr.WaitTimeoutError:
                    st.error("Listening timed out.")

    # --- Send Button ---
    if st.button("Send", key="send_button"):
        if user_input.strip():
            st.session_state.chat_history.append({"role": "You", "content": user_input})
            bot_reply = get_bot_response(user_input)
            bot_display = f"{avatar_emoji} {bot_reply}" if avatar_choice_display else bot_reply
            st.session_state.chat_history.append({"role": "AI", "content": bot_display})
            saved_chats[st.session_state.chat_name] = st.session_state.chat_history
            with open(chat_file, "w", encoding='utf-8') as f:
                json.dump(saved_chats, f, indent=2, ensure_ascii=False)
        else:
            st.warning("Please enter or speak a message.")

    # --- Chat Display ---
    st.markdown("### 💬 Chat")
    if st.session_state.chat_history:
        for msg in st.session_state.chat_history:
            st.markdown(f"**{msg['role']}**: {msg['content']}")
    else:
        st.info("Start chatting with Edusphere AI!")

    # --- PDF Generation ---
    # --- PDF Generation in Sidebar ---
    with st.sidebar.expander(" 📝 Export Chat", expanded=False):

        # Prepare chat data
        txt_data = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])

        # --- Active Download as .txt Button (Styled Like PDF Button) ---
        st.download_button(
            label="📄 Download as .txt",
            data=txt_data if txt_data.strip() else "No chat available.",
            file_name="chat.txt",
            mime="text/plain",
            key="download_txt",
            use_container_width=True
        )
        st.markdown("""
            <style>
            .stDownloadButton button {
                background-color: transparent !important;  /* Discord-like Blue */
                color: white !important;
                border: none;
                border-radius: 8px;
            }
            .stDownloadButton button:hover {
                background-color: #4752C4 !important;
            }
            </style>
        """, unsafe_allow_html=True)


        # --- Generate PDF and Offer Download ---
        def generate_pdf(chat_data):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for msg in chat_data:
                pdf.multi_cell(0, 10, txt=f"{msg['role']}: {msg['content']}")
            pdf_file = "chat.pdf"
            pdf.output(pdf_file)
            return pdf_file


        if st.button("📑 Generate PDF", key="generate_pdf", use_container_width=True):
            pdf_file = generate_pdf(st.session_state.chat_history)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="📥 Click to Download PDF",
                    data=f,
                    file_name=pdf_file,
                    mime="application/pdf",
                    key="download_pdf",
                    use_container_width=True
                )
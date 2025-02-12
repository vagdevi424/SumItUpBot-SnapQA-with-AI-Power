import streamlit as st
import requests

# Backend URL
BACKEND_URL = "http://localhost:8000"  # Change this if deployed elsewhere

st.set_page_config(page_title="SumItUpBot: SnapQ&A with AI Power", layout="wide")

# Custom Styling
st.markdown(
    """
    <style>
        /* General Styles */
        .stApp {
            background-color: #f9f5ff !important;
            font-family: 'Poppins', Arial, sans-serif;
        }

        /* Title Bar */
        .title-bar {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 16px;
            background: #BBA0CD; /* Darkened Lavender - Slightly darker than before */
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            text-align: center;
            color: #000000;
        }

        .title-bar h1 {
            font-size: 32px;
            font-weight: 600;
            color: #000000;
            margin: 0;
        }

        .title-bar p {
            font-size: 12px;
            font-weight: 400;
            color: #000000;
            margin-top: 5px;
        }

        /* Section Titles */
        h3 {
            color: #000000;
            font-size: 16px;
            font-weight: 600;
            border-bottom: 1px solid #E6E6FA;
            padding-bottom: 4px;
            margin-bottom: 15px;
        }

        /* Upload Box */
        .stFileUploader {
            background-color: #FFFFFF !important;
            border: 1px solid #E6E6FA !important;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            margin-bottom: 15px;
        }

        /* Summary Box */
        .summary-container {
            border-radius: 8px;
            padding: 12px;
            background-color: #FFFFFF;
            overflow-y: auto;
            height: 200px;
            max-height: 200px;
            width: 100%;
            border: 1px solid #E6E6FA;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        .summary-container p {
            line-height: 1.4;
            font-size: 14px;
            color: #000000;
        }

        /* Chat Box */
        .chat-box {
            height: 300px;
            overflow-y: auto;
            border: 1px solid #E6E6FA;
            padding: 12px;
            border-radius: 8px;
            background-color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column;
            margin-top: 10px;
        }

        /* Chat Messages */
        .chat-message {
            padding: 10px;
            border-radius: 8px;
            margin: 4px;
            font-size: 14px;
            width: fit-content;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .chat-user {
            background: #FFFFFF;
            color: #000000;
            text-align: right;
            align-self: flex-end;
        }

        .chat-ai {
            background: #E6E6FA;
            color: #000000;
            text-align: left;
            align-self: flex-start;
        }

        /* Chat Input */
        .stTextArea textarea {
            border: 1px solid #E6E6FA;
            border-radius: 6px;
            padding: 8px 10px;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03);
            color: #000000;
        }

        .stTextArea textarea::placeholder {
            color: #000000;
        }

        /* Buttons */
        .send-btn {
            width: 100%;
            font-size: 14px;
            background-color: #E6E6FA;
            color: #000000;
            padding: 8px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        .send-btn:hover {
            background-color: #D8BFD8;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title Bar with Icon and Caption
st.markdown("""
    <div class="title-bar">
        <h1>SumItUpBot: SnapQ&A with AI Power</h1>
        <p>AI-powered summaries and Q&A at your fingertips, empowering your document workflow with ease.</p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state
if "summary" not in st.session_state:
    st.session_state["summary"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "temp_input" not in st.session_state:
    st.session_state["temp_input"] = ""  # Temporary storage for user input

# Layout configuration
col1, col2 = st.columns([2, 3], gap="large")  # Adjusted column ratio for better chat alignment

with col1:
    # File Upload Section
    st.markdown("<h3>Upload Document</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt", "xlsx", "png", "jpeg", "jpg"], label_visibility="collapsed")

    if uploaded_file and st.session_state["summary"] is None:
        with st.spinner("Processing file..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(f"{BACKEND_URL}/upload/", files=files)

            if response.status_code == 200:
                data = response.json()
                st.session_state["summary"] = data.get("summary", "Summary generation failed.")
            else:
                st.error("Failed to process file. Please try again.")

    # Summary Section with Fixed Height and Scroll
    if st.session_state["summary"]:
        st.markdown("<h3>Summary</h3>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="summary-container">
                <p style="text-align: justify;">{st.session_state["summary"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col2:
    # Chat Window
    st.markdown("<h3>Chat with AI</h3>", unsafe_allow_html=True)
    chat_container = st.container()

    # Render chat messages
    with chat_container:
        chat_html = "<div class='chat-box'>"

        for msg in st.session_state["chat_history"]:
            if msg["is_user"]:
                chat_html += f"<div class='chat-message chat-user'>{msg['content']}</div>"
            else:
                chat_html += f"<div class='chat-message chat-ai'>{msg['content']}</div>"

        chat_html += "</div>"
        chat_container.markdown(chat_html, unsafe_allow_html=True)

    # Chat Input and Send Button
    user_input = st.text_area("Type your message", value=st.session_state["temp_input"], key="temp_input", placeholder="Enter your message here...", label_visibility="collapsed")

    send_clicked = st.button("Send", help="Click to send your message")

    if send_clicked and user_input.strip():
        user_message = user_input.strip()
        st.session_state["chat_history"].append({"content": user_message, "is_user": True})

        with st.spinner("Generating response..."):
            response = requests.post(f"{BACKEND_URL}/qa/", data={"question": user_message})

            if response.status_code == 200:
                answer = response.json().get("answer", "No answer found.")
                st.session_state["chat_history"].append({"content": answer, "is_user": False})
            else:
                st.error("Failed to retrieve answer. Make sure a document is uploaded.")

        # Clear the text input field using session state reset method
        del st.session_state["temp_input"]
        st.rerun()

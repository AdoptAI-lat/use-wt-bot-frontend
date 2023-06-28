import json
import requests
from dataclasses import dataclass
from typing import Literal
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title=
    "USE chatbot",
    page_icon="🌎",
    layout="centered",
    initial_sidebar_state="auto")


@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str


def get_chat_response(question, chat_history = None, global_counter = 0):
    url = f'{st.secrets["host_microservice"]}/api/ms/use-wt-bot/chat'
    headers = {
        'api-key-use': st.secrets["ms_api_key"],
        'Content-Type': 'application/json'
    }

    if chat_history:
        payload = json.dumps({
            "question": question,
            "chat_history": chat_history,
            "global_counter": global_counter
        })
    else:
        payload = json.dumps({
            "question": question
        })
    response = requests.post(url, headers=headers, data=payload)
    print(f"microservice status code: {response.status_code}")
    data = response.json()
    return data['chat_response'], data['chat_history'], data['global_counter']


def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
        st.session_state.global_counter = 0


def on_click_callback():
    human_prompt = st.session_state.human_prompt
    llm_response, chat_history, global_counter = get_chat_response(human_prompt, st.session_state.chat_history, st.session_state.global_counter)
    st.session_state.history.append(
        Message("human", human_prompt)
    )
    st.session_state.history.append(
        Message("ai", llm_response)
    )
    st.session_state.chat_history = chat_history
    st.session_state.global_counter = global_counter
    st.session_state.human_prompt = ""


load_css()
initialize_session_state()

st.title("Bienvenido al chatbot de USE 🤖")

chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")

with chat_placeholder:
    for chat in st.session_state.history:
        div = f"""
<div class="chat-row 
    {'' if chat.origin == 'ai' else 'row-reverse'}">
    <img class="chat-icon" src="app/static/{
        'ai_icon.png' if chat.origin == 'ai' 
                      else 'user_icon.png'}"
         width=32 height=32>
    <div class="chat-bubble
    {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}">
        &#8203;{chat.message}
    </div>
</div>
        """
        st.markdown(div, unsafe_allow_html=True)
    
    for _ in range(3):
        st.markdown("")

with prompt_placeholder:
    st.markdown("**Chat**")
    cols = st.columns((6, 1))
    cols[0].text_input(
        "Chat",
        placeholder="Inserta tu pregunta",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "Submit", 
        type="primary", 
        on_click=on_click_callback, 
    )


components.html("""
<script>
const streamlitDoc = window.parent.document;

const buttons = Array.from(
    streamlitDoc.querySelectorAll('.stButton > button')
);
const submitButton = buttons.find(
    el => el.innerText === 'Submit'
);

streamlitDoc.addEventListener('keydown', function(e) {
    switch (e.key) {
        case 'Enter':
            submitButton.click();
            break;
    }
});
</script>
""", 
    height=0,
    width=0,
)


footer_text = """
<div class="footer">
    <p>Disclaimer: Sistema únicamente de prueba para uso interno y las respuestas pueden no ser correctas.</p>
</div>
"""
st.markdown(footer_text, unsafe_allow_html=True)
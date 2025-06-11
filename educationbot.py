#교육 지원 챗봇은 여기에다 작성해주세요.
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="GPT-4.1 Mini 챗봇", layout="centered")

# === API Key 입력 및 세션 상태 저장 ===
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
api_key_input = st.text_input("OpenAI API Key를 입력하세요:", type="password", value=st.session_state.api_key)
st.session_state.api_key = api_key_input

st.title("GPT-4.1 Mini 챗봇")

# === 초기 세션 상태 설정 ===
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "당신은 친절한 AI 챗봇입니다."}]
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""

# === 모델 및 temperature 설정 ===
model = st.selectbox("사용할 모델을 선택하세요:", ["gpt-3.5-turbo", "gpt-4.1-mini"], index=1, key="chat_model")
temperature = st.slider("창의성(temperature) 설정:", 0.0, 1.0, 0.7, step=0.1, key="chat_temp")

# === Clear 버튼 ===
if st.button("🧹 Clear 대화 초기화"):
    st.session_state.messages = [{"role": "system", "content": "당신은 친절한 AI 챗봇입니다."}]
    st.session_state.chat_input = ""

# === 이전 메시지 출력 ===
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"**🧑 사용자:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 GPT:** {msg['content']}")

# === 사용자 입력 ===
user_input = st.text_input("메시지를 입력하세요:", value=st.session_state.chat_input, key="chat_input_box")

if user_input and st.session_state.api_key:
    # 입력값 저장 후 초기화
    st.session_state.chat_input = user_input
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        client = OpenAI(api_key=st.session_state.api_key)
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            temperature=temperature,
            max_tokens=500,
        )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.chat_input = ""  # 입력창 초기화

    except Exception as e:
        st.error(f"오류 발생: {str(e).encode('utf-8', errors='ignore').decode('utf-8')}")
       여기부터 import streamlit as st
from openai import OpenAI
from datetime import datetime

# === 페이지 설정 ===
st.set_page_config(page_title="GPT-4.1 Mini 챗봇", layout="centered")

# === 세션 상태 초기화 ===
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "당신은 친절한 AI 챗봇입니다."}]
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False
if "client" not in st.session_state:
    st.session_state.client = None
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "user_level" not in st.session_state:
    st.session_state.user_level = "초급자"

# === 사이드바 설정 ===
st.sidebar.title("🔧 설정")
st.session_state.api_key = st.sidebar.text_input("🔐 OpenAI API Key", type="password", value=st.session_state.api_key)
model = st.sidebar.selectbox("💬 모델 선택", ["gpt-3.5-turbo", "gpt-4.1-mini"], index=1)
temperature = st.sidebar.slider("🎨 창의성 (temperature)", 0.0, 1.0, 0.7, step=0.1)
dark_mode_toggle = st.sidebar.checkbox("🌙 다크모드", value=st.session_state.dark_mode)
if dark_mode_toggle != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_mode_toggle
    st.rerun()

# === 사용자 레벨 선택 ===
col1, col2 = st.columns(2)
with col1:
    if st.button("👶 초급자 모드"):
        st.session_state.user_level = "초급자"
with col2:
    if st.button("🧠 중급자 모드"):
        st.session_state.user_level = "중급자"

st.markdown(f"현재 모드: **{st.session_state.user_level}**")

# === 테마 적용 ===
def apply_theme():
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
            .stApp { background-color: #121212; color: #e0e0e0; }
            .stTextInput>div>input, .stTextArea>div>textarea {
                background-color: #222222; color: #e0e0e0;
            }
            pre {
                background-color: #222222; color: #e0e0e0;
                padding: 10px; border-radius: 8px; overflow-x: auto;
            }
            .chat-user { background-color: #333a4d; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
            .chat-assistant { background-color: #003a6c; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            pre {
                background-color: #f5f5f5; color: #333333;
                padding: 10px; border-radius: 8px; overflow-x: auto;
            }
            .chat-user { background-color: #f0f0f5; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
            .chat-assistant { background-color: #e8f6ff; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)

apply_theme()

# === 본문 타이틀 ===
st.title("🤖 GPT-4.1 Mini 챗봇")

# === 대화 초기화 ===
if st.sidebar.button("🧹 대화 초기화"):
    st.session_state.messages = [{"role": "system", "content": "당신은 친절한 AI 챗봇입니다."}]
    st.session_state.chat_input = ""
    st.session_state.clear_input = True
    st.rerun()

# === 대화 다운로드 ===
def get_chat_log_text():
    chat_log = ""
    for msg in st.session_state.messages[1:]:
        role = "사용자" if msg["role"] == "user" else "GPT"
        chat_log += f"{role}: {msg['content']}\n\n"
    return chat_log

chat_log_text = get_chat_log_text()
st.sidebar.download_button(
    label="💾 대화 저장",
    data=chat_log_text,
    file_name=f"chat_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    mime="text/plain",
)

# === 이전 메시지 출력 ===
chat_html = ""
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        chat_html += f"<div class='chat-user'>🧑‍💻 {msg['content']}</div>"
    elif msg["role"] == "assistant":
        chat_html += f"<div class='chat-assistant'>🤖 {msg['content']}</div>"

st.markdown(f"""
<div id='chat-container' style='height: 500px; overflow-y: auto; padding: 10px; border: 1px solid #ddd;'>
{chat_html}
</div>
<script>
    var chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
</script>
""", unsafe_allow_html=True)

# === 사용자 입력 ===
if st.session_state.clear_input:
    st.session_state.chat_input = ""
    st.session_state.clear_input = False

if st.session_state.is_thinking:
    st.info("GPT가 응답 중입니다... 잠시만 기다려주세요.")
else:
    user_input = st.text_area("메시지를 입력하세요:", key="chat_input", height=150, placeholder="코드나 질문을 입력하세요. Shift+Enter로 줄바꿈 할 수 있어요.")
    if st.button("💬 질문하기", disabled=st.session_state.is_thinking) and user_input.strip():
        st.session_state.chat_input = user_input
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.is_thinking = True

        with st.spinner("GPT가 생각 중입니다..."):
            try:
                if st.session_state.client is None:
                    st.session_state.client = OpenAI(api_key=st.session_state.api_key)

                # 사용자 수준에 따라 system 메시지 재구성
                if st.session_state.user_level == "초급자":
                    st.session_state.messages[0] = {"role": "system", "content": "너는 초급자를 위한 친절한 도우미야. 항상 예제를 먼저 보여주고, 아주 쉽게 설명해줘."}
                else:
                    st.session_state.messages[0] = {"role": "system", "content": "너는 중급자를 위한 도우미야. 코드만 정확하게 출력하고 불필요한 설명은 하지 않아도 돼."}

                response = st.session_state.client.chat.completions.create(
                    model=model,
                    messages=st.session_state.messages,
                    temperature=temperature,
                    max_tokens=500,
                )
                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")

            finally:
                st.session_state.is_thinking = False
                st.session_state.clear_input = True
                st.rerun()


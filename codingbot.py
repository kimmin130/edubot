import streamlit as st
from openai import OpenAI
from datetime import datetime
from streamlit.components.v1 import html

# === 페이지 설정 ===
st.set_page_config(page_title="코딩 도우미 코딩봇", layout="centered")

# === 세션 상태 초기화 ===
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
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
if "summary_requested" not in st.session_state:
    st.session_state.summary_requested = False
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "current_language" not in st.session_state:
    st.session_state.current_language = "Python"
if "generated_problem" not in st.session_state:
    st.session_state.generated_problem = ""

# === 시스템 프롬프트 ===
default_system_prompt = """
default_system_prompt = """
너는 이제부터 학생을 도와주는 **코드를 쉽게 분석해주는 튜터** 역할을 해.
너의 목표는 학생이 코드의 작동 원리를 스스로 이해할 수 있도록 돕는 거야.
설명은 **쉬운 말로**, 단계별로 진행하고, **학생이 이해하고 있는지 확인하기 위해 자주 질문**해.
처음엔 아래 3가지 질문을 한 번에 하지 말고 **하나씩**, **학생의 대답을 기다리며** 대화하듯 진행해:

1. "안녕하세요! 어떤 코드를 분석하고 싶은가요? 어떤 부분이 궁금한지 알려줄 수 있을까요?"
2. (대답 후) "좋아요! 혹시 학습 수준은 어떻게 되나요? 고등학생, 대학생, 직장인 중 어디에 속하나요?"
3. (대답 후) "이 코드에 대해서 이미 알고 있는 부분이 있다면 이야기해줄래요?"

학생의 답변을 받은 후 아래 규칙을 따라:

- 코드를 한 줄씩 또는 블록 단위로 나눠서 설명하고,
- 각 설명마다 "이 부분은 어떤 의미일까?" "이게 왜 필요했을까?"처럼 질문을 던지고,
- 헷갈릴 수 있는 부분은 간단한 예시나 비유로 풀어줘.
- 정답을 바로 말하지 말고, 학생이 생각하고 말하도록 유도해.
- 학생이 개념을 자기 말로 설명하거나, 비슷한 예시를 만들거나, 다른 문제에 적용할 수 있을 때까지 도와줘.

학생이 어느 정도 이해했다고 느껴지면 이렇게 마무리해:

"좋아요! 이제 이 코드를 네가 직접 설명할 수 있겠어요. 궁금한 게 더 있으면 언제든 물어봐!"
"""

# === 초기 메시지 ===
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({"role": "system", "content": default_system_prompt})
    st.session_state.messages.append({"role": "assistant", "content": "안녕하세요! 코딩 도우미 챗봇 **에듀봇**입니다.\n알고 싶은 코드가 있다면 편하게 물어보세요 😊"})

# === 다크모드 CSS ===
def apply_theme():
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .stApp { background-color: #121212; color: #e0e0e0; }
        pre, code { background-color: #222 !important; color: #eee !important; padding: 10px; border-radius: 8px; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        pre, code { background-color: #f5f5f5; color: #333; padding: 10px; border-radius: 8px; }
        </style>
        """, unsafe_allow_html=True)

# === 사이드바 ===
st.sidebar.title("🔧 설정")
st.session_state.api_key = st.sidebar.text_input("🔐 OpenAI API Key", type="password", value=st.session_state.api_key)
model = st.sidebar.selectbox("💬 모델 선택", ["gpt-3.5-turbo", "gpt-4.1-mini"], index=1)
dark_mode_toggle = st.sidebar.checkbox("🌙 다크모드", value=st.session_state.dark_mode)
if dark_mode_toggle != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_mode_toggle
    st.rerun()

if not st.session_state.api_key:
    st.warning("⚠️ OpenAI API 키가 필요합니다. 사이드바에서 입력해 주세요.")
    st.stop()

if st.session_state.client is None:
    st.session_state.client = OpenAI(api_key=st.session_state.api_key)

apply_theme()
st.title("🤖 GPT-4.1 Mini 코딩봇")

# === 대화 표시 ===
with st.container():
    for msg in st.session_state.messages[1:]:
        if msg["role"] == "user":
            st.markdown(f"<div style='background:#eee;border-radius:8px;padding:8px'>🧑‍💻 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#cce6ff;border-radius:8px;padding:8px'>🤖 {msg['content']}</div>", unsafe_allow_html=True)

# === 입력 ===
user_input = st.text_area("메시지를 입력하세요:", value=st.session_state.chat_input, height=150, placeholder="코드나 질문을 입력하세요.")
if st.button("💬 물어보기", disabled=st.session_state.is_thinking) and user_input.strip():
    st.session_state.is_thinking = True
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.generated_code = user_input
    st.session_state.chat_input = ""
    st.rerun()

# === GPT 요청 함수 ===
def ask_gpt(messages):
    try:
        response = st.session_state.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"GPT 요청 실패: {e}")
        return ""

# === 코드 변환 + 문제 생성 버튼 ===
col_py, col_c, col_java, col_prob = st.columns(4)

with col_py:
    if st.button("🐍 Python 코드"):
        if st.session_state.generated_code.strip() and st.session_state.current_language != "Python":
            with st.spinner("Python 코드로 변환 중..."):
                result = ask_gpt([{"role": "user", "content": f"다음 코드를 Python으로 변환해줘:\n{st.session_state.generated_code}"}])
                st.session_state.current_language = "Python"
                st.session_state.generated_code = result
                st.code(result, language="python")

with col_c:
    if st.button("💻 C 코드"):
        if st.session_state.generated_code.strip() and st.session_state.current_language != "C":
            with st.spinner("C 코드로 변환 중..."):
                result = ask_gpt([{"role": "user", "content": f"다음 코드를 C언어로 변환해줘:\n{st.session_state.generated_code}"}])
                st.session_state.current_language = "C"
                st.session_state.generated_code = result
                st.code(result, language="c")

with col_java:
    if st.button("☕ Java 코드"):
        if st.session_state.generated_code.strip() and st.session_state.current_language != "Java":
            with st.spinner("Java 코드로 변환 중..."):
                result = ask_gpt([{"role": "user", "content": f"다음 코드를 Java로 변환해줘:\n{st.session_state.generated_code}"}])
                st.session_state.current_language = "Java"
                st.session_state.generated_code = result
                st.code(result, language="java")

with col_prob:
    if st.button("📌 문제 생성"):
        if st.session_state.generated_code.strip():
            with st.spinner("문제 + 코드 생성 중..."):
                prompt = (
                    f"다음 주제를 기반으로 간단한 코딩 문제를 하나 내주고, "
                    f"{st.session_state.current_language}로 풀이 코드를 작성해줘.\n\n"
                    f"주제: {st.session_state.generated_code}"
                )
                result = ask_gpt([{"role": "user", "content": prompt}])
                st.session_state.generated_problem = result
                st.markdown("**📌 생성된 문제 + 코드:**")
                st.code(result, language=st.session_state.current_language.lower())
        else:
            st.warning("먼저 코드나 주제를 입력해 주세요!")

import os
import streamlit as st
from openai import OpenAI
import time

# OpenAI 클라이언트 설정
client = OpenAI(api_key=st.secrets["API_KEY"])

# Streamlit 앱 설정
st.title("외계행성계 챗봇 도우미")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.assistant_id = "asst_ePVQMU5H2n9iOINxYbv35biN"

# 채팅 히스토리를 표시할 컨테이너
chat_container = st.container()

# 사용자 입력 받기 (페이지 맨 아래에 위치)
user_input = st.chat_input("학생이 궁금한 점을 물어보세요!:")

if user_input:
    # 사용자 메시지 추가 및 즉시 표시
    st.session_state.messages.append({"role": "학생", "content": user_input})
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # 로딩 메시지 표시
    with chat_container:
        with st.chat_message("도우미"):
            message_placeholder = st.empty()
            message_placeholder.text("답변을 생성하고 있습니다...")

    # 스레드 생성 또는 기존 스레드 사용
    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

    # 메시지 추가
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=user_input
    )

    # 실행 생성
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=st.session_state.assistant_id
    )

    # 실행 완료 대기
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )

    # 응답 메시지 가져오기
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    # 새 메시지 추가 및 표시
    for message in messages.data:
        if message.role == "assistant" and message.content[0].type == "text":
            assistant_message = message.content[0].text.value
            st.session_state.messages.append({"role": "도우미", "content": assistant_message})
            message_placeholder.text(assistant_message)
            break

# 대화 내용 표시
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 자동 스크롤을 위한 JavaScript 실행
st.markdown("""
<script>
    var element = window.parent.document.querySelector('section.main');
    element.scrollTop = element.scrollHeight;
</script>
""", unsafe_allow_html=True)
import os
import streamlit as st
from openai import OpenAI
import time
import asyncio

# OpenAI 클라이언트 설정
client = OpenAI(api_key=st.secrets["API_KEY"])

# Streamlit 앱 설정
st.title("외계행성계 챗봇 도우미")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.assistant_id = "asst_ePVQMU5H2n9iOINxYbv35biN"
    st.session_state.waiting_for_response = False

if "thread_id" not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

# 비동기 함수 정의
async def get_assistant_response(user_input):
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
        await asyncio.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )

    # 응답 메시지 가져오기
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    for message in messages.data:
        if message.role == "assistant" and message.content[0].type == "text":
            return message.content[0].text.value

    return "죄송합니다. 응답을 생성하는 데 문제가 발생했습니다."

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력 처리
if user_input := st.chat_input("학생이 궁금한 점을 물어보세요!:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.waiting_for_response = True

# 비동기 응답 처리
if st.session_state.waiting_for_response:
    with st.chat_message("ai"):
        message_placeholder = st.empty()
        message_placeholder.text("답변을 생성하고 있습니다...")

    assistant_response = asyncio.run(get_assistant_response(user_input))
    
    st.session_state.messages.append({"role": "ai", "content": assistant_response})
    message_placeholder.text(assistant_response)
    st.session_state.waiting_for_response = False

    st.rerun()

# 자동 스크롤
st.markdown("""
<script>
    var element = window.parent.document.querySelector('section.main');
    element.scrollTop = element.scrollHeight;
</script>
""", unsafe_allow_html=True)
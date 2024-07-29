import os
import streamlit as st
from openai import OpenAI
import time

API_KEY = api_key

# OpenAI 클라이언트 설정
client = OpenAI(api_key=API_KEY)

# Streamlit 앱 설정
st.title("OpenAI Assistant 챗봇")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.assistant_id = "asst_ePVQMU5H2n9iOINxYbv35biN"

# 사용자 입력 받기
user_input = st.text_input("메시지를 입력하세요:")

if user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})

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

    # 새 메시지 추가
    for message in messages.data:
        if message.role == "assistant" and message.content[0].type == "text":
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            break

# 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
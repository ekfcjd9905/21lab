import streamlit as st
from openai import OpenAI

st.title("Chat 페이지 (gpt-5-mini 챗봇)")

# 🔐 API Key (이미 session_state에 있다면 이 부분은 생략 가능)
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input(
    "OpenAI API Key를 입력하세요 (Chat 페이지용)",
    type="password",
    value=st.session_state.api_key,
    key = "api_key_qa"
)
st.session_state.api_key = api_key

# 🧠 메모리 초기화 (대화 기록)
if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role":"user","content":"..."}, ...]

# 🧹 Clear 버튼: 대화 전체 삭제
if st.button("🧹 Clear (대화 초기화)"):
    st.session_state.messages = []
    st.success("대화가 초기화되었습니다.")

st.write("---")

# 💬 지금까지 저장된 메시지들 화면에 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 💬 사용자 입력
if prompt := st.chat_input("메시지를 입력해보세요 (챗페이지 챗봇)"):
    if not st.session_state.api_key:
        st.error("⚠ 먼저 OpenAI API Key를 입력하세요.")
    else:
        # 1) 사용자 메시지 화면에 보여주기
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2) 메모리에 사용자 메시지 저장
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        # 3) 지금까지의 대화를 history로 만들어서 모델에 전달
        history_messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        for m in st.session_state.messages:
            history_messages.append(
                {"role": m["role"], "content": m["content"]}
            )

        # 4) OpenAI Chat Completions API 호출
        try:
            client = OpenAI(api_key=st.session_state.api_key)

            with st.chat_message("assistant"):
                with st.spinner("gpt-5-mini가 응답을 생성 중입니다..."):
                    resp = client.chat.completions.create(
                        model="gpt-5-mini",
                        messages=history_messages,
                    )
                    answer = resp.choices[0].message.content
                    st.markdown(answer)

            # 5) 메모리에 LLM 응답 저장
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")




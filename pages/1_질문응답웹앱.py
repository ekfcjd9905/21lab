import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="GPT-5-mini QA", layout="wide")

# -------------------------
# 1. API KEY 저장 (Session State)
# -------------------------
st.title("GPT-5-mini 질문 응답 웹앱")

# API Key가 session_state에 없으면 한 번 생성
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# 입력 시 session_state에 자동 저장
api_key_input = st.text_input(
    "OpenAI API Key를 입력하세요",
    type="password",
    value=st.session_state.api_key
)

# session_state 업데이트
st.session_state.api_key = api_key_input


# -------------------------
# 2. 질문 입력
# -------------------------
question = st.text_area(
    "질문을 입력하세요",
    placeholder="예: 인공지능과 머신러닝의 차이를 알려줘"
)

# -------------------------
# 3. API 호출 캐시 함수
# -------------------------
@st.cache_data(show_spinner=False)
def ask_gpt(api_key, question):
    """
    질문이 같으면 캐시된 데이터가 반환됨.
    api_key + question 조합이 같아야 캐시 사용됨.
    """
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content


# -------------------------
# 4. 버튼 눌렀을 때 수행
# -------------------------
if st.button("GPT-5-mini에게 물어보기"):
    if not st.session_state.api_key:
        st.error("⚠ API Key를 먼저 입력하세요.")
    elif not question.strip():
        st.error("⚠ 질문을 입력하세요.")
    else:
        with st.spinner("GPT-5-mini가 답변 생성 중..."):
            answer = ask_gpt(st.session_state.api_key, question)

        st.subheader("📌 GPT-5-mini의 응답")
        st.write(answer)

import streamlit as st
from openai import OpenAI

def show_message(msg):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -------------------------------
# 0. API Key 입력 (이 페이지에서 직접 입력)
# -------------------------------
st.header("ChatPDF")

# session_state에 api_key 저장
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key = st.text_input(
    "OpenAI API Key를 입력하세요",
    type="password",
    value=st.session_state.api_key,
    key="chatpdf_api_key"
)

# 입력 시 자동 반영
st.session_state.api_key = api_key

# API Key가 없으면 진행 불가
if not api_key:
    st.info("PDF 업로드 및 질의응답을 위해 먼저 API Key를 입력하세요.")
    st.stop()

# OpenAI client 생성
client = OpenAI(api_key=api_key)


# -------------------------------
# 1. PDF 파일 업로드
# -------------------------------
pdf_file = st.file_uploader(
    "PDF 파일을 업로드하세요", 
    type=["pdf"], 
    accept_multiple_files=False
)

# 최초 업로드 시 vector store 생성 및 파일 업로드
if pdf_file is not None and "chatpdf_vector_store" not in st.session_state:
    vector_store = client.vector_stores.create(name="ChatPDF")
    file_batch = client.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=[pdf_file]
    )
    st.session_state.chatpdf_vector_store = vector_store


# PDF 없으면 대화 불가
if "chatpdf_vector_store" not in st.session_state:
    st.info("PDF 파일을 업로드하면 해당 내용을 기반으로 대화할 수 있습니다.")
    st.stop()


# -------------------------------
# 2. 대화 기록 초기화
# -------------------------------
if "chatpdf_messages" not in st.session_state:
    st.session_state.chatpdf_messages = []


# -------------------------------
# 3. Clear 버튼 (PDF 삭제 + 대화 초기화)
# -------------------------------
if st.button("Clear (PDF 및 대화 초기화)"):
    # 대화 삭제
    st.session_state.chatpdf_messages = []

    # PDF vector store 삭제
    try:
        client.vector_stores.delete(st.session_state.chatpdf_vector_store.id)
    except:
        pass

    # 세션에서 제거
    if "chatpdf_vector_store" in st.session_state:
        del st.session_state.chatpdf_vector_store

    st.success("PDF 파일과 대화 기록이 삭제되었습니다. 새 PDF를 업로드해 주세요.")
    st.stop()


# -------------------------------
# 4. 지금까지의 대화 출력
# -------------------------------
for msg in st.session_state.chatpdf_messages:
    show_message(msg)


# -------------------------------
# 5. 사용자 질문 입력 → File Search → 모델 응답
# -------------------------------
if prompt := st.chat_input("PDF 내용을 바탕으로 질문해 보세요"):
    # 사용자 메시지 저장 + 출력
    user_msg = {"role": "user", "content": prompt}
    st.session_state.chatpdf_messages.append(user_msg)
    show_message(user_msg)

    # 모델 호출 (Responses API + File Search)
    with st.chat_message("assistant"):
        with st.spinner("PDF에서 답을 찾는 중입니다..."):
            response = client.responses.create(
                model="gpt-5-mini",
                input=st.session_state.chatpdf_messages,
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [st.session_state.chatpdf_vector_store.id]
                    }
                ]
            )
            answer_text = response.output_text
            st.markdown(answer_text)

    # 모델 메시지 저장
    assistant_msg = {"role": "assistant", "content": answer_text}
    st.session_state.chatpdf_messages.append(assistant_msg)

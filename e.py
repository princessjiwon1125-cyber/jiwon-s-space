import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# 1. Streamlit 설정 (가장 위에 위치해야 함)
st.set_page_config(page_title="jiwon's space", page_icon="💖")

# 2. 환경 변수 로드 및 설정
load_dotenv("key.env")
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 3. CSS를 이용한 UI 커스텀 (말풍선 색상 포함)
st.markdown(f"""
    <style>
    /* 전체 배경색 */
    .stApp {{
        background-color: #fae8ed;
    }}
    
    /* 사이드바 배경색 */
    [data-testid="stSidebar"] {{
        background-color: #fdd5df;
    }}

    /* 유저 말풍선 (오른쪽) 배경색 변경 */
    [data-testid="stChatMessage"] {{
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }}

    /* 버튼 스타일 */
    .stButton>button {{
        background-color: #Fdd5df;
        color: #ffb2c5;
        border-radius: 20px;
        border: 2px solid #ffa2b9;
        font-weight: bold;
    }}
    
    .stButton>button:hover {{
        border-color: #Ffdd5df;
        color: white;
        background-color: #ffa2b9;
    }}

    /* 입력창 테두리 색상 */
    div[data-baseweb="input"] {{
        border-color: #Fdd5df !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. LLM 호출 함수
def get_chatbot_response(messages, temp=0.7, model="gpt-4o-mini"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"API 호출 중 에러가 발생했습니다: {e}"

# 5. UI 텍스트
st.title("jiwonononononon <3")
st.caption("heyyyy")

# 6. 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# 7. 기존 대화 표시
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 8. 입력 및 응답
if prompt := st.chat_input("drop your questionssss"):
    # 사용자 메시지 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("jiwon is thinking..."):
            full_response = get_chatbot_response(st.session_state.messages)
            st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 9. 사이드바 설정
with st.sidebar:
    st.header("Settings")
    if st.button("Reset Conversation"):
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
        st.rerun()
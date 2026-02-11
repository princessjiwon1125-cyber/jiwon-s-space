import streamlit as st
import os

# 터미널 창(로그)에 사용 가능한 이미지 모델 목록이 출력됩니다.
for m in genai_client.models.list():
    if 'image' in m.name or 'imagen' in m.name:
        print(f"✅ 사용 가능한 모델: {m.name}")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from duckduckgo_search import DDGS
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Library not found. Please run: pip install -U google-genai")

# --- 0. Set your Gemini API Key ---
# ⚠️ SECURITY WARNING: Sharing your API key publicly is not recommended.
#    For production, use environment variables (e.g., in a .env file and load with dotenv).
os.environ["GOOGLE_API_KEY"] = "AIzaSyACX_I8PeSQ7PX3nAvJSfDdeghNjFObL34"

# --- 1. Streamlit Page Configuration ---
st.set_page_config(page_title="jiwon's space 🥨", page_icon="🥨", layout="wide")

# --- 2. UI Customization (Pink Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #fae8ed; }
    [data-testid="stSidebar"] { background-color: #fdd5df; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    .stButton > button {
        background-color: #Fdd5df; color: #ffb2c5;
        border-radius: 20px; border: 2px solid #ffa2b9; font-weight: bold;
    }
    .stButton > button:hover { border-color: #Ffdd5df; color: white; background-color: #ffa2b9; }
    div[data-baseweb="input"] { border-color: #Fdd5df !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Gemini LLM & Tool Setup ---
@tool
def web_search(query: str) -> str:
    """Useful for searching current events or real-time data on the web."""
    try:
        with DDGS() as ddgs:
            results = [f"Title: {r['title']}\nSnippet: {r['body']}" for r in ddgs.text(query, max_results=3)]
        return "\n\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

# Initialize Gemini LLM for chat and tool use
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_with_tools = llm.bind_tools([web_search])

# --- 4. Gemini Image Generation Setup ---
# Gemini SDK 클라이언트 초기화
# 51번 라인 근처
genai_client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

def generate_gemini_image(prompt: str):
    try:
        with st.spinner(f"✨ Generating image..."):
            # 1. 'model=' 이 중복되지 않도록 주의하세요!
            # 2. 모델명을 'imagen-3.0-generate-001'로 고정합니다.
            response = genai_client.models.generate_images(
                #model='imagen-3.0-generate-001'
                model='imagen-3.0-fast-generate-001', 
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                )
            )
            
            if response.generated_images:
                # 데이터를 바이트로 변환하여 반환
                return response.generated_images[0].image.as_bytes()
            return None
    except Exception as e:
        # 404 에러가 계속된다면, API 키가 Imagen 사용 권한이 있는지 확인해야 합니다.
        st.error(f"Image Error: {e}")
        return None

# --- 5. Memory & Session Management for Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = ChatMessageHistory()

def get_chat_session_history(session_id):
    return st.session_state.messages

# --- 6. Build the Agent Chain for Chat ---
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a versatile AI assistant. You are searching the web for recent or real-time web. ALWAYS respond in English."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chat_chain = chat_prompt | llm_with_tools
chat_agent_with_memory = RunnableWithMessageHistory(
    chat_chain,
    get_chat_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# --- 7. Streamlit UI Elements ---
st.title("jiwonononononon <3")
st.caption("heyyyy - Ask me anything, or generate an image!")

# Sidebar for Conversation Reset and Image Creator
with st.sidebar:
    st.header("Settings")
    if st.button("Reset Conversation"):
        st.session_state.messages.clear()
        st.rerun()
    st.markdown("---")
    st.header("Image Creator")
    image_prompt = st.text_area("Enter prompt for your image:", "A cute panda hacker coding on a laptop, cyberpunk style")
    if st.button("Generate Image"):
        if image_prompt:
            st.session_state["last_image_bytes"] = generate_gemini_image(image_prompt)
        else:
            st.warning("Please enter a prompt to generate an image.")

# --- 8. Display Last Generated Image (if any) ---
if "last_image_bytes" in st.session_state and st.session_state["last_image_bytes"]:
    st.subheader("Last Generated Image")
    st.image(st.session_state["last_image_bytes"], caption="Generated by Gemini", use_column_width=True)
    st.markdown("---")

# --- 9. Display Chat History ---
for msg in st.session_state.messages.messages:
    role = "user" if msg.type == "human" else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- 10. Chat Input & Processing ---
if user_input := st.chat_input("drop your questionssss"):
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Process AI Response
    with st.chat_message("assistant"):
        with st.spinner("jiwon is thinking..."):
            # A simple session_id is fine for Streamlit's single-user context
            chat_config = {"configurable": {"session_id": "streamlit_user"}} 
            
            response = chat_agent_with_memory.invoke({"input": user_input}, config=chat_config)

            # Check if Tool (Search) was called by the LLM
            if response.tool_calls:
                search_query = response.tool_calls[0]['args']['query']
                st.info(f"🔍 Searching for: {search_query}...")
                
                search_result = web_search.invoke(response.tool_calls[0]["args"])
                
                # Gemini generates final summary
                final_answer = llm.invoke(
                    f"User Question: {user_input}\nSearch Result: {search_result}\nSummarize in English (3-4 sentences)."
                )
                output_text = final_answer.content
            else:
                output_text = response.content
            
            st.markdown(output_text)
            
            # Manually update history for Streamlit if tool was used (otherwise RunnableWithMessageHistory handles it)
            # This ensures tool outputs are reflected in the displayed history
            if response.tool_calls:
                 st.session_state.messages.add_user_message(user_input)
                 st.session_state.messages.add_ai_message(output_text)
import streamlit as st
from google import genai

# 페이지 설정
st.set_page_config(
    page_title="연애상담 챗봇",
    page_icon="💖",
)

st.title("💖 연애상담 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# API 키 확인
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secrets에 GEMINI_API_KEY가 설정되지 않았습니다.")
    st.stop()

# Gemini 클라이언트 생성
client = genai.Client(api_key=api_key)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "안녕하세요 😊\n\n"
                "저는 연애상담 챗봇입니다.\n"
                "썸, 짝사랑, 이별, 재회, 연애 고민 등을 편하게 이야기해 주세요."
            ),
        }
    ]

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
prompt = st.chat_input("연애 고민을 입력하세요...")

if prompt:

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("생각 중..."):

                # 대화 기록 생성
                conversation = ""

                for msg in st.session_state.messages:
                    role = "사용자" if msg["role"] == "user" else "상담사"
                    conversation += f"{role}: {msg['content']}\n"

                system_prompt = """
너는 공감 능력이 뛰어난 연애상담 전문가다.

규칙:
1. 따뜻하고 친절하게 답변한다.
2. 사용자의 감정을 먼저 공감한다.
3. 현실적인 조언을 제공한다.
4. 비난하거나 공격적인 표현을 사용하지 않는다.
5. 답변은 한국어로 한다.
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=f"""
{system_prompt}

다음은 상담 기록이다.

{conversation}

상담사 답변:
"""
                )

                answer = response.text

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

        except Exception as e:
            error_msg = f"오류가 발생했습니다.\n\n{str(e)}"

            st.error(error_msg)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "죄송해요. 잠시 후 다시 시도해 주세요.",
                }
            )

# 사이드바
with st.sidebar:
    st.header("설정")

    if st.button("대화 초기화"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "안녕하세요 😊\n\n"
                    "연애 고민을 편하게 이야기해 주세요."
                ),
            }
        ]
        st.rerun()

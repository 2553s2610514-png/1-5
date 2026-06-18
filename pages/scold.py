import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="AI 절약 잔소리꾼",
    page_icon="💸",
    layout="centered"
)

st.title("💸 AI 절약 잔소리꾼")
st.caption("후회되는 소비를 입력하면 AI가 잔소리해드립니다.")

# API 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("GEMINI_API_KEY가 설정되지 않았습니다.")
    st.stop()

amount = st.number_input(
    "얼마를 썼나요? (원)",
    min_value=0,
    step=1000
)

waste = st.text_input(
    "필요 없었다고 생각하는 지출은?"
)

level = st.selectbox(
    "잔소리 강도",
    ["😊 순한맛", "😒 보통", "🔥 매운맛"]
)

allow_swear = st.checkbox("욕설 허용")

generate = st.button("AI 잔소리 듣기")

if generate:

    if amount <= 0:
        st.warning("지출 금액을 입력해주세요.")
        st.stop()

    if not waste.strip():
        st.warning("후회되는 지출 내용을 입력해주세요.")
        st.stop()

    intensity_map = {
        "😊 순한맛": "부드럽고 유머러스하게",
        "😒 보통": "현실적으로",
        "🔥 매운맛": "아주 강하게"
    }

    swear_rule = ""

    if allow_swear:
        swear_rule = """
욕설 사용을 허용한다.
단, 과도한 혐오 표현은 금지.
친구가 장난스럽게 혼내는 느낌으로 적당한 욕설 사용 가능.
"""
    else:
        swear_rule = """
욕설 사용 금지.
"""

    prompt = f"""
너는 '절약 잔소리 AI'다.

사용자가 후회하는 소비를 했다.

지출 금액:
{amount:,}원

지출 내용:
{waste}

잔소리 강도:
{intensity_map[level]}

규칙:
- 한국어로 답변
- 5~8문장 정도
- 재미있게 작성
- 소비 습관을 반성하게 만들 것
- 마지막에는 절약 팁 1개 제공

{swear_rule}
"""

    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash-lite"
        )

        response = model.generate_content(prompt)

        st.subheader("📢 AI의 잔소리")

        st.write(response.text)

    except Exception as e:
        st.error("AI 응답 생성 중 오류가 발생했습니다.")
        st.exception(e)

st.markdown("---")
st.caption("Made with Streamlit + Gemini")

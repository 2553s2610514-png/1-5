import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import google.generativeai as genai

st.set_page_config(
    page_title="AI 잔소리 가계부",
    page_icon="💸",
    layout="wide"
)

st.title("💸 AI 잔소리 가계부")
st.caption("돈을 쓸 때마다 잔소리하는 똑똑한 가계부")

# 세션 상태 초기화
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["날짜", "카테고리", "금액", "메모"]
    )

categories = [
    "식비",
    "카페",
    "교통",
    "쇼핑",
    "게임",
    "배달",
    "취미",
    "기타"
]

st.sidebar.header("➕ 소비 기록")

with st.sidebar.form("expense_form"):
    date = st.date_input("날짜")
    category = st.selectbox("카테고리", categories)
    amount = st.number_input(
        "금액",
        min_value=0,
        step=1000
    )
    memo = st.text_input("메모")

    submitted = st.form_submit_button("기록하기")

    if submitted:
        if amount <= 0:
            st.sidebar.error("금액은 0보다 커야 합니다.")
        else:
            new_row = pd.DataFrame([{
                "날짜": date,
                "카테고리": category,
                "금액": amount,
                "메모": memo
            }])

            st.session_state.expenses = pd.concat(
                [st.session_state.expenses, new_row],
                ignore_index=True
            )

            st.sidebar.success("소비가 기록되었습니다.")

df = st.session_state.expenses

if df.empty:
    st.info("왼쪽에서 소비를 기록해보세요.")
    st.stop()

st.subheader("📋 소비 내역")
st.dataframe(df, use_container_width=True)

# 소비왕
st.subheader("🏆 가장 많이 사용한 항목")

category_sum = df.groupby("카테고리")["금액"].sum()

top_category = category_sum.idxmax()
top_amount = category_sum.max()

st.success(
    f"이번 달 소비왕은 '{top_category}' "
    f"({top_amount:,.0f}원) 입니다."
)

# 파이차트
st.subheader("🥧 카테고리별 소비 비율")

fig1, ax1 = plt.subplots()

ax1.pie(
    category_sum,
    labels=category_sum.index,
    autopct="%1.1f%%"
)

ax1.axis("equal")

st.pyplot(fig1)

# 월간 소비 통계
st.subheader("📊 월간 소비 통계")

df["날짜"] = pd.to_datetime(df["날짜"])

monthly = (
    df.groupby(df["날짜"].dt.strftime("%Y-%m"))["금액"]
    .sum()
)

fig2, ax2 = plt.subplots()

monthly.plot(
    kind="bar",
    ax=ax2
)

ax2.set_ylabel("금액(원)")
ax2.set_xlabel("월")

st.pyplot(fig2)

# 기본 잔소리
def basic_nag(data):
    sums = data.groupby("카테고리")["금액"].sum()

    messages = []

    if sums.get("카페", 0) >= 50000:
        messages.append(
            "☕ 커피값이 꽤 쌓였어요. 집 커피도 사랑해주세요."
        )

    if sums.get("게임", 0) >= 100000:
        messages.append(
            "🎮 게임은 재밌지만 통장 경험치도 챙겨야 해요."
        )

    if sums.get("배달", 0) >= 100000:
        messages.append(
            "🍔 배달앱과 너무 가까워진 것 같아요."
        )

    if sums.get("쇼핑", 0) >= 150000:
        messages.append(
            "🛍️ 장바구니를 다시 한 번 확인해볼까요?"
        )

    if not messages:
        messages.append(
            "👏 지금 소비 패턴은 비교적 건강해 보여요!"
        )

    return "\n".join(messages)

st.subheader("🤖 AI 잔소리")

api_key = st.secrets.get("GEMINI_API_KEY", "")

if api_key:
    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            "gemini-2.5-flash-lite"
        )

        summary = (
            df.groupby("카테고리")["금액"]
            .sum()
            .to_dict()
        )

        prompt = f"""
다음 소비 내역을 보고
재치 있고 귀여운 잔소리를 3줄 이내로 작성해줘.

소비 내역:
{summary}

절약 팁도 하나 포함해줘.
"""

        response = model.generate_content(prompt)

        st.warning(response.text)

    except Exception:
        st.warning(
            "AI 잔소리를 불러오지 못해 기본 잔소리를 제공합니다."
        )
        st.warning(basic_nag(df))

else:
    st.info(
        "GEMINI_API_KEY가 없어 기본 잔소리를 제공합니다."
    )
    st.warning(basic_nag(df))

# CSV 다운로드
st.subheader("⬇️ 소비 내역 다운로드")

csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="CSV 다운로드",
    data=csv,
    file_name="expenses.csv",
    mime="text/csv"
)

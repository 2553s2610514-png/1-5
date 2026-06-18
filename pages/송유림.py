import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import google.generativeai as genai

st.set_page_config(
    page_title="AI 잔소리 가계부",
    page_icon="💸",
    layout="wide"
)

st.title("💸 AI 잔소리 가계부")
st.caption("소비할 때마다 AI가 당신의 통장을 대신 걱정해드립니다.")

# 세션 상태 초기화
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# 기본 잔소리
def basic_nagging(category, item, amount):
    messages = [
        f"'{item}'에 {amount:,}원을 썼네요. 정말 필요한 소비였나요?",
        f"{category} 지출 {amount:,}원! 미래의 당신이 울고 있을지도 몰라요.",
        f"통장은 다 기억합니다. '{item}' {amount:,}원 소비 완료.",
        f"{amount:,}원... 작은 금액 같지만 모이면 큰돈이에요.",
        f"오늘의 소비 '{item}'! 한 번 더 생각해볼 걸 그랬나요?"
    ]

    return messages[amount % len(messages)]


# Gemini 잔소리
def gemini_nagging(category, item, amount):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")

        if not api_key:
            return basic_nagging(category, item, amount)

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        prompt = f"""
사용자가 소비를 했습니다.

카테고리: {category}
항목: {item}
금액: {amount}원

20자~50자의 재치 있고 귀여운 잔소리를 한국어로 작성하세요.
"""

        response = model.generate_content(prompt)

        text = response.text.strip()

        if text:
            return text

    except Exception:
        pass

    return basic_nagging(category, item, amount)


# 소비 입력
st.header("📝 소비 입력")

with st.form("expense_form"):
    col1, col2 = st.columns(2)

    with col1:
        expense_date = st.date_input("날짜", value=date.today())

        category = st.selectbox(
            "카테고리",
            ["식비", "카페", "교통", "쇼핑", "취미", "교육", "생활", "기타"]
        )

    with col2:
        item = st.text_input("항목명")

        amount = st.number_input(
            "금액(원)",
            min_value=0,
            step=1000
        )

    submitted = st.form_submit_button("소비 등록")

    if submitted:
        if item.strip() == "":
            st.warning("항목명을 입력해주세요.")
        elif amount <= 0:
            st.warning("금액은 0원보다 커야 합니다.")
        else:
            nagging = gemini_nagging(category, item, int(amount))

            st.session_state.expenses.append({
                "날짜": expense_date,
                "카테고리": category,
                "항목": item,
                "금액": int(amount)
            })

            st.success("소비가 등록되었습니다.")
            st.info("🤖 AI 잔소리")
            st.write(nagging)


# 데이터프레임 생성
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)

    st.header("📋 소비 내역")
    st.dataframe(df, use_container_width=True)

    # 가장 많이 사용한 항목
    st.header("🏆 가장 큰 소비")

    max_row = df.loc[df["금액"].idxmax()]

    st.metric(
        label=max_row["항목"],
        value=f"{max_row['금액']:,}원",
        delta=max_row["카테고리"]
    )

    # 카테고리 비율
    st.header("🥧 카테고리별 소비 비율")

    category_sum = df.groupby("카테고리")["금액"].sum()

    fig1, ax1 = plt.subplots()

    ax1.pie(
        category_sum,
        labels=category_sum.index,
        autopct="%1.1f%%"
    )

    ax1.axis("equal")

    st.pyplot(fig1)

    # 월간 소비 통계
    st.header("📊 월간 소비 통계")

    df["날짜"] = pd.to_datetime(df["날짜"])

    df["월"] = df["날짜"].dt.strftime("%Y-%m")

    monthly = df.groupby("월")["금액"].sum()

    fig2, ax2 = plt.subplots()

    ax2.bar(monthly.index, monthly.values)

    ax2.set_ylabel("금액(원)")
    ax2.set_xlabel("월")

    plt.xticks(rotation=45)

    st.pyplot(fig2)

    # 총 소비
    st.header("💰 총 소비")

    st.metric(
        "누적 소비 금액",
        f"{df['금액'].sum():,}원"
    )

    # 초기화
    if st.button("전체 소비 내역 삭제"):
        st.session_state.expenses = []
        st.success("모든 소비 내역이 삭제되었습니다.")
        st.rerun()

else:
    st.info("아직 등록된 소비 내역이 없습니다.")

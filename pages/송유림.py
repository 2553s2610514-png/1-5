import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(
    page_title="스마트 소비 분석 가계부",
    page_icon="💰",
    layout="wide"
)

st.title("💰 스마트 소비 분석 가계부")
st.write("소비 내역을 기록하고 나의 소비 습관을 분석해보세요.")

# 세션 상태 초기화
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["날짜", "카테고리", "금액", "메모"]
    )

# 사이드바 입력
st.sidebar.header("➕ 소비 내역 입력")

date = st.sidebar.date_input("날짜")

category = st.sidebar.selectbox(
    "카테고리",
    ["식비", "교통", "쇼핑", "문화", "생활", "교육", "기타"]
)

amount = st.sidebar.number_input(
    "금액(원)",
    min_value=0,
    step=1000
)

memo = st.sidebar.text_input("메모")

if st.sidebar.button("추가"):
    try:
        if amount <= 0:
            st.sidebar.error("금액은 0원보다 커야 합니다.")
        else:
            new_data = pd.DataFrame({
                "날짜": [date],
                "카테고리": [category],
                "금액": [amount],
                "메모": [memo]
            })

            st.session_state.expenses = pd.concat(
                [st.session_state.expenses, new_data],
                ignore_index=True
            )

            st.sidebar.success("소비 내역이 추가되었습니다.")

    except Exception as e:
        st.sidebar.error(f"오류 발생: {e}")

df = st.session_state.expenses

# 데이터 표시
st.header("📋 소비 내역")

if df.empty:
    st.info("아직 등록된 소비 내역이 없습니다.")
else:
    st.dataframe(df, use_container_width=True)

    total = df["금액"].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("총 소비 금액", f"{total:,.0f} 원")

    with col2:
        top_category = (
            df.groupby("카테고리")["금액"]
            .sum()
            .idxmax()
        )

        top_amount = (
            df.groupby("카테고리")["금액"]
            .sum()
            .max()
        )

        st.metric(
            "가장 많이 사용한 항목",
            f"{top_category}",
            f"{top_amount:,.0f} 원"
        )

    # 카테고리별 소비 비율
    st.header("🥧 카테고리별 소비 비율")

    category_sum = (
        df.groupby("카테고리")["금액"]
        .sum()
    )

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

    temp = df.copy()

    temp["날짜"] = pd.to_datetime(temp["날짜"])

    temp["월"] = temp["날짜"].dt.strftime("%Y-%m")

    monthly = (
        temp.groupby("월")["금액"]
        .sum()
        .sort_index()
    )

    fig2, ax2 = plt.subplots()

    monthly.plot(
        kind="bar",
        ax=ax2
    )

    ax2.set_ylabel("금액(원)")
    ax2.set_xlabel("월")

    st.pyplot(fig2)

    # CSV 다운로드
    st.header("⬇️ 데이터 다운로드")

    csv = df.to_csv(index=False)

    st.download_button(
        label="CSV 다운로드",
        data=csv,
        file_name="expenses.csv",
        mime="text/csv"
    )

    # 데이터 초기화
    st.header("🗑️ 데이터 관리")

    if st.button("모든 데이터 삭제"):
        st.session_state.expenses = pd.DataFrame(
            columns=["날짜", "카테고리", "금액", "메모"]
        )
        st.success("모든 데이터가 삭제되었습니다.")
        st.rerun()

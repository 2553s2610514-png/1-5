import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="스마트 소비 분석 가계부",
    page_icon="💰",
    layout="wide"
)

st.title("💰 스마트 소비 분석 가계부")
st.write("소비 내역을 기록하고 소비 패턴을 분석해보세요.")

REQUIRED_COLUMNS = ["날짜", "카테고리", "금액", "메모"]


def create_empty_df():
    return pd.DataFrame(columns=REQUIRED_COLUMNS)


# 세션 상태 초기화
if "expenses" not in st.session_state:
    st.session_state.expenses = create_empty_df()

# 잘못된 데이터 복구
if (
    not isinstance(st.session_state.expenses, pd.DataFrame)
    or not all(
        col in st.session_state.expenses.columns
        for col in REQUIRED_COLUMNS
    )
):
    st.session_state.expenses = create_empty_df()

df = st.session_state.expenses

# ----------------------
# 소비 입력
# ----------------------
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
    if amount <= 0:
        st.sidebar.error("금액은 0보다 커야 합니다.")
    else:
        new_row = pd.DataFrame({
            "날짜": [date],
            "카테고리": [category],
            "금액": [amount],
            "메모": [memo]
        })

        st.session_state.expenses = pd.concat(
            [st.session_state.expenses, new_row],
            ignore_index=True
        )

        st.sidebar.success("소비 내역이 추가되었습니다.")
        st.rerun()

df = st.session_state.expenses.copy()

# 금액 숫자 변환
df["금액"] = pd.to_numeric(
    df["금액"],
    errors="coerce"
)

# 숫자가 아닌 금액 제거
df = df.dropna(subset=["금액"])

# ----------------------
# 소비 내역
# ----------------------
st.header("📋 소비 내역")

if df.empty:
    st.info("등록된 소비 내역이 없습니다.")

else:
    st.dataframe(df, use_container_width=True)

    # 총 소비 금액
    total = df["금액"].sum()

    st.header("📌 소비 요약")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "총 소비 금액",
            f"{total:,.0f} 원"
        )

    with col2:
        category_total = (
            df.groupby("카테고리")["금액"]
            .sum()
        )

        if not category_total.empty:
            st.metric(
                "가장 많이 사용한 항목",
                category_total.idxmax(),
                f"{category_total.max():,.0f} 원"
            )

    # ----------------------
    # 카테고리별 소비 비율
    # ----------------------
    st.header("🥧 카테고리별 소비 비율")

    category_total = (
        df.groupby("카테고리")["금액"]
        .sum()
    )

    category_total = category_total[
        category_total > 0
    ]

    if category_total.empty:
        st.info("파이 차트를 표시할 데이터가 없습니다.")
    else:
        fig1, ax1 = plt.subplots()

        ax1.pie(
            category_total.values,
            labels=category_total.index,
            autopct="%1.1f%%"
        )

        ax1.axis("equal")

        st.pyplot(fig1)

    # ----------------------
    # 월간 소비 통계
    # ----------------------
    st.header("📊 월간 소비 통계")

    temp = df.copy()

    temp["날짜"] = pd.to_datetime(
        temp["날짜"],
        errors="coerce"
    )

    temp = temp.dropna(subset=["날짜"])

    if temp.empty:
        st.info("월간 통계를 표시할 데이터가 없습니다.")
    else:
        temp["월"] = temp["날짜"].dt.strftime("%Y-%m")

        monthly = (
            temp.groupby("월")["금액"]
            .sum()
            .sort_index()
        )

        if monthly.empty:
            st.info("월간 통계를 표시할 데이터가 없습니다.")
        else:
            fig2, ax2 = plt.subplots()

            monthly.plot(
                kind="bar",
                ax=ax2
            )

            ax2.set_xlabel("월")
            ax2.set_ylabel("금액(원)")

            st.pyplot(fig2)

    # ----------------------
    # CSV 다운로드
    # ----------------------
    st.header("⬇️ CSV 다운로드")

    csv = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "CSV 다운로드",
        data=csv,
        file_name="expenses.csv",
        mime="text/csv"
    )

    # ----------------------
    # 데이터 초기화
    # ----------------------
    st.header("🗑️ 데이터 관리")

    if st.button("모든 데이터 삭제"):
        st.session_state.expenses = create_empty_df()
        st.success("모든 데이터가 삭제되었습니다.")
        st.rerun()

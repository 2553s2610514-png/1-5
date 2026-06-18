import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from datetime import date

st.set_page_config(
    page_title="똑똑한 소비 분석 가계부",
    page_icon="💰",
    layout="wide"
)

st.title("💰 똑똑한 소비 분석 가계부")
st.write("소비 내역을 입력하고 나의 소비 습관을 분석해보세요.")

# 세션 상태 초기화
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["날짜", "카테고리", "항목", "금액"]
    )

# 사이드바 입력
st.sidebar.header("소비 내역 입력")

expense_date = st.sidebar.date_input("날짜", value=date.today())

category = st.sidebar.selectbox(
    "카테고리",
    ["식비", "교통", "쇼핑", "문화", "생활", "교육", "기타"]
)

item = st.sidebar.text_input("항목명")

amount = st.sidebar.number_input(
    "금액(원)",
    min_value=0,
    step=1000
)

if st.sidebar.button("추가"):
    try:
        if item.strip() == "":
            st.sidebar.error("항목명을 입력해주세요.")
        elif amount <= 0:
            st.sidebar.error("금액은 0원보다 커야 합니다.")
        else:
            new_row = pd.DataFrame({
                "날짜": [expense_date],
                "카테고리": [category],
                "항목": [item],
                "금액": [amount]
            })

            st.session_state.expenses = pd.concat(
                [st.session_state.expenses, new_row],
                ignore_index=True
            )

            st.sidebar.success("소비 내역이 추가되었습니다.")

    except Exception as e:
        st.sidebar.error(f"오류 발생: {e}")

df = st.session_state.expenses

st.subheader("📋 소비 내역")

if df.empty:
    st.info("아직 입력된 소비 내역이 없습니다.")
else:
    st.dataframe(df, use_container_width=True)

    total = int(df["금액"].sum())

    st.metric("총 소비 금액", f"{total:,}원")

    # 가장 많이 사용한 항목
    st.subheader("🏆 가장 많이 사용한 항목")

    top_item = (
        df.groupby("항목")["금액"]
        .sum()
        .sort_values(ascending=False)
    )

    item_name = top_item.index[0]
    item_amount = int(top_item.iloc[0])

    st.success(
        f"가장 많이 소비한 항목은 '{item_name}' ({item_amount:,}원) 입니다."
    )

    col1, col2 = st.columns(2)

    # 카테고리별 소비 비율
    with col1:
        st.subheader("🥧 카테고리별 소비 비율")

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
    with col2:
        st.subheader("📊 월간 소비 통계")

        temp = df.copy()

        temp["날짜"] = pd.to_datetime(temp["날짜"])

        temp["월"] = temp["날짜"].dt.strftime("%Y-%m")

        monthly = (
            temp.groupby("월")["금액"]
            .sum()
        )

        fig2, ax2 = plt.subplots()

        ax2.bar(monthly.index, monthly.values)

        ax2.set_xlabel("월")
        ax2.set_ylabel("금액(원)")
        ax2.tick_params(axis="x", rotation=45)

        st.pyplot(fig2)

    # CSV 다운로드
    st.subheader("⬇️ 데이터 다운로드")

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="CSV 다운로드",
        data=csv,
        file_name="expense_data.csv",
        mime="text/csv"
    )

import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(
    page_title="소비 기록장",
    page_icon="💰",
    layout="centered"
)

DATA_FILE = "expenses.csv"


# 데이터 불러오기
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_csv(DATA_FILE)
        else:
            return pd.DataFrame(
                columns=["날짜", "카테고리", "금액", "메모"]
            )
    except Exception:
        return pd.DataFrame(
            columns=["날짜", "카테고리", "금액", "메모"]
        )


# 데이터 저장
def save_data(df):
    try:
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception:
        return False


st.title("💰 소비 기록장")

df = load_data()

st.subheader("소비 내역 입력")

with st.form("expense_form"):
    expense_date = st.date_input(
        "날짜",
        value=date.today()
    )

    category = st.selectbox(
        "카테고리",
        [
            "식비",
            "교통",
            "쇼핑",
            "문화생활",
            "주거",
            "의료",
            "기타"
        ]
    )

    amount = st.number_input(
        "금액(원)",
        min_value=0,
        step=1000
    )

    memo = st.text_input(
        "메모(선택)"
    )

    submit = st.form_submit_button("저장")

    if submit:
        try:
            new_row = pd.DataFrame({
                "날짜": [expense_date],
                "카테고리": [category],
                "금액": [amount],
                "메모": [memo]
            })

            df = pd.concat(
                [df, new_row],
                ignore_index=True
            )

            if save_data(df):
                st.success("소비 내역이 저장되었습니다.")
                st.rerun()
            else:
                st.error("저장 중 오류가 발생했습니다.")

        except Exception as e:
            st.error(f"오류 발생: {e}")

st.divider()

st.subheader("📊 소비 현황")

if not df.empty:
    total_amount = int(df["금액"].sum())

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "총 지출 금액",
            f"{total_amount:,}원"
        )

    with col2:
        st.metric(
            "기록 수",
            len(df)
        )

else:
    st.info("저장된 소비 내역이 없습니다.")

st.divider()

st.subheader("📋 소비 내역")

if not df.empty:
    st.dataframe(
        df.sort_values("날짜", ascending=False),
        use_container_width=True
    )

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="CSV 다운로드",
        data=csv,
        file_name="expenses.csv",
        mime="text/csv"
    )

    if st.button("전체 삭제"):
        try:
            empty_df = pd.DataFrame(
                columns=["날짜", "카테고리", "금액", "메모"]
            )
            save_data(empty_df)
            st.success("모든 데이터가 삭제되었습니다.")
            st.rerun()

        except Exception as e:
            st.error(f"삭제 오류: {e}")

else:
    st.info("아직 저장된 소비 내역이 없습니다.")

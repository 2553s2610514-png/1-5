import streamlit as st
import pandas as pd
import random
import importlib.util
import os

# --- 1. 페이지 초기 설정 ---
st.set_page_config(
    page_title="AI 잔소리 가계부 - 홈",
    page_icon="💸",
    layout="centered"
)

# --- 2. 임시 데이터 (대시보드 출력용) ---
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame([
        {"날짜": "2026-06-01", "내역": "스타벅스", "금액": 6000},
        {"날짜": "2026-06-05", "내역": "택시비", "금액": 15000},
        {"날짜": "2026-06-12", "내역": "치킨 배달", "금액": 28000},
    ])

if 'budget' not in st.session_state:
    st.session_state.budget = 500000 

# --- 3. 현재 활성화된 메뉴 상태 관리 ---
if 'current_menu' not in st.session_state:
    st.session_state.current_menu = "🏠 메인 홈 / 소비 요약"

# --- 4. 소비 요약 계산 및 AI 잔소리 ---
total_spent = st.session_state.expenses["금액"].sum()
remaining = st.session_state.budget - total_spent
ratio = total_spent / st.session_state.budget

def get_nagging_message(ratio):
    if ratio < 0.5: return "🙄 통장이 아직 숨은 쉬네요. 언제 지를지 내가 지켜보고 있습니다."
    elif ratio < 0.9: return "⚠️ 슬슬 시동 걸리죠? 지금 긁으려는 그 카드 당장 내려놓으세요."
    else: return "🚨 파산 직전! 통장이 아니라 텅장입니다. 당장 숨만 쉬고 사세요!!"


# --- 5. 안전하게 다른 팀원 코드를 불러오는 헬퍼 함수 ---
def run_team_page(file_name, page_title):
    file_path = f"pages/{file_name}"
    
    # 홈으로 돌아가는 버튼 상단 배정
    if st.button("⬅️ 메인 홈으로 돌아가기"):
        st.session_state.current_menu = "🏠 메인 홈 / 소비 요약"
        st.rerun()
    st.write("---")

    if os.path.exists(file_path):
        try:
            spec = importlib.util.spec_from_file_location("mod", file_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            st.error(f"🚨 {page_title} 페이지 코드 내부에 에러가 있습니다!")
            st.exception(e)
    else:
        st.warning(f"⚠️ `pages/{file_name}` 파일이 아직 깃허브에 없습니다. 팀원이 업로드하면 활성화됩니다!")


# --- 6. 사이드바 내비게이션 (메인과 연동) ---
st.sidebar.title("📌 메뉴 내비게이션")
selected_sidebar = st.sidebar.radio(
    "메뉴 선택:",
    ["🏠 메인 홈 / 소비 요약", "📊 소비분석", "📝 소비기록", "🤖 AI 잔소리", "🌱 절약활동"],
    index=["🏠 메인 홈 / 소비 요약", "📊 소비분석", "📝 소비기록", "🤖 AI 잔소리", "🌱 절약활동"].index(st.session_state.current_menu)
)
if selected_sidebar != st.session_state.current_menu:
    st.session_state.current_menu = selected_sidebar
    st.rerun()


# --- 7. 화면 조건문 처리 (새로운 영어 파일명 적용 완료) ---

# [화면 1] 메인 대시보드 홈
if st.session_state.current_menu == "🏠 메인 홈 / 소비 요약":
    st.title("💸 AI 잔소리 가계부")
    st.markdown("### 이번 달 소비 현황 요약")
    st.write("---")

    # 상단 요약 카드
    col1, col2, col3 = st.columns(3)
    col1.metric("총 지출액", f"{total_spent:,} 원")
    col2.metric("설정 예산", f"{st.session_state.budget:,} 원")
    col3.metric("남은 금액", f"{remaining:,} 원", delta=f"-{total_spent:,}원")

    st.progress(min(1.0, float(ratio)))
    st.caption(f"현재 예산 대비 **{ratio*100:.1f}%** 사용 중입니다.")

    st.write("---")
    st.subheader("🤖 AI 가디언의 잔소리 한마디")
    nagging_msg = get_nagging_message(ratio)
    if ratio >= 0.9: st.error(nagging_msg)
    elif ratio >= 0.5: st.warning(nagging_msg)
    else: st.success(nagging_msg)

    st.write("---")

    # 메인 화면 버튼 형식 메뉴
    st.subheader("🛠️ 다른 기능으로 이동")
    st.write("원하는 기능 버튼을 클릭하면 해당 페이지 화면으로 즉시 전환됩니다.")

    menu_col1, menu_col2 = st.columns(2)

    with menu_col1:
        st.info("📊 소비 패턴을 분석하고 싶나요?")
        if st.button("📊 소비분석 페이지로 이동", use_container_width=True):
            st.session_state.current_menu = "📊 소비분석"
            st.rerun()

        st.write("") 
        
        st.info("🔥 건별 잔소리 폭격을 맞고 싶나요?")
        if st.button("🤖 AI 잔소리 페이지로 이동", use_container_width=True):
            st.session_state.current_menu = "🤖 AI 잔소리"
            st.rerun()

    with menu_col2:
        st.info("📝 새로운 소비를 기록하고 싶나요?")
        if st.button("📝 소비기록 페이지로 이동", use_container_width=True):
            st.session_state.current_menu = "📝 소비기록"
            st.rerun()

        st.write("") 

        st.info("🌱 절약 활동 미션을 확인해볼까요?")
        if st.button("🌱 절약활동 페이지로 이동", use_container_width=True):
            st.session_state.current_menu = "🌱 절약활동"
            st.rerun()

# [화면 2] 소비분석 페이지 전환 (송유림 -> report.py)
elif st.session_state.current_menu == "📊 소비분석":
    st.title("📊 소비분석")
    run_team_page("report.py", "소비분석")

# [화면 3] 소비기록 페이지 전환 (안시윤 -> expensive.py)
elif st.session_state.current_menu == "📝 소비기록":
    st.title("📝 소비기록")
    run_team_page("expensive.py", "소비기록")

# [화면 4] AI 잔소리 페이지 전환 (김유민 -> scold.py)
elif st.session_state.current_menu == "🤖 AI 잔소리":
    st.title("🤖 AI 잔소리")
    run_team_page("scold.py", "AI 잔소리")

# [화면 5] 절약활동 페이지 전환 (정선아 -> challenge.py)
elif st.session_state.current_menu == "🌱 절약활동":
    st.title("🌱 절약활동")
    run_team_page("challenge.py", "절약활동")

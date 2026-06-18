
import streamlit as st
import google.generativeai as genai
import json
import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="지갑 수호자: AI 절약 챌린지",
    page_icon="💰",
    layout="centered"
)

# 2. Gemini API 키 및 클라이언트 설정
if "GEMINI_API_KEY" in st.secrets:GEMINI_API_KEY = "YOUR_ACTUAL_API_KEY"
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("GEMINI_API_KEY = " "YOUR_ACTUAL_API_KEY""")
    st.stop()

# 3. 세션 상태(Session State) 초기화 (데이터 휘발 방지)
if "total_saved" not in st.session_state:
    st.session_state.total_saved = 0
if "saved_log" not in st.session_state:
    st.session_state.saved_log = []
if "daily_missions" not in st.session_state:
    # 기본 미션 구성 (API 호출 실패 시 백업용 겸 초기 데이터)
    st.session_state.daily_missions = [
        {"task": "카페 커피 대신 탕비실/집 커피 마시기", "cost": 5000, "done": False},
        {"task": "배달 앱 대신 냉장고에 있는 재료로 요리하기", "cost": 20000, "done": False},
        {"task": "가까운 거리는 대중교통 대신 걷기", "cost": 1500, "done": False}
    ]

# AI 텍스트 생성 공통 함수
def get_ai_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"🚨 AI 연결에 실패했습니다. (오류: {str(e)})"

# --- 화면 구현 ---
st.title("💰 지갑 수호자: AI 절약 챌린지")
st.markdown("돈을 함부로 쓰려는 나 자신을 제어하고, AI와 함께 건강한 절약 습관을 만들어보세요!")
st.markdown("---")

# 대시보드 - 누적 절약 금액 표시
st.subheader("📊 오늘의 내 절약 저금통")
st.metric(label="지금까지 아낀 총 금액", value=f"{st.session_state.total_saved:,} 원")
st.markdown("---")

# 탭 구조 설계 (기능별 분리)
tab1, tab2, tab3 = st.tabs(["📅 오늘의 절약 행동", "🚨 지름신 방어막", "📝 절약 히스토리"])

# --- TAB 1: 오늘의 절약 행동 (핵심 요청 기능) ---
with tab1:
    st.header("💡 AI 추천 오늘의 절약 행동")
    st.write("AI가 제안하는 미션을 달성하고 체크박스를 눌러 지갑을 지키세요!")
    
    # 새로운 미션 생성 버튼
    if st.button("🔄 새로운 AI 맞춤 미션 받기"):
        with st.spinner("AI가 오늘의 절약 미션을 짜는 중입니다..."):
            prompt = """
            일상생활에서 직장인이나 대학생이 실천할 수 있는 돈 아끼는 행동 3가지를 추천해줘.
            반드시 아래 예시와 같은 순수한 JSON 배열 형식으로만 답변해줘. 서론이나 코드 블록(```json 등)은 절대 포함하지 마.
            [
                {"task": "미션 내용 1", "cost": 4000},
                {"task": "미션 내용 2", "cost": 15000},
                {"task": "미션 내용 3", "cost": 2000}
            ]
            """
            ai_output = get_ai_response(prompt)
            
            # JSON 파싱 및 예외 처리
            try:
                # 마크다운 서식 등이 들어갔을 경우를 대비한 정제
                clean_json = ai_output.replace("```json", "").replace("```", "").strip()
                parsed_missions = json.loads(clean_json)
                
                # 상태 업데이트
                st.session_state.daily_missions = [
                    {"task": m["task"], "cost": int(m["cost"]), "done": False} for m in parsed_missions
                ]
                st.success("새로운 미션이 생성되었습니다!")
            except Exception:
                st.error("AI 미션을 불러오는 중 형식이 맞지 않아 기본 미션으로 대체합니다.")
    
    st.markdown("### 오늘의 미션 체크리스트")
    # 체크박스 리스트 렌더링
    for idx, item in enumerate(st.session_state.daily_missions):
        # 이미 완료된 미션인지 여부 확인
        disabled = item["done"]
        
        # 각 미션별로 고유한 key 부여
        checked = st.checkbox(
            f"{item['task']} (예상 절약: +{item['cost']:,}원)", 
            value=item["done"], 
            key=f"mission_{idx}",
            disabled=disabled
        )
        
        # 사용자가 새로 체크했을 때 동작
        if checked and not item["done"]:
            st.session_state.daily_missions[idx]["done"] = True
            st.session_state.total_saved += item["cost"]
            st.session_state.saved_log.append({
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "detail": f"🎯 [미션 달성] {item['task']}",
                "money": item["cost"]
            })
            st.toast(f"🎉 {item['cost']:,}원 절약 성공!")
            st.rerun()

# --- TAB 2: 지름신 방어막 (추가 차별화 기능) ---
with tab2:
    st.header("🚨 살까 말까 고민될 땐? AI 잔소리!")
    st.write("지금 결제하려는 물건과 금액을 적어보세요. AI가 뼈 때리는 잔소리로 막아드립니다.")
    
    wish_item = st.text_input("소비 고민 중인 항목", placeholder="예: 야식으로 치킨 시키기, 신상 운동화 구매")
    wish_price = st.number_input("예상 금액 (원)", min_value=0, step=1000, value=0)
    
    if st.button("⚡ 정신 차리게 잔소리 듣기"):
        if not wish_item:
            st.warning("고민 중인 항목을 먼저 입력해 주세요!")
        else:
            with st.spinner("AI가 팩트 폭행을 장전 중입니다..."):
                prompt = f"""
                사용자가 현재 '{wish_item}'에 {wish_price:,}원을 지출할지 고민하고 있습니다.
                이 지출을 막을 수 있도록 냉정하고 현실적이면서도 약간의 유머가 섞인 잔소리를 해주세요.
                상황에 맞는 이모지를 적극 활용하고, 반말과 존댓말을 섞어 친구처럼 따끔하게 3줄 이내로 말해주세요.
                """
                nag_reply = get_ai_response(prompt)
                st.chat_message("assistant").write(nag_reply)
                
                if wish_price > 0:
                    st.markdown("---")
                    st.write("💡 **AI의 말을 듣고 마음을 접으셨나요?**")
                    if st.button("🙌 안 사고 참았다! (돈 아끼기)"):
                        st.session_state.total_saved += wish_price
                        st.session_state.saved_log.append({
                            "date": datetime.date.today().strftime("%Y-%m-%d"),
                            "detail": f"🛡️ [소비 방어] {wish_item}",
                            "money": wish_price
                        })
                        st.success(f"참 잘하셨습니다! {wish_price:,}원이 저금통에 적립되었습니다.")
                        st.rerun()

# --- TAB 3: 절약 히스토리 ---
with tab3:
    st.header("📝 나의 절약 영웅담")
    
    if not st.session_state.saved_log:
        st.info("아직 기록된 절약 활동이 없습니다. 오늘부터 하나씩 시작해 보세요!")
    else:
        for log in reversed(st.session_state.saved_log):
            st.write(f"📅 **{log['date']}** | {log['detail']} | 💸 `+{log['money']:,}원` 아낌")
            
        st.markdown("---")
        if st.button("🗑️ 모든 기록 초기화"):
            st.session_state.total_saved = 0
            st.session_state.saved_log = []
            st.success("기록이 성공적으로 초기화되었습니다.")
            st.rerun()

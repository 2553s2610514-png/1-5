import random
import streamlit as st

st.set_page_config(page_title="식사 추천기", page_icon="🍚")

st.title("🍚 오늘 뭐 먹지?")
st.write("버튼을 누르면 식사를 추천해줘요!")

foods = [
    "김치찌개",
    "비빔밥",
    "치킨",
    "떡볶이",
    "햄버거",
    "파스타",
    "초밥",
    "라면",
    "삼겹살",
    "돈까스"
]

if st.button("추천 받기"):
    menu = random.choice(foods)
    st.success(f"오늘의 추천 메뉴는 👉 {menu}")

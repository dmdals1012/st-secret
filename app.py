import streamlit as st
import numpy as np
from functools import reduce
from operator import mul
import pandas as pd

# 필터링할 고정 숫자 집합 (52,55,61,67,73,79,91)
FILTER_NUMBERS = {52, 55, 61, 67, 73, 79, 91}

def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        st.title("🔒 접근 권한")
        password = st.number_input("비밀번호를 입력하세요", format="%d")
        
        if st.button("로그인", use_container_width=True):
            if password == 1234:
                st.session_state.authenticated = True
                st.session_state.filtered_selections = []
                st.session_state.unfiltered_selections = []
                st.rerun()
            else:
                st.error("❌ 잘못된 비밀번호입니다. 다시 시도해주세요.")
        return False
    return True

if check_password():
    # 반드시 세션 상태 변수 초기화!
    if 'filtered_selections' not in st.session_state:
        st.session_state.filtered_selections = []
    if 'unfiltered_selections' not in st.session_state:
        st.session_state.unfiltered_selections = []

    # 공통 입력 칸
    cols = st.columns(6)
    inputs = []
    for i in range(6):
        with cols[i]:
            input_str = st.text_input(
                f"{i+1}번째 숫자", 
                placeholder="쉼표로 구분 (예: 1,5,10)",
                key=f"col_{i}"
            )
            try:
                numbers = sorted({int(n.strip()) for n in input_str.split(',') if n.strip()})
            except:
                numbers = []
            inputs.append(numbers)

    max_combinations = reduce(mul, [len(col) for col in inputs if len(col) > 0], 1) if all(len(col) > 0 for col in inputs) else 0
    
    # 탭 생성
    tab1, tab2 = st.tabs(["🔍 필터 적용 버전", "🎲 일반 버전"])
    
    # 필터 적용 탭
    with tab1:
        
        count_filtered = st.number_input(
            "생성할 조합 수 (필터)", 
            min_value=1, 
            max_value=10000,
            value=5,
            key="count_filtered"
        )

        if st.button("🎲 필터 적용 생성", key="btn_filtered", use_container_width=True):
            if max_combinations == 0:
                st.error("❗모든 칸에 숫자를 입력해주세요!")
            else:
                valid_combos = []
                attempt = 0
                max_attempts = count_filtered * 10
                
                while len(valid_combos) < count_filtered and attempt < max_attempts:
                    combo = tuple(sorted([np.random.choice(col) for col in inputs]))
                    filter_count = sum(1 for num in combo if num in FILTER_NUMBERS)
                    
                    if filter_count <= 1 and combo not in valid_combos:
                        valid_combos.append(combo)
                    attempt += 1
                
                st.session_state.filtered_selections = valid_combos
                st.success(f"✅ {len(valid_combos)}개 유효 조합 생성")

        if st.session_state.filtered_selections:
            df_filtered = pd.DataFrame(
                st.session_state.filtered_selections,
                columns=[f"번호{i+1}" for i in range(6)]
            )
            
            st.dataframe(df_filtered.style.format("{:02d}"), height=400)
            
            csv_filtered = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 필터 데이터 다운로드",
                data=csv_filtered,
                file_name="filtered_lotto.csv",
                mime="text/csv",
                use_container_width=True
            )

    # 일반 버전 탭
    with tab2:

        
        count_unfiltered = st.number_input(
            "생성할 조합 수 (일반)", 
            min_value=1, 
            max_value=10000,
            value=5,
            key="count_unfiltered"
        )

        if st.button("🎲 일반 생성", key="btn_unfiltered", use_container_width=True):
            if max_combinations == 0:
                st.error("❗모든 칸에 숫자를 입력해주세요!")
            else:
                valid_combos = []
                attempt = 0
                max_attempts = count_unfiltered * 10
                
                while len(valid_combos) < count_unfiltered and attempt < max_attempts:
                    combo = tuple(sorted([np.random.choice(col) for col in inputs]))
                    if combo not in valid_combos:
                        valid_combos.append(combo)
                    attempt += 1
                
                st.session_state.unfiltered_selections = valid_combos
                st.success(f"✅ {len(valid_combos)}개 조합 생성")

        if st.session_state.unfiltered_selections:
            df_unfiltered = pd.DataFrame(
                st.session_state.unfiltered_selections,
                columns=[f"번호{i+1}" for i in range(6)]
            )
            
            st.dataframe(df_unfiltered.style.format("{:02d}"), height=400)
            
            csv_unfiltered = df_unfiltered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 일반 데이터 다운로드",
                data=csv_unfiltered,
                file_name="unfiltered_lotto.csv",
                mime="text/csv",
                use_container_width=True
            )

    # 로그아웃 버튼 (공통)
    if st.button("🚪 로그아웃", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

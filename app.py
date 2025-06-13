import streamlit as st
import numpy as np
import itertools
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
                st.session_state.selections = []
                st.rerun()
            else:
                st.error("❌ 잘못된 비밀번호입니다. 다시 시도해주세요.")
        return False
    return True

if check_password():
    if 'selections' not in st.session_state:
        st.session_state.selections = []

    def get_max_combinations(inputs):
        lengths = [len(arr) for arr in inputs]
        return reduce(mul, lengths, 1) if 0 not in lengths else 0

    def generate_valid_combinations(inputs, count):
        valid_combos = []
        attempt = 0
        max_attempts = count * 10  # 무한 루프 방지
        
        while len(valid_combos) < count and attempt < max_attempts:
            # 조합 생성
            combo = tuple(sorted([
                np.random.choice(col) 
                for col in inputs
            ]))
            
            # 🔽 필터링 조건 변경 (2개 이상 → 1개 이하)
            filter_count = sum(1 for num in combo if num in FILTER_NUMBERS)
            
            if filter_count <= 1 and combo not in valid_combos:  # 조건 변경
                valid_combos.append(combo)
                
            attempt += 1
            
        return valid_combos

    st.title("🔢 조건부 로또 조합 생성기")

    # 입력 칸
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

    max_combinations = get_max_combinations(inputs)
    st.info(f"🎲 최대 조합 수: **{max_combinations:,}개** (필터 적용 전)")

    count = st.number_input(
        "생성할 조합 수", 
        min_value=1, 
        max_value=10000,
        value=5
    )

    if st.button("🎲 번호 생성하기", use_container_width=True):
        if max_combinations == 0:
            st.error("❗모든 칸에 숫자를 입력해주세요!")
        else:
            valid_combos = generate_valid_combinations(inputs, count)
            st.session_state.selections = valid_combos
            st.success(f"✅ {len(valid_combos)}개 유효 조합 생성")

    if st.session_state.selections:
        df = pd.DataFrame(
            st.session_state.selections,
            columns=[f"번호{i+1}" for i in range(6)]
        )
        
        st.dataframe(df.style.format("{:02d}"), height=400)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name="filtered_lotto.csv",
            mime="text/csv",
            use_container_width=True
        )

    if st.button("🚪 로그아웃", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

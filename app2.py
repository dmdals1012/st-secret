import streamlit as st
import numpy as np
import pandas as pd
import itertools

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

def generate_combinations_with_max_two(nums):
    combs = []
    if len(nums) == 0:
        return []
    combs.extend(itertools.combinations(nums, 1))
    if len(nums) >= 2:
        combs.extend(itertools.combinations(nums, 2))
    return combs

def calc_unique_combinations(inputs):
    """유효 조합 개수만 계산 (최적화)"""
    if not all(len(col) > 0 for col in inputs):
        return 0
    
    count = [0]
    
    def backtrack(col_idx, current_size, used_numbers):
        if col_idx == 6:
            if current_size == 6:
                count[0] += 1
            return
        
        for size in [1, 2]:
            if current_size + size > 6:
                continue
            if current_size + size + (5 - col_idx) < 6:
                continue
                
            for combo in itertools.combinations(inputs[col_idx], size):
                if not any(num in used_numbers for num in combo):
                    backtrack(col_idx + 1, 
                            current_size + size, 
                            used_numbers | set(combo))
    
    backtrack(0, 0, set())
    return count[0]

def generate_unfiltered_combinations(inputs):
    """일반 조합 생성 (최적화)"""
    results = []
    
    def backtrack(col_idx, current_combo, used_numbers):
        if col_idx == 6:
            if len(current_combo) == 6:
                results.append(tuple(current_combo))
            return
        
        for size in [1, 2]:
            if len(current_combo) + size > 6:
                continue
            if len(current_combo) + size + (5 - col_idx) < 6:
                continue
                
            for combo in itertools.combinations(inputs[col_idx], size):
                if not any(num in used_numbers for num in combo):
                    backtrack(col_idx + 1, 
                            current_combo + list(combo), 
                            used_numbers | set(combo))
    
    backtrack(0, [], set())
    return results

def generate_filtered_combinations(inputs):
    """필터 조합 생성 (최적화)"""
    results = []
    
    def backtrack(col_idx, current_combo, used_numbers, filter_count):
        if col_idx == 6:
            if len(current_combo) == 6 and filter_count <= 1:
                results.append(tuple(current_combo))
            return
        
        for size in [1, 2]:
            if len(current_combo) + size > 6:
                continue
            if len(current_combo) + size + (5 - col_idx) < 6:
                continue
                
            for combo in itertools.combinations(inputs[col_idx], size):
                if not any(num in used_numbers for num in combo):
                    new_filter_count = filter_count + sum(1 for n in combo if n in FILTER_NUMBERS)
                    if new_filter_count <= 1:
                        backtrack(col_idx + 1, 
                                current_combo + list(combo), 
                                used_numbers | set(combo),
                                new_filter_count)
    
    backtrack(0, [], set(), 0)
    return results

def main():
    if not check_password():
        return
    
    st.title("로또 조합 생성기 (52,55,61,67,73,79,91 필터링)")
    
    if 'filtered_selections' not in st.session_state:
        st.session_state.filtered_selections = []
    if 'unfiltered_selections' not in st.session_state:
        st.session_state.unfiltered_selections = []
    
    cols = []
    for i in range(6):
        cols.append(st.text_input(f"{i+1}번 칸 숫자 입력 (띄어쓰기로 구분)", key=f"col{i}"))
    
    inputs = []
    for col_str in cols:
        nums = set()
        for x in col_str.split(" "):
            x = x.strip()
            if x.isdigit():
                nums.add(int(x))
        inputs.append(sorted(nums))
    
    st.write("입력 숫자:", inputs)
    
    if st.button("조합 개수 계산"):
        count = calc_unique_combinations(inputs)
        st.write(f"생성 가능한 조합 수: {count}")
    
    tab1, tab2 = st.tabs(["필터링 조합", "일반 조합"])
    
    with tab1:
        if st.button("필터링 조합 생성", key="filter_gen"):
            with st.spinner("조합 생성 중..."):
                filtered_combos = generate_filtered_combinations(inputs)
                st.session_state.filtered_selections = filtered_combos
        
        if len(st.session_state.filtered_selections) > 0:
            st.write(f"필터링된 조합 갯수: {len(st.session_state.filtered_selections)}")
            df = pd.DataFrame(st.session_state.filtered_selections, 
                            columns=[f"숫자{i+1}" for i in range(6)])
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("CSV 다운로드", csv, file_name="filtered_combinations.csv")
    
    with tab2:
        if st.button("일반 조합 생성", key="unfilter_gen"):
            with st.spinner("조합 생성 중..."):
                unfiltered_combos = generate_unfiltered_combinations(inputs)
                st.session_state.unfiltered_selections = unfiltered_combos
        
        if len(st.session_state.unfiltered_selections) > 0:
            st.write(f"일반 조합 갯수: {len(st.session_state.unfiltered_selections)}")
            df = pd.DataFrame(st.session_state.unfiltered_selections, 
                            columns=[f"숫자{i+1}" for i in range(6)])
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("CSV 다운로드", csv, file_name="unfiltered_combinations.csv")
    
    if st.button("로그아웃"):
        st.session_state.authenticated = False
        st.rerun()

if __name__ == "__main__":
    main()

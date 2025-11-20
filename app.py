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
                st.experimental_rerun()
            else:
                st.error("❌ 잘못된 비밀번호입니다. 다시 시도해주세요.")
        return False
    return True

def generate_combinations_with_max_two(nums):
    # 주어진 숫자 리스트에서 1개 또는 2개 숫자 조합 생성 (중복 없이)
    combs = []
    if len(nums) == 0:
        return []
    combs.extend(itertools.combinations(nums, 1))
    if len(nums) >= 2:
        combs.extend(itertools.combinations(nums, 2))
    return combs

def calc_unique_combinations(inputs):
    # inputs: 리스트 6개 (각 칸 숫자 리스트)
    # 각 칸별 1개 또는 2개 숫자 조합 생성 후 6칸 조합 cartesian product
    # 합쳐서 중복 숫자 없이 총 6개 숫자 조합 필터링

    if not all(len(col) > 0 for col in inputs):
        return 0

    # 각 칸에서 1개 또는 2개 숫자 조합 리스트
    combos_per_col = [generate_combinations_with_max_two(col) for col in inputs]

    unique_count = 0
    for prod in itertools.product(*combos_per_col):
        combined = sum(prod, ())  # prod는 6개 튜플, 각각 1~2개 숫자의 튜플, 이들을 합침
        if len(combined) == 6 and len(set(combined)) == 6:
            unique_count += 1
    return unique_count

def generate_filtered_combinations(inputs):
    # 필터 적용된 조합 생성 함수
    combos_per_col = [generate_combinations_with_max_two(col) for col in inputs]
    filtered_results = []
    for prod in itertools.product(*combos_per_col):
        combined = sum(prod, ())
        if len(combined) == 6 and len(set(combined)) == 6:
            # 고정 숫자 필터: 포함된 고정 숫자 갯수 체크
            fixed_count = sum(num in FILTER_NUMBERS for num in combined)
            if fixed_count <= 1:
                filtered_results.append(combined)
    return filtered_results

def generate_unfiltered_combinations(inputs):
    # 필터 없는 조합 생성 함수
    combos_per_col = [generate_combinations_with_max_two(col) for col in inputs]
    results = []
    for prod in itertools.product(*combos_per_col):
        combined = sum(prod, ())
        if len(combined) == 6 and len(set(combined)) == 6:
            results.append(combined)
    return results

def main():
    if not check_password():
        return

    st.title("로또 조합 생성기 (최대 2개 숫자/칸 허용)")

    cols = []
    for i in range(6):
        cols.append(st.text_input(f"{i+1}번 칸 숫자 입력 (쉼표로 구분)", key=f"col{i}"))

    inputs = []
    for col_str in cols:
        nums = set()
        for x in col_str.split(","):
            x = x.strip()
            if x.isdigit():
                nums.add(int(x))
        inputs.append(sorted(nums))

    st.write("입력 숫자:", inputs)

    if st.button("조합 개수 계산"):
        count = calc_unique_combinations(inputs)
        st.write(f"생성 가능한 조합 수: {count}")

    tab1, tab2 = st.tabs(["필터링 조합", "일반 조합"])

    if tab1.button("필터링 조합 생성"):
        filtered_combos = generate_filtered_combinations(inputs)
        st.write(f"필터링된 조합 갯수: {len(filtered_combos)}")
        if len(filtered_combos) > 0:
            df = pd.DataFrame(filtered_combos, columns=[f"칸{i+1}" for i in range(6)])
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("CSV 다운로드", csv, file_name="filtered_combinations.csv")

    if tab2.button("일반 조합 생성"):
        unfiltered_combos = generate_unfiltered_combinations(inputs)
        st.write(f"일반 조합 갯수: {len(unfiltered_combos)}")
        if len(unfiltered_combos) > 0:
            df = pd.DataFrame(unfiltered_combos, columns=[f"칸{i+1}" for i in range(6)])
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("CSV 다운로드", csv, file_name="unfiltered_combinations.csv")

    if st.button("로그아웃"):
        st.session_state.authenticated = False
        st.experimental_rerun()

if __name__ == "__main__":
    main()

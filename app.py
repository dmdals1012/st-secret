import streamlit as st
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

def calc_unique_combinations(inputs):
    all_numbers = set()
    for col in inputs:
        all_numbers.update(col)
    all_numbers = sorted(all_numbers)

    unique_count = 0
    input_sets = [set(col) for col in inputs]

    for combo in itertools.combinations(all_numbers, 6):
        valid = True
        for s in input_sets:
            count = sum(1 for x in combo if x in s)
            if count > 2:
                valid = False
                break
        if valid:
            unique_count += 1
    return unique_count

def generate_filtered_combinations(inputs, sort_each):
    all_numbers = set()
    for col in inputs:
        all_numbers.update(col)
    all_numbers = sorted(all_numbers)

    input_sets = [set(col) for col in inputs]
    results = []

    for combo in itertools.combinations(all_numbers, 6):
        valid = True
        for s in input_sets:
            count = sum(1 for x in combo if x in s)
            if count > 2:
                valid = False
                break
        if valid:
            fixed_count = sum(num in FILTER_NUMBERS for num in combo)
            if fixed_count <= 1:
                if sort_each:
                    results.append(tuple(sorted(combo)))
                else:
                    results.append(combo)
    return results

def generate_unfiltered_combinations(inputs, sort_each):
    all_numbers = set()
    for col in inputs:
        all_numbers.update(col)
    all_numbers = sorted(all_numbers)

    input_sets = [set(col) for col in inputs]
    results = []

    for combo in itertools.combinations(all_numbers, 6):
        valid = True
        for s in input_sets:
            count = sum(1 for x in combo if x in s)
            if count > 2:
                valid = False
                break
        if valid:
            if sort_each:
                results.append(tuple(sorted(combo)))
            else:
                results.append(combo)
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

    sort_each = st.checkbox("조합 내 숫자 오름차순 정렬", value=True)

    if st.button("조합 개수 계산"):
        count = calc_unique_combinations(inputs)
        st.write(f"생성 가능한 조합 수: {count}")

    tab1, tab2 = st.tabs(["필터링 조합", "일반 조합"])

    if tab1.button("필터링 조합 생성"):
        filtered_combos = generate_filtered_combinations(inputs, sort_each)
        st.write(f"필터링된 조합 갯수: {len(filtered_combos)}")
        if len(filtered_combos) > 0:
            df = pd.DataFrame(filtered_combos, columns=[f"숫자{i+1}" for i in range(6)])
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("CSV 다운로드", csv, file_name="filtered_combinations.csv")

    if tab2.button("일반 조합 생성"):
        unfiltered_combos = generate_unfiltered_combinations(inputs, sort_each)
        st.write(f"일반 조합 갯수: {len(unfiltered_combos)}")
        if len(unfiltered_combos) > 0:
            df = pd.DataFrame(unfiltered_combos, columns=[f"숫자{i+1}" for i in range(6)])
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("CSV 다운로드", csv, file_name="unfiltered_combinations.csv")

    if st.button("로그아웃"):
        st.session_state.authenticated = False
        st.rerun()

if __name__ == "__main__":
    main()

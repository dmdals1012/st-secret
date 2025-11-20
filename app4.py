import streamlit as st
import numpy as np
from functools import reduce
from operator import mul
import pandas as pd
import itertools

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

def calc_unique_combinations(inputs):
    """중복 없는 조합 수 계산 함수"""
    if not all(len(col) > 0 for col in inputs):
        return 0
    all_combos = itertools.product(*inputs)
    unique_count = 0
    for combo in all_combos:
        if len(set(combo)) == 6:
            unique_count += 1
    return unique_count

def calc_max_combinations(inputs):
    """기존 곱셈 법칙 계산 함수"""
    return reduce(mul, [len(col) for col in inputs if len(col) > 0], 1) if all(len(col) > 0 for col in inputs) else 0

def main():
    if not check_password():
        return

    # 반드시 세션 상태 변수 초기화!
    if 'filtered_selections' not in st.session_state:
        st.session_state.filtered_selections = []

    if 'unfiltered_selections' not in st.session_state:
        st.session_state.unfiltered_selections = []

    st.title("🎲 로또 조합 생성기")

    # 공통 입력 칸
    cols = st.columns(6)
    inputs = []

    for i in range(6):
        with cols[i]:
            input_str = st.text_input(
                f"{i+1}번째 숫자",
                placeholder="띄어쓰기로 구분 (예: 1 5 10)",
                key=f"col_{i}"
            )
            try:
                numbers = sorted({int(n.strip()) for n in input_str.split(' ') if n.strip()})
            except:
                numbers = []
            inputs.append(numbers)

    # 계산 실행
    total_combinations = calc_max_combinations(inputs)
    unique_combinations = calc_unique_combinations(inputs)

    # 탭 생성
    tab1, tab2 = st.tabs(["🔍 필터 적용 버전", "🎲 일반 버전"])

    # 필터 적용 탭
    with tab1:
        st.info(f"🎲 총 조합 수 (중복 허용): **{total_combinations:,}개**")
        st.info(f"🎲 중복 없는 조합 수: **{unique_combinations:,}개**")

        count_filtered = st.number_input(
            "생성할 조합 수 (필터)",
            min_value=1,
            max_value=unique_combinations if unique_combinations else 1,
            value=min(10, unique_combinations) if unique_combinations else 1,
            key="count_filtered"
        )

        if st.button("🎲 필터 적용 생성", key="btn_filtered", use_container_width=True):
            if unique_combinations == 0:
                st.error("❗모든 칸에 숫자를 입력해주세요!")
            else:
                # 모든 조합 생성
                all_combos = [tuple(sorted(combo)) for combo in itertools.product(*inputs) if len(set(combo)) == 6]
                # 필터 적용
                filtered_combos = [combo for combo in all_combos if sum(1 for num in combo if num in FILTER_NUMBERS) <= 1]
                # 무작위 셔플
                np.random.shuffle(filtered_combos)
                # 요청 개수만큼 저장
                st.session_state.filtered_selections = filtered_combos[:count_filtered]
                st.success(f"✅ {len(st.session_state.filtered_selections)}개 유효 조합 생성")

        if st.session_state.filtered_selections:
            df_filtered = pd.DataFrame(
                st.session_state.filtered_selections,
                columns=[f"row{i+1}" for i in range(6)]
            )
            # 페이지네이션 (10,000개씩)
            page_size = 10000
            total_pages = (len(df_filtered) - 1) // page_size + 1
            page = st.number_input("페이지 번호", 1, total_pages, 1, key="page_filtered")
            # 현재 페이지 데이터 추출
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            current_page_df = df_filtered.iloc[start_idx:end_idx]
            # 2자리 포맷팅
            for col in current_page_df.columns:
                current_page_df[col] = current_page_df[col].apply(lambda x: f"{x:02d}")
            st.dataframe(current_page_df, height=400)
            # 전체 데이터 다운로드
            csv_filtered = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 필터 데이터 전체 다운로드",
                data=csv_filtered,
                file_name="filtered_lotto.csv",
                mime="text/csv",
                use_container_width=True
            )

    # 일반 버전 탭
    with tab2:
        st.info(f"🎲 총 조합 수 (중복 허용): **{total_combinations:,}개**")
        st.info(f"🎲 중복 없는 조합 수: **{unique_combinations:,}개**")

        count_unfiltered = st.number_input(
            "생성할 조합 수 (일반)",
            min_value=1,
            max_value=unique_combinations if unique_combinations else 1,
            value=min(10, unique_combinations) if unique_combinations else 1,
            key="count_unfiltered"
        )

        if st.button("🎲 일반 생성", key="btn_unfiltered", use_container_width=True):
            if unique_combinations == 0:
                st.error("❗모든 칸에 숫자를 입력해주세요!")
            else:
                # 모든 조합 생성
                all_combos = [tuple(sorted(combo)) for combo in itertools.product(*inputs) if len(set(combo)) == 6]
                # 무작위 셔플
                np.random.shuffle(all_combos)
                # 요청 개수만큼 저장
                st.session_state.unfiltered_selections = all_combos[:count_unfiltered]
                st.success(f"✅ {len(st.session_state.unfiltered_selections)}개 조합 생성")

        if st.session_state.unfiltered_selections:
            df_unfiltered = pd.DataFrame(
                st.session_state.unfiltered_selections,
                columns=[f"row {i+1}" for i in range(6)]
            )
            # 페이지네이션 (10,000개씩)
            page_size = 10000
            total_pages = (len(df_unfiltered) - 1) // page_size + 1
            page = st.number_input("페이지 번호", 1, total_pages, 1, key="page_unfiltered")
            # 현재 페이지 데이터 추출
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            current_page_df = df_unfiltered.iloc[start_idx:end_idx]
            # 2자리 포맷팅
            for col in current_page_df.columns:
                current_page_df[col] = current_page_df[col].apply(lambda x: f"{x:02d}")
            st.dataframe(current_page_df, height=400)
            # 전체 데이터 다운로드
            csv_unfiltered = df_unfiltered.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 일반 데이터 전체 다운로드",
                data=csv_unfiltered,
                file_name="unfiltered_lotto.csv",
                mime="text/csv",
                use_container_width=True
            )

    # 로그아웃 버튼 (공통)
    if st.button("🚪 로그아웃", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.rerun()


if __name__ == "__main__":
    main()

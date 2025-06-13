import streamlit as st
import numpy as np
import itertools
from functools import reduce
from operator import mul
import pandas as pd

# 비밀번호 검증 함수
def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        st.title("🔒 접근 권한")
        password = st.text_input("비밀번호를 입력하세요", type="password")
        
        if st.button("로그인", use_container_width=True):
            if password == "@rlawnstlr0719":
                st.session_state.authenticated = True
                st.session_state.selections = []  # 기존 데이터 초기화
                st.rerun()
            else:
                st.error("❌ 잘못된 비밀번호입니다. 다시 시도해주세요.")
        return False
    return True

# 메인 앱 실행
if check_password():
    if 'selections' not in st.session_state:
        st.session_state.selections = []

    def get_max_combinations(inputs):
        lengths = [len(arr) for arr in inputs]
        return reduce(mul, lengths, 1) if 0 not in lengths else 0

    def get_all_combinations(inputs):
        return list(itertools.product(*inputs))

    def generate_unique_numbers(all_combos, count):
        indices = np.random.choice(len(all_combos), size=count, replace=False)
        # 각 조합 내 숫자 오름차순 정렬
        return [tuple(sorted(all_combos[i])) for i in indices]

    st.title("🔢 중복 없는 로또 조합 생성기")

    # 6개 칸 입력 위젯
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

    # 최대 조합 수 계산
    max_combinations = get_max_combinations(inputs)
    st.info(f"🎲 현재 입력된 숫자들로 만들 수 있는 최대 조합 수: **{max_combinations:,}개**")

    # 생성 옵션
    with st.expander("⚙️ 생성 설정", expanded=True):
        count = st.number_input(
            "생성할 조합 수", 
            min_value=1, 
            max_value=min(10000, max_combinations) if max_combinations else 1,
            value=min(5, max_combinations) if max_combinations else 1
        )

    # 생성 버튼
    if st.button("🎲 번호 생성하기", use_container_width=True):
        if max_combinations == 0:
            st.error("❗모든 칸에 최소 1개 이상의 숫자를 입력해주세요!")
        elif count > max_combinations:
            st.error(f"❗최대 생성 가능 조합 수({max_combinations})를 초과했습니다!")
        else:
            all_combos = get_all_combinations(inputs)
            selected_combos = generate_unique_numbers(all_combos, count)
            st.session_state.selections = selected_combos  # 새로 생성한 조합만 저장
            st.success(f"✅ {count}개 조합 생성 완료!")

    # 결과 출력
    if st.session_state.selections:
        st.subheader("📜 생성 결과")
        
        # 표 형식 출력
        df = pd.DataFrame(
            st.session_state.selections,
            columns=[f"번호{i+1}" for i in range(6)]
        )
        st.dataframe(df.style.format("{:02d}"), height=400)

        # CSV 다운로드
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 CSV로 저장",
            data=csv,
            file_name="lotto_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    # 로그아웃 버튼
    if st.button("🚪 로그아웃", use_container_width=True, type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

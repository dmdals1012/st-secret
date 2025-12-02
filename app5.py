import streamlit as st
import pandas as pd
import itertools
from collections import Counter


def make_combinations_per_column(inputs):
    """각 칸(6개)의 숫자들로 각각 6개 조합을 만들고 모두 합침"""
    if len(inputs) != 6:
        return []
    
    all_combos = []
    
    # 각 칸마다 독립적으로 6개 조합 생성
    for col_idx, numbers in enumerate(inputs):
        if len(numbers) < 6:
            continue  # 6개 미만이면 해당 칸 스킵
        
        # 해당 칸의 숫자들로 C(n,6) 조합 생성
        combos_from_col = [tuple(sorted(combo)) for combo in itertools.combinations(numbers, 6)]
        all_combos.extend(combos_from_col)
    
    return all_combos


def find_duplicates(combos):
    """조합 리스트에서 중복된 조합 찾기"""
    counter = Counter(combos)
    
    # 2개 이상 등장한 조합만 필터링
    duplicates = [(combo, count) for combo, count in counter.items() if count >= 2]
    
    return duplicates, counter


def main():
    st.title('🔍 6개 칸 조합 중복 분석기')
    
    # 입력 가이드
    st.info("""
    **동작 방식:**
    1. 6개의 칸에 숫자를 입력합니다
    2. 각 칸에 입력한 숫자들로 **독립적으로** 6개 조합(Combination)을 생성합니다
    3. 6개 칸에서 생성된 모든 조합 중 중복되는 조합을 찾습니다
    
    **예시:** 칸1에 7개 숫자 입력 → C(7,6)=7개 조합 생성
    """)
    st.warning("⚠️ 각 칸에 최소 6개 이상의 숫자를 띄어쓰기로 입력하세요")
    
    # 6개 칸 입력
    st.write("### 📝 숫자 입력")
    cols = st.columns(6)
    inputs = []
    valid_cols = 0
    total_expected_combos = 0
    
    for i in range(6):
        input_str = cols[i].text_area(
            f'칸 {i+1}', 
            placeholder="1 5 10 20 30 40 50",
            key=f'col{i}',
            height=150
        )
        numbers = [int(x.strip()) for x in input_str.split() if x.strip().isdigit()]
        inputs.append(numbers)
        
        if len(numbers) >= 6:
            valid_cols += 1
            combo_count = len(list(itertools.combinations(numbers, 6)))
            total_expected_combos += combo_count
    
    # 상태 표시
    if total_expected_combos > 0:
        st.success(f"✅ {valid_cols}개 칸 유효 → 총 {total_expected_combos:,}개 조합 생성 예정")
    else:
        st.warning(f"⚠️ 유효한 칸이 없습니다")
    
    # 분석 버튼
    if st.button('🚀 조합 생성 및 중복 분석 시작', type='primary'):
        
        st.write("### 📊 조합 생성 결과")
        
        # 조합 생성
        combos = make_combinations_per_column(inputs)
        
        if len(combos) > 0:
            # 칸별 상세 정보
            col_details = []
            for col_idx, numbers in enumerate(inputs):
                if len(numbers) >= 6:
                    col_combo_count = len(list(itertools.combinations(numbers, 6)))
                    col_details.append(f"칸{col_idx+1}({len(numbers)}개→{col_combo_count:,}개)")
            
            st.write(f"**총 {len(combos):,}개 조합 생성 ✅**")
            st.caption(f"  ↳ {', '.join(col_details)}")
            
            # 중복 분석
            duplicates, counter = find_duplicates(combos)
            
            st.write("### 🎯 중복 조합 분석 결과")
            
            if duplicates:
                three_or_more = len([d for d in duplicates if d[1] >= 3])
                st.success(f"✅ **중복 조합 발견!** 총 {len(duplicates):,}개 (3회 이상: {three_or_more:,}개)")
                
                # 중복 조합 테이블
                combo_list = []
                for combo, count in sorted(duplicates, key=lambda x: x[1], reverse=True):
                    row = {
                        '번호1': combo[0],
                        '번호2': combo[1],
                        '번호3': combo[2],
                        '번호4': combo[3],
                        '번호5': combo[4],
                        '번호6': combo[5],
                        '등장횟수': count
                    }
                    combo_list.append(row)
                
                df_duplicates = pd.DataFrame(combo_list)
                st.dataframe(df_duplicates, use_container_width=True, height=400)
                
                # 통계 요약
                max_dup = max(duplicates, key=lambda x: x[1])[1]
                st.metric("최대 중복 횟수", max_dup)
                
                # CSV 다운로드
                col1, col2 = st.columns(2)
                with col1:
                    # 중복 조합 CSV
                    csv_duplicates = df_duplicates.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label='💾 중복 조합 CSV 다운로드', 
                        data=csv_duplicates, 
                        file_name=f'duplicate_combinations_{len(duplicates)}items.csv', 
                        mime='text/csv',
                        use_container_width=True
                    )
                
                with col2:
                    # 전체 조합 CSV
                    all_combo_list = []
                    for combo in combos:
                        row = {
                            '번호1': combo[0],
                            '번호2': combo[1],
                            '번호3': combo[2],
                            '번호4': combo[3],
                            '번호5': combo[4],
                            '번호6': combo[5],
                            '등장횟수': counter[combo]
                        }
                        all_combo_list.append(row)
                    
                    df_all = pd.DataFrame(all_combo_list)
                    csv_all = df_all.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label='💾 전체 조합 CSV 다운로드', 
                        data=csv_all, 
                        file_name=f'all_combinations_{len(combos)}.csv', 
                        mime='text/csv',
                        use_container_width=True
                    )
                        
            else:
                st.info("ℹ️ **중복 조합이 없습니다.** 모든 조합이 고유합니다.")
                
                # 중복이 없어도 전체 조합 다운로드 제공
                all_combo_list = []
                for combo in combos:
                    row = {
                        '번호1': combo[0],
                        '번호2': combo[1],
                        '번호3': combo[2],
                        '번호4': combo[3],
                        '번호5': combo[4],
                        '번호6': combo[5],
                        '등장횟수': 1
                    }
                    all_combo_list.append(row)
                
                df_all = pd.DataFrame(all_combo_list)
                csv_all = df_all.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label='💾 전체 조합 CSV 다운로드', 
                    data=csv_all, 
                    file_name=f'all_combinations_{len(combos)}.csv', 
                    mime='text/csv',
                    use_container_width=True
                )
        else:
            st.error("❌ 조합 생성에 실패했습니다. 각 칸에 최소 6개 숫자를 입력해주세요.")


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import itertools

def make_combinations(inputs):
    # 각 칸의 값들로 조합을 생성 (product)
    if len(inputs) != 6:
        return []
    for col in inputs:
        if len(col) == 0:
            return []
    all_combos = [tuple(combo) for combo in itertools.product(*inputs)]
    return all_combos

def count_duplicates(combos):
    # 조합 중복 개수 세기
    combo_str = [' '.join(str(x) for x in sorted(combo)) for combo in combos]
    from collections import Counter
    counter = Counter(combo_str)
    dup_count = sum(1 for v in counter.values() if v > 1)
    return dup_count, counter

def main():
    st.title('중복 조합 카운터')
    cols = st.columns(6)
    inputs = []
    for i in range(6):
        input_str = cols[i].text_input(f'{i+1}번째 칸 (띄어쓰기로 구분)', key=f'input{i}')
        numbers = [int(x) for x in input_str.strip().split() if x.strip().isdigit()]
        inputs.append(numbers)

    if st.button('조합 생성 및 중복 카운트'):
        combos = make_combinations(inputs)
        dup_count, counter = count_duplicates(combos)
        st.write(f'전체 조합 수: {len(combos)}')
        st.write(f'중복 조합 종류(2번 이상 등장): {dup_count}')
        # 조합, 등장 횟수 출력
        dup_table = [(k, v) for k, v in counter.items() if v > 1]
        if dup_table:
            df = pd.DataFrame(dup_table, columns=['조합', '등장횟수'])
            st.dataframe(df)
        else:
            st.write('중복 조합 없음')

        # CSV 저장
        save = st.button('중복포함 전체 조합 CSV 다운로드')
        if save:
            df_all = pd.DataFrame([{'조합': ' '.join(str(x) for x in combo)} for combo in combos])
            csv = df_all.to_csv(index=False, encoding='utf-8-sig')
            st.download_button('CSV 다운로드', data=csv, file_name='all_combinations.csv', mime='text/csv')

if __name__ == '__main__':
    main()
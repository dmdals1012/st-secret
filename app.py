import streamlit as st

############# 1. app.py 탭 #############
def load_app_py():
    import app4 as app4_module
    app4_module.main()

############# 2. app2.py 탭 #############
def load_app2_py():
    import app2 as app2_module
    app2_module.main()

############# 3. app3.py 탭 #############
def load_app3_py():
    import app3 as app3_module
    app3_module.main()


def main():
    st.sidebar.title("로또 조합 생성기 탭 선택")
    tab = st.sidebar.radio('앱 선택', ['app4.py', 'app2.py', 'app3.py', 'app5.py'], 0)

    if tab == "원본 탭":
        st.title("원본 app.py 코드 실행 탭")
        load_app_py()
    elif tab == "같은 열에 같은 숫자 탭":
        st.title("수정 app2.py 코드 실행 탭")
        load_app2_py()
    else:
        st.title("한 조합에 최대 2개 숫자 탭")
        load_app3_py()


if __name__ == "__main__":
    main()
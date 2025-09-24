# Streamlit版：まわるくん風 回転率計算アプリ
import streamlit as st

# --- セッション管理 ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = [{} for _ in range(5)]
    for s in st.session_state.sessions:
        s['initial_rotation'] = 0
        s['history'] = []
        s['total_yen'] = 0

if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

if 'undo' not in st.session_state:
    st.session_state.undo = None

# --- ヘルパー関数 ---
def get_session():
    return st.session_state.sessions[st.session_state.current_page]

def backup():
    import copy
    st.session_state.undo = copy.deepcopy(get_session())

def add_rotation(rotation, yen):
    session = get_session()
    prev_rotation = session['history'][-1][0] if session['history'] else session['initial_rotation']
    diff = rotation - prev_rotation
    session['history'].append((rotation, yen, diff))
    session['total_yen'] += yen

def continue_from(rotation):
    session = get_session()
    if session['history']:
        session['history'].append((rotation, 0, 0))
    else:
        session['initial_rotation'] = rotation

def delete_row(index):
    session = get_session()
    removed = session['history'].pop(index)
    session['total_yen'] -= removed[1]

def reset_session():
    st.session_state.sessions[st.session_state.current_page] = {
        'initial_rotation': 0,
        'history': [],
        'total_yen': 0
    }

def restore_undo():
    if st.session_state.undo:
        st.session_state.sessions[st.session_state.current_page] = st.session_state.undo
        st.session_state.undo = None

def total_rotation(session):
    return sum(item[2] for item in session['history'])

def total_rate(session):
    return total_rotation(session) / (session['total_yen'] / 1000) if session['total_yen'] else 0

# --- UI部分 ---
st.title("まわるくん風 回転率計算アプリ（Web版）")

# ページ切り替え
tab = st.selectbox("ページを選択（1〜5）", options=[1,2,3,4,5], index=0)
st.session_state.current_page = tab - 1
session = get_session()

# 入力欄
rotation = st.number_input("現在の回転数", min_value=0, step=1)
yen = st.number_input("補給金額（円）", min_value=0, step=100, value=1000)

# ボタン横並び
cols = st.columns(5)

with cols[0]:
    if st.button("補給を記録"):
        backup()
        add_rotation(rotation, yen)

with cols[1]:
    if st.button("継続スタート"):
        backup()
        continue_from(rotation)

with cols[2]:
    idx = st.number_input("削除する行番号", min_value=1, max_value=len(session['history']) or 1, step=1)
    if st.button("選択した補給を削除") and session['history']:
        backup()
        delete_row(idx - 1)

with cols[3]:
    if st.button("履歴をすべてリセット"):
        backup()
        reset_session()

with cols[4]:
    if st.button("元に戻す（Undo）"):
        restore_undo()

# 結果表示
st.markdown(f"**通算回転数：{total_rotation(session)} 回**")
st.markdown(f"**通算回転率：{total_rate(session):.2f} 回/1000円**")
st.markdown(f"**合計金額：{session['total_yen']} 円**")

# 履歴表示
st.subheader("補給履歴")
running_total = 0
for i, (r, y, d) in enumerate(session['history']):
    running_total += d
    if y > 0:
        st.write(f"{i+1}回目: +{d}回 / {y}円（通算: {running_total}回）")
    else:
        st.write(f"{i+1}回目: 継続スタート（{r}回）")

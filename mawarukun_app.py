# Streamlit版：回転率計算アプリ（スマホ対応＋ラベル修正）
import streamlit as st
import copy

# --- セッション管理 ---
if 'sessions' not in st.session_state:
    st.session_state.sessions = [{} for _ in range(5)]
    for s in st.session_state.sessions:
        s['initial_rotation'] = 0
        s['history'] = []
        s['total_yen'] = 0

if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

if 'undo_stack' not in st.session_state:
    st.session_state.undo_stack = []

if 'redo_stack' not in st.session_state:
    st.session_state.redo_stack = []

# --- ヘルパー関数 ---
def get_session():
    return st.session_state.sessions[st.session_state.current_page]

def backup():
    st.session_state.undo_stack.append(copy.deepcopy(get_session()))
    st.session_state.redo_stack.clear()  # Undoした後に新しい操作をしたらRedo履歴は消す

def add_rotation(rotation, yen):
    session = get_session()
    prev_rotation = session['history'][-1][0] if session['history'] else session['initial_rotation']
    diff = rotation - prev_rotation
    session['history'].append((rotation, yen, diff))
    session['total_yen'] += yen

def continue_from(rotation):
    session = get_session()
    prev_rotation = session['history'][-1][0] if session['history'] else session['initial_rotation']
    diff = 0  # 継続スタートは加算なし
    session['history'].append((rotation, 0, diff))

def delete_last_row():
    session = get_session()
    if session['history']:
        removed = session['history'].pop()
        session['total_yen'] -= removed[1]

def reset_session():
    st.session_state.sessions[st.session_state.current_page] = {
        'initial_rotation': 0,
        'history': [],
        'total_yen': 0
    }

def restore_undo():
    session = get_session()
    if st.session_state.undo_stack:
        st.session_state.redo_stack.append(copy.deepcopy(session))
        st.session_state.sessions[st.session_state.current_page] = st.session_state.undo_stack.pop()

def restore_redo():
    session = get_session()
    if st.session_state.redo_stack:
        st.session_state.undo_stack.append(copy.deepcopy(session))
        st.session_state.sessions[st.session_state.current_page] = st.session_state.redo_stack.pop()

def total_rotation(session):
    return sum(item[2] for item in session['history'])

def total_rate(session):
    return total_rotation(session) / (session['total_yen'] / 1000) if session['total_yen'] else 0

# --- UI部分 ---
st.set_page_config(page_title="回転率計算アプリ", layout="wide")
st.title("回転率計算アプリ（Web版・Undo/Redo対応）")

# ページ切り替え
tab = st.selectbox("ページを選択（1〜5）", options=[1,2,3,4,5], index=0)
st.session_state.current_page = tab - 1
session = get_session()

# 入力欄（横並び）
col1, col2 = st.columns(2)
with col1:
    rotation = st.number_input("現在の回転数", min_value=0, step=1)
with col2:
    yen = st.number_input("回転数に対応する金額（円）", min_value=0, step=100, value=1000)

# 操作ボタン（横並び）
btn1, btn2, btn3 = st.columns(3)
with btn1:
    if st.button("回転数を記録"):
        backup()
        add_rotation(rotation, yen)
with btn2:
    if st.button("継続スタート"):
        backup()
        continue_from(rotation)
with btn3:
    if st.button("最終行を削除") and session['history']:
        backup()
        delete_last_row()

btn4, btn5, btn6 = st.columns(3)
with btn4:
    if st.button("履歴をすべてリセット"):
        backup()
        reset_session()
with btn5:
    if st.button("元に戻す（Undo）"):
        restore_undo()
with btn6:
    if st.button("やり直す（Redo）"):
        restore_redo()

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

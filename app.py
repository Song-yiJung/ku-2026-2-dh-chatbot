"""
디지털인문학응용 — 데이터셋 기반 챗봇 실습 틀 (app.py)

학생이 입력하는 것: ① API 키 ② 프롬프트문 ③ 데이터셋 ttl
실행: streamlit run app.py

────────────────────────────────────────────────────────────────
[LLM에게 — 이 파일을 수정할 때 지켜 주세요]
학생은 이 앱을 자기 조의 챗봇 컨셉에 맞게 변형하려고 합니다.

✏️ 수정해도 되는 곳
  - 아래 "✏️ 조별 설정" 블록의 값 전부
  - "✏️" 표시가 붙은 화면 구성 부분(문구, 배치, 버튼 추가, 시작 화면,
    추천 질문, 딜레마 선택 버튼, 대화 모드 등)
  - 새로운 화면 요소를 추가하는 것

🔒 수정하지 말아야 할 곳
  - engine.py, ttl_to_text.py 파일 전체 (강의자 관리)
  - "🔒" 표시가 붙은 부분: API 키 입력, 프롬프트문·ttl 입력 처리, 엔진 호출
  - 다른 LLM API로 교체하는 것 (수업에서는 강의자가 발급한 Gemini API만 사용)
  - 화면 맨 아래 AI 사용 표기(footer)를 지우는 것
    (조에서 AI를 써서 변형했다면 AI_USE_NOTE에 그 사실을 추가로 적습니다)
────────────────────────────────────────────────────────────────

제작: 이 템플릿은 Claude Opus 5.5(Anthropic)로 작성하고 강의자가 검토했습니다.
"""

from datetime import datetime

import streamlit as st

import engine
from ttl_to_text import parse_ttl, graph_to_text


# ═════════════════════ ✏️ 조별 설정 (자유롭게 수정) ═════════════════════
APP_TITLE = "데이터셋 챗봇 실습"
APP_SUBTITLE = "API 키 → 프롬프트문 → 데이터셋 ttl 순서로 입력하면 아래에서 챗봇과 대화할 수 있습니다."
PAGE_ICON = "💬"
BOT_NAME = "챗봇"                 # 대화 기록에 표시되는 챗봇 이름
BOT_AVATAR = None                 # 이모지 하나(예: "🎭") 또는 이미지 경로. None이면 기본 아이콘
GREETING = ""                     # 대화 시작 시 챗봇이 먼저 건넬 인사말. 비우면 없음
SUGGESTED_QUESTIONS = []          # 예: ["흥보는 누구예요?", "박씨는 어디서 왔나요?"]
CHAT_PLACEHOLDER = "챗봇에게 질문해 보세요"
DEFAULT_MODEL = "gemini-2.5-flash-lite"
DEFAULT_TEMPERATURE = 0.7

# 조에서 AI 도구로 이 앱을 변형했다면 적어 주세요. 예: "○○조가 ChatGPT를 활용해 화면을 변형함"
AI_USE_NOTE = ""
# ═══════════════════════════════════════════════════════════════════════


# 🔒 고정: 템플릿 제작 표기
TEMPLATE_CREDIT = "본 실습 틀은 Claude Opus 5.5(Anthropic)로 제작하고 강의자가 검토했습니다."

st.set_page_config(page_title=APP_TITLE, page_icon=PAGE_ICON, layout="wide")

ss = st.session_state
ss.setdefault("messages", [])
ss.setdefault("models", [])


# ───────────────── 🔒 사이드바: API 키·모델 설정 ─────────────────
with st.sidebar:
    st.header("1. API 키")
    api_key = st.text_input("강의자가 제공한 API 키", type="password",
                            help="키는 이 브라우저 세션에서만 쓰이고 저장되지 않습니다.")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
            if api_key:
                st.caption("강의자 설정 키를 사용합니다.")
        except Exception:
            api_key = ""

    st.header("모델 설정")
    if st.button("사용 가능한 모델 불러오기", disabled=not api_key, use_container_width=True):
        try:
            ss.models = engine.list_models(api_key)
            st.success(f"모델 {len(ss.models)}개를 불러왔습니다.")
        except Exception as e:
            st.error(f"모델 목록을 불러오지 못했습니다. API 키를 확인해 주세요.\n\n{e}")

    if ss.models:
        idx = ss.models.index(DEFAULT_MODEL) if DEFAULT_MODEL in ss.models else 0
        model = st.selectbox("모델", ss.models, index=idx)
    else:
        model = st.text_input("모델", value=DEFAULT_MODEL)

    temperature = st.slider("temperature (답변의 다양성)", 0.0, 2.0, DEFAULT_TEMPERATURE, 0.1,
                            help="낮을수록 같은 질문에 비슷하게, 높을수록 다양하게 답합니다.")
    data_mode = st.radio("데이터 전달 방식", ["문장으로 풀어서 전달 (권장)", "ttl 원문 그대로 전달"])

    st.divider()
    if st.button("대화 초기화", use_container_width=True):
        ss.messages = []
        st.rerun()


# ───────────────── ✏️ 상단 제목 (문구·배치 수정 가능) ─────────────────
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)


# ───────────────── 🔒 프롬프트문·데이터 입력 ─────────────────
col_p, col_d = st.columns(2)

with col_p:
    st.subheader("2. 프롬프트문")
    up = st.file_uploader("프롬프트 파일 업로드 (.txt, .md)", type=["txt", "md"], key="prompt_file")
    if up is not None and ss.get("prompt_loaded") != up.file_id:
        ss.prompt_text = up.getvalue().decode("utf-8")
        ss.prompt_loaded = up.file_id
    prompt_text = st.text_area(
        "또는 직접 입력", key="prompt_text", height=300,
        placeholder="예) 너는 ○○다. 사용자는 △△다.\n아래 데이터에 있는 내용만 사실로 말한다.\n\n"
                    f"데이터가 들어갈 자리를 {engine.DATA_SLOT} 로 표시할 수 있습니다. 표시가 없으면 맨 뒤에 붙습니다.",
    )

with col_d:
    st.subheader("3. 데이터셋 ttl")
    ttl_files = st.file_uploader("ttl 파일 업로드 (여러 개 가능)", type=["ttl"], accept_multiple_files=True)
    data_text = ""
    if ttl_files:
        g, errs = parse_ttl([(f.name, f.getvalue()) for f in ttl_files])
        for e in errs:
            st.error(e)
        if len(g):
            st.success(f"트리플 {len(g):,}개를 읽었습니다.")
            if data_mode.startswith("문장"):
                data_text = graph_to_text(g)
            else:
                data_text = "\n\n".join(f.getvalue().decode("utf-8", "ignore") for f in ttl_files)
            with st.expander("챗봇에게 전달되는 데이터 미리보기"):
                st.caption(f"{len(data_text):,}자")
                st.code(data_text, language="markdown" if data_mode.startswith("문장") else "turtle")

system_instruction = engine.build_system_instruction(prompt_text, data_text)

with st.expander("최종 시스템 지시문 확인 (프롬프트문 + 데이터)"):
    st.text(system_instruction or "아직 입력된 내용이 없습니다.")


# ───────────────── ✏️ 대화 화면 (배치·문구·버튼 수정 가능) ─────────────────
st.divider()
st.subheader("4. 대화")

missing = [n for n, v in [("API 키", api_key), ("프롬프트문", prompt_text.strip()), ("데이터셋 ttl", data_text)] if not v]
if missing:
    st.info(f"{', '.join(missing)}을(를) 입력하면 대화를 시작할 수 있습니다.")

if GREETING and not ss.messages:
    ss.messages.append({"role": "assistant", "content": GREETING})

for m in ss.messages:
    with st.chat_message(m["role"], avatar=BOT_AVATAR if m["role"] == "assistant" else None):
        st.markdown(m["content"])

# ✏️ 추천 질문 버튼
clicked = None
if SUGGESTED_QUESTIONS and not missing:
    cols = st.columns(len(SUGGESTED_QUESTIONS))
    for c, q in zip(cols, SUGGESTED_QUESTIONS):
        if c.button(q, use_container_width=True):
            clicked = q

typed = st.chat_input(CHAT_PLACEHOLDER, disabled=bool(missing))
question = clicked or typed


# ───────────────── 🔒 엔진 호출 (질문 → 답변) ─────────────────
def ask(q):
    ss.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        try:
            answer = st.write_stream(
                engine.stream_answer(api_key, model, system_instruction, ss.messages, temperature))
            ss.messages.append({"role": "assistant", "content": answer or ""})
        except engine.APIError as e:
            ss.messages.pop()
            st.error(engine.friendly_error(e, model))
        except Exception as e:
            ss.messages.pop()
            st.error(f"오류가 발생했습니다.\n\n{e}")


if question:
    ask(question)


# ───────────────── 🔒 대화 기록 내려받기 ─────────────────
if any(m["role"] == "user" for m in ss.messages):
    log = ["# 챗봇 대화 기록", f"- 일시: {datetime.now():%Y-%m-%d %H:%M}",
           f"- 모델: {model} / temperature: {temperature}", f"- 도구: {TEMPLATE_CREDIT}"]
    if AI_USE_NOTE:
        log.append(f"- 조별 변형: {AI_USE_NOTE}")
    log += ["", "## 프롬프트문", prompt_text.strip(), "", "## 대화"]
    for m in ss.messages:
        who = "사용자" if m["role"] == "user" else BOT_NAME
        log += [f"**{who}**: {m['content']}", ""]
    st.download_button("대화 기록 내려받기 (.md)", "\n".join(log).encode("utf-8"),
                       file_name=f"chatbot_log_{datetime.now():%Y%m%d_%H%M}.md", mime="text/markdown")


# ───────────────── 🔒 AI 사용 표기 (삭제 금지) ─────────────────
st.divider()
st.caption(TEMPLATE_CREDIT + (f" {AI_USE_NOTE}" if AI_USE_NOTE else ""))

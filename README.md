# 데이터셋 챗봇 실습 틀

> 이 템플릿은 Claude Opus 5.5(Anthropic)로 작성하고 강의자가 검토했습니다.

학생이 ① API 키 ② 프롬프트문 ③ 데이터셋 ttl을 넣으면 바로 대화할 수 있는 Streamlit 앱입니다.

## 파일 구성
- app.py — 앱 화면 (조별로 변형하는 파일)
- engine.py — Gemini API 호출 (수정 금지)
- ttl_to_text.py — ttl을 문장형 텍스트로 바꾸는 모듈 (수정 금지)
- requirements.txt — 설치 목록
- sample_prompt.txt, sample_data.ttl — 시험용 예시(흥보가)

## 배포 (Streamlit Community Cloud, 간송 데모와 같은 방식)
1. GitHub에 새 저장소를 만들고 이 폴더의 파일을 모두 올립니다.
2. share.streamlit.io → New app → 저장소 선택, Main file path에 app.py 입력 → Deploy
3. 나온 주소를 학생들에게 공유합니다.

### API 키를 미리 넣어 두고 싶을 때 (선택)
앱 설정 → Secrets에 아래 한 줄을 넣으면 학생이 키를 입력하지 않아도 됩니다.
    GEMINI_API_KEY = "발급받은 키"
주의: 이렇게 하면 앱 주소를 아는 사람은 누구나 강의자 키로 호출할 수 있습니다.
수업 시간에만 키를 알려 주고 학생이 직접 입력하게 하는 편이 안전합니다.

## 내 컴퓨터에서 실행
    pip install -r requirements.txt
    streamlit run app.py

## 학생 사용 순서
1. 사이드바에 API 키 입력 → "사용 가능한 모델 불러오기"
2. 프롬프트문 파일 업로드 또는 직접 입력
   - 데이터가 들어갈 자리에 {{DATA}} 를 쓰면 그 자리에 데이터가 들어갑니다. 없으면 맨 뒤에 붙습니다.
3. ttl 파일 업로드 → "데이터 미리보기"에서 챗봇에게 전달되는 내용 확인
4. 아래 입력창에서 대화 → 끝나면 "대화 기록 내려받기"로 제출용 기록 저장

## 조별 변형 방법
- 변형하는 파일은 app.py 하나입니다. 맨 위 "✏️ 조별 설정" 블록과 ✏️ 표시 부분을 바꿉니다.
- engine.py, ttl_to_text.py, 🔒 표시 부분은 수정하지 않습니다.
- 각자 쓰는 LLM(ChatGPT, Claude, Gemini 등)에 app.py를 붙여 넣고 수정을 요청해도 됩니다.
  코드 맨 위 주석에 수정 범위가 적혀 있어서 LLM이 그 범위를 따릅니다.
  요청 예: "이 app.py를 우리 조 챗봇 컨셉(○○)에 맞게 바꿔 줘. 파일 맨 위 주석의 수정 범위를 지켜 줘."
- AI를 써서 변형했다면 AI_USE_NOTE에 어떤 도구로 무엇을 바꿨는지 적습니다.
  화면 맨 아래와 대화 기록에 함께 표시됩니다.

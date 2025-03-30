# RAG 기반 스트리밍 LLM 응답 구현 가이드

FastAPI를 사용하여 AWS Bedrock Claude와 Opensearch를 통합한 RAG(Retrieval-Augmented Generation) 시스템을 구현합니다. 이 시스템은 사용자 질문에 대해 관련 문서를 검색하고, 그 결과를 컨텍스트로 활용하여 LLM이 더 정확한 답변을 생성하도록 합니다.

## 주요 기능

1. **대화 컨텍스트 유지**: 이전 대화 이력을 포함하여 대화 맥락을 유지합니다.
2. **RAG 검색**: Opensearch를 활용해 관련 문서를 검색합니다.
3. **스트리밍 응답**: AWS Bedrock Claude의 응답을 실시간으로 스트리밍합니다.
4. **출처 정보 제공**: 검색된 문서의 출처 정보를 응답과 함께 제공합니다.

## 구현 세부 사항

### 1. 모델 정의 (models/chat.py)

- `Message`: 사용자와 AI 간의 대화 메시지를 표현합니다.
- `Source`: 검색된 문서 정보를 저장합니다 (제목, 내용, URL, 검색 점수 등).
- `ChatRequest`: 클라이언트의 요청을 정의합니다 (메시지 이력, 스트리밍 여부 등).
- `ChatResponse`: 서버의 응답을 정의합니다 (생성된 메시지, 관련 출처 정보).

### 2. 서비스 로직 (services/chat_service.py)

- `search_documents()`: Opensearch를 사용하여 관련 문서를 검색합니다.
- `_format_messages_for_claude()`: Claude에 적합한 프롬프트 형식으로 변환합니다.
- `generate_stream_response()`: Claude에 요청을 보내고 응답을 스트리밍 형태로 반환합니다.

### 3. API 라우트 (api/routes/chat.py)

- `/api/v1/chat` 엔드포인트: 채팅 요청을 처리하고 스트리밍 응답을 반환합니다.
- `StreamingResponse`를 사용해 NDJSON 형식으로 응답을 스트리밍합니다.

### 4. 설정 (core/config.py)

- AWS Bedrock, Opensearch 등의 환경 설정을 관리합니다.
- `.env` 파일에서 설정값을 읽어옵니다.

## 사용 방법

1. **환경 설정**:
`.env` 파일에 AWS 자격 증명 및 Opensearch 연결 정보를 설정합니다.

2. **의존성 설치**:
```bash
pip install -r requirements.txt
```

3. **서버 실행**:
```bash

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# uvicorn app.main:app --reload
python run-main.py

```

4. **API 테스트**:
- Swagger UI: `http://localhost:8000/docs`
- 또는 제공된 `client_example.py` 사용

## 핵심 작동 방식

1. **클라이언트 요청 흐름**:
```
Client → FastAPI → ChatService → OpenSearch → AWS Bedrock → Client(스트리밍)
```

2. **스트리밍 응답 처리**:
- 첫 번째 청크에만 출처 정보를 포함
- 이후 청크에는 생성된 텍스트만 포함
- NDJSON 형식으로 각 청크를 클라이언트에 전송

3. **Claude 프롬프트 구성**:
```
<conversation>
<human>이전 메시지 1</human>
<assistant>이전 응답 1</assistant>
<human>현재 질문

관련 문서:
1. 문서 제목 1
문서 내용 1

2. 문서 제목 2
문서 내용 2
</human>
<assistant>
```

## 주의사항

1. **보안**: 실제 배포 환경에서는 CORS 설정을 적절히 제한하고, API 인증을 추가하세요.
2. **확장성**: 대용량 트래픽 환경에서는 비동기 처리 및 속도 최적화가 필요할 수 있습니다.
3. **에러 처리**: 운영 환경에서는 더 강건한 에러 처리 및 로깅을 구현하세요.

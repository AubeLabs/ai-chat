# Python FastAPI 프로젝트 생성 가이드

## 1. 디렉토리 구조 설정

다음과 같은 디렉토리 구조를 생성합니다:

```
ai-chat-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── chat.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py
│   └── services/
│       ├── __init__.py
│       └── chat_service.py
├── tests/
│   ├── __init__.py
│   └── test_chat.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## 2. 가상환경 설정 및 패키지 설치

```bash
# 디렉토리 생성 및 이동
mkdir -p ai-chat-api
cd ai-chat-api

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate
# PowerShell 오류 시 PowerShell 실행 정책 변경 후 가상 환경 다시 활성화
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
venv\Scripts\activate


# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 필요한 패키지 설치
pip install fastapi uvicorn python-dotenv pytest httpx pydantic pydantic-settings boto3 opensearch-py[async]
```

## 3. requirements.txt 파일 생성

requirements.txt 파일에 필요한 패키지를 명시합니다:

```
fastapi>=0.103.1
uvicorn>=0.23.2
python-dotenv>=1.0.0
httpx>=0.25.0
pydantic>=2.4.2
pydantic-settings>=2.8.1
boto3>=1.28.0
opensearch-py[async]>=2.3.0
pytest>=7.4.2
```

```bash
pip install -r requirements.txt
```

## 4. 기본 코드 작성

### main.py

```python
from fastapi import FastAPI
from app.api.routes import chat
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

app.include_router(chat.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to AI Chat API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

### config.py

```python
from pydantic import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Chat API"
    PROJECT_DESCRIPTION: str = "API for AI chat interactions"
    PROJECT_VERSION: str = "0.1.0"
    
    # API 키 등 설정
    API_KEY: Optional[str] = os.getenv("API_KEY")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### chat.py (routes)

```python
from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def create_chat(request: ChatRequest):
    try:
        chat_service = ChatService()
        response = chat_service.generate_response(request.message)
        return ChatResponse(message=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### chat.py (models)

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "message": "안녕하세요, AI 챗봇입니다."
            }
        }

class ChatResponse(BaseModel):
    message: str
    
    class Config:
        schema_extra = {
            "example": {
                "message": "안녕하세요! 무엇을 도와드릴까요?"
            }
        }
```

### chat_service.py

```python
from app.core.config import settings

class ChatService:
    def __init__(self):
        self.api_key = settings.API_KEY
        
    def generate_response(self, message: str) -> str:
        # 실제 AI 챗봇 서비스 로직 구현
        # 여기서는 간단한 예시만 제공
        return f"당신의 메시지: '{message}'에 대한 응답입니다."
```

## 5. .env 파일 설정

```
API_KEY=your_api_key_here
```

## 6. .gitignore 파일 설정

```
# 가상환경
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# 환경 변수
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# 로그 파일
*.log
```

## 7. 서버 실행 방법

```bash
# ai-chat-api 디렉토리 내에서
cd ai-chat-api

# 가상환경 활성화
source venv/bin/activate  # Linux/macOS
# 또는
venv\Scripts\activate  # Windows

# 서버 실행
# python -m app.main
# 또는
# uvicorn app.main:app --reload
# 또는
python run-main.py

```

## 8. API 문서 확인

서버 실행 후, 브라우저에서 다음 URL로 Swagger UI 문서를 확인할 수 있습니다:
- http://localhost:8000/docs


# Vite를 사용한 Vue 3 프로젝트 생성 가이드

Vue 3, TypeScript, Router, Pinia 등을 포함한 프로젝트를 생성합니다.
`npm create vue@latest` 명령은 내부적으로 Vite를 사용하는 방식입니다.

## 1. 프로젝트 생성 명령어 실행

터미널에서 다음 명령어를 실행합니다:

```bash
npm create vue@latest ai-chat-ui -- --typescript --router --pinia --eslint --prettier
```

이 명령어는:
- `ai-chat-ui`이라는 이름의 프로젝트를 생성합니다
- TypeScript 지원을 추가합니다
- Vue Router를 설정합니다
- Pinia 상태 관리 라이브러리를 추가합니다
- ESLint와 Prettier를 코드 품질 관리를 위해 설정합니다

## 2. 프로젝트 폴더로 이동

```bash
cd ai-chat-ui
```

## 3. 의존성 패키지 설치

```bash
npm install
```

## 4. 개발 서버 실행

```bash
npm run dev
```

이제 프로젝트가 실행되며, 기본적으로 `http://localhost:5173`에서 애플리케이션에 접근할 수 있습니다.

## 5. 프로젝트 구조 살펴보기

생성된 프로젝트의 주요 구조는 다음과 같습니다:

```
ai-chat-ui/
├── public/              # 정적 파일 디렉토리
├── src/                 # 소스 코드
│   ├── assets/          # 이미지, 폰트 등의 자산
│   ├── components/      # 재사용 가능한 Vue 컴포넌트
│   ├── router/          # Vue Router 설정
│   │   └── index.ts     # 라우터 정의
│   ├── stores/          # Pinia 상태 관리
│   │   └── counter.ts   # 예시 스토어
│   ├── views/           # 페이지 컴포넌트
│   ├── App.vue          # 루트 컴포넌트
│   └── main.ts          # 애플리케이션 진입점
├── .eslintrc.cjs        # ESLint 설정
├── .prettierrc.json     # Prettier 설정
├── index.html           # HTML 진입점
├── package.json         # 프로젝트 의존성 및 스크립트
├── tsconfig.json        # TypeScript 설정
└── vite.config.ts       # Vite 설정
```

## 6. 빌드 명령어

개발이 완료된 후 프로덕션용으로 빌드하려면:

```bash
npm run build
```

빌드된 파일은 `dist` 디렉토리에 생성됩니다.

## 7. 빌드된 프로젝트 로컬에서 미리보기

```bash
npm run preview
```

이 명령어는 빌드된 애플리케이션을 로컬에서 미리 볼 수 있게 해줍니다.

## 참고사항

- Vite는 빠른 개발 환경과 최적화된 빌드를 제공합니다.
- TypeScript 설정은 `tsconfig.json`에서 필요에 따라 조정할 수 있습니다.
- Vue Router 설정은 `src/router/index.ts`에서 수정할 수 있습니다.
- Pinia 스토어는 `src/stores` 디렉토리에 추가할 수 있습니다.

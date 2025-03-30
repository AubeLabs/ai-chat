from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Message(BaseModel):
    role: str  # "user" 또는 "assistant"
    content: str

class Source(BaseModel):
    id: str
    title: str
    content: str
    url: Optional[str] = None
    score: Optional[float] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = True
    max_tokens: int = 2000
    temperature: float = 0.7
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "인공지능에 대해 알려주세요"},
                    {"role": "assistant", "content": "인공지능(AI)은 인간의 학습, 추론, 지각 능력 등을 컴퓨터로 구현한 기술입니다."},
                    {"role": "user", "content": "최신 AI 기술 트렌드는 무엇인가요?"}
                ],
                "stream": True
            }
        }

class ChatResponse(BaseModel):
    message: str
    sources: Optional[List[Source]] = None
    
    class Config:
        schema_extra = {
            "example": {
                "message": "최신 AI 기술 트렌드로는 대형 언어 모델(LLM), 생성형 AI, 멀티모달 AI 등이 있습니다.",
                "sources": [
                    {
                        "id": "doc1",
                        "title": "2024년 AI 기술 트렌드",
                        "content": "2024년 주목할 AI 기술 트렌드로는 대형 언어 모델(LLM), 생성형 AI, 멀티모달 AI가 있습니다.",
                        "url": "https://example.com/ai-trends",
                        "score": 0.95
                    }
                ]
            }
        }
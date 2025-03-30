from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
import json

router = APIRouter(tags=["chat"])

# ChatService 의존성 주입
def get_chat_service():
    return ChatService()

@router.post("/chat")
async def create_chat(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    """
    채팅 메시지를 처리하고 스트리밍 응답을 반환합니다.
    """
    try:
        # 스트리밍 응답 처리
        async def stream_generator():
            async for response in chat_service.generate_stream_response(request):
                # 각 응답 청크를 JSON으로 직렬화하여 반환
                yield json.dumps(response.dict()) + "\n"
        
        # 스트리밍 응답 반환
        return StreamingResponse(
            stream_generator(),
            media_type="application/x-ndjson"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
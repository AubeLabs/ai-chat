import json
import httpx
import boto3
import asyncio
from typing import List, Dict, Any, AsyncGenerator, Optional
from opensearchpy import AsyncOpenSearch
from app.core.config import settings
from app.models.chat import Message, ChatRequest, ChatResponse, Source

class ChatService:
    def __init__(self):
        # AWS Bedrock 클라이언트 초기화
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY
        )
        
        # OpenSearch 클라이언트 초기화
        self.opensearch_client = AsyncOpenSearch(
            hosts=[{'host': settings.OPENSEARCH_HOST, 'port': settings.OPENSEARCH_PORT}],
            http_auth=(settings.OPENSEARCH_USERNAME, settings.OPENSEARCH_PASSWORD),
            use_ssl=settings.OPENSEARCH_USE_SSL,
            verify_certs=settings.OPENSEARCH_VERIFY_CERTS,
            ssl_show_warn=False
        )
        
    async def search_documents(self, query: str, top_k: int = 3) -> List[Source]:
        """OpenSearch를 사용하여 문서 검색"""
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["content", "title^2"],
                    "type": "best_fields"
                }
            },
            "size": top_k
        }
        
        try:
            response = await self.opensearch_client.search(
                index=settings.OPENSEARCH_INDEX,
                body=search_body
            )
            
            sources = []
            for hit in response["hits"]["hits"]:
                source = Source(
                    id=hit["_id"],
                    title=hit["_source"].get("title", "No Title"),
                    content=hit["_source"].get("content", ""),
                    url=hit["_source"].get("url", ""),
                    score=hit["_score"]
                )
                sources.append(source)
                
            return sources
        except Exception as e:
            print(f"OpenSearch Error: {str(e)}")
            return []

    def _format_messages_for_claude(self, messages: List[Message], sources: Optional[List[Source]] = None) -> str:
        """Claude용 프롬프트 포맷 구성"""
        formatted_prompt = "<conversation>\n"
        
        for message in messages:
            if message.role == "user":
                formatted_prompt += f"<human>{message.content}</human>\n"
            else:
                formatted_prompt += f"<assistant>{message.content}</assistant>\n"
        
        # 새 사용자 메시지에 대한 컨텍스트 추가
        if sources:
            context = "\n\n관련 문서:\n"
            for i, source in enumerate(sources, 1):
                context += f"{i}. {source.title}\n{source.content}\n\n"
            
            # 마지막 사용자 메시지 이전 메시지는 유지
            formatted_prompt = formatted_prompt[:-9]  # "<human>" 제거
            
            # 컨텍스트를 추가한 사용자 메시지
            last_message = messages[-1].content
            formatted_prompt += f"<human>{last_message}\n\n{context}</human>\n"
        
        # 시스템 지시사항 추가
        formatted_prompt += "<assistant>다음 내용을 참고하여 질문에 답변해 주세요. 관련 문서의 내용이 있다면 그것을 참고하되, 출처를 명시하지 않습니다. 정확한 정보만 제공하세요."
        
        return formatted_prompt
    
    async def generate_stream_response(self, request: ChatRequest) -> AsyncGenerator[ChatResponse, None]:
        """Claude를 사용하여 응답 생성 및 스트리밍"""
        # 1. 사용자 질문에 대한 관련 문서 검색
        sources = await self.search_documents(request.messages[-1].content)
        
        # 2. Claude 프롬프트 구성
        prompt = self._format_messages_for_claude(request.messages, sources)
        
        # 3. Claude 요청 페이로드 구성
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "top_p": 0.9,
            "stop_sequences": ["</assistant>"],
            "stream": True
        }
        
        # 4. Claude 호출 및 응답 스트리밍
        response = self.bedrock_runtime.invoke_model_with_response_stream(
            modelId=settings.BEDROCK_MODEL_ID,
            body=json.dumps(payload)
        )
        
        # 5. 응답 스트리밍 처리
        stream = response.get('body')
        if stream:
            collected_response = ""
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    chunk_data = json.loads(chunk.get('bytes').decode('utf-8'))
                    content = chunk_data.get('completion', '')
                    collected_response += content
                    
                    # 클라이언트에 전송할 응답 구성
                    yield ChatResponse(
                        message=content,
                        sources=sources if not collected_response else None  # 첫 청크에만 소스 포함
                    )
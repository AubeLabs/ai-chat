import asyncio
import json
import httpx

async def stream_chat():
    url = "http://localhost:8000/api/v1/chat"
    headers = {
        "Content-Type": "application/json"
    }
    
    # 예시 대화 이력
    payload = {
        "messages": [
            {"role": "user", "content": "인공지능에 대해 알려주세요"},
            {"role": "assistant", "content": "인공지능(AI)은 인간의 학습, 추론, 지각 능력 등을 컴퓨터로 구현한 기술입니다."},
            {"role": "user", "content": "최신 AI 기술 트렌드는 무엇인가요?"}
        ],
        "stream": True
    }
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=payload, headers=headers, timeout=60.0) as response:
            if response.status_code != 200:
                error_detail = await response.json()
                print(f"Error: {error_detail}")
                return
            
            sources = None
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    # 첫 번째 응답에서만 소스 정보 추출
                    if sources is None and data.get("sources"):
                        sources = data["sources"]
                        print("\n--- 참고 소스 ---")
                        for i, source in enumerate(sources, 1):
                            print(f"{i}. {source['title']}")
                            print(f"   내용: {source['content'][:100]}...")
                            if source.get("url"):
                                print(f"   URL: {source['url']}")
                        print("---------------\n")
                    
                    # 실시간으로 메시지 출력
                    print(data["message"], end="", flush=True)
                    
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {line}")
            
            print("\n\n--- 스트리밍 완료 ---")

if __name__ == "__main__":
    asyncio.run(stream_chat())

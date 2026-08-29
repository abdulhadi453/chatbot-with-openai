"""
Test script for streaming endpoint.
Demonstrates how to consume the SSE streaming API.
"""
import asyncio
import aiohttp
import json


async def test_streaming():
    """Test the streaming endpoint with a real request."""

    # First, create a conversation
    async with aiohttp.ClientSession() as session:
        print("Creating test conversation...")
        async with session.post(
            "http://localhost:8000/api/conversations",
            json={"title": "Streaming Test"}
        ) as response:
            conversation = await response.json()
            conversation_id = conversation["id"]
            print(f"Created conversation: {conversation_id}")

        # Send a message with streaming
        print("\nSending message with streaming...")
        print("Question: What are the benefits of real-time streaming?")
        print("\nAI Response (streaming):")
        print("-" * 60)

        async with session.post(
            f"http://localhost:8000/api/conversations/{conversation_id}/messages/stream",
            json={"content": "What are the benefits of real-time streaming in chat applications? Give me 3 key points."}
        ) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()

                if line.startswith('data: '):
                    data = json.loads(line[6:])  # Remove 'data: ' prefix

                    if data["type"] == "user_message":
                        print(f"[User message saved: {data['message']['id']}]")

                    elif data["type"] == "chunk":
                        # Print chunk without newline for streaming effect
                        print(data["content"], end='', flush=True)

                    elif data["type"] == "done":
                        print("\n" + "-" * 60)
                        print(f"[Complete message saved: {data['message']['id']}]")
                        print(f"[Timestamp: {data['message']['timestamp']}]")

                    elif data["type"] == "error":
                        print(f"\n[ERROR: {data['detail']}]")


if __name__ == "__main__":
    print("=== Testing Streaming Endpoint ===\n")
    try:
        asyncio.run(test_streaming())
        print("\n\n✓ Streaming test completed successfully!")
    except Exception as e:
        print(f"\n\n✗ Streaming test failed: {e}")

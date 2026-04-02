import asyncio
import httpx
import time

async def send_request(client, prompt):
    start = time.time()
    async with client.stream("POST", "http://localhost:8000/generate", json={"prompt": prompt}) as response:
        async for line in response.aiter_lines():
            if line:
                print(f"[{prompt}] {line}")
    print(f"Done in {time.time() - start:.2f}s")

async def main():
    async with httpx.AsyncClient() as client:
        # Send 5 requests at once to trigger batching
        await asyncio.gather(*[send_request(client, f"Prompt {i}") for i in range(5)])

if __name__ == "__main__":
    asyncio.run(main())

import uuid
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from model import MockModel
from engine import ServingEngine

app = FastAPI()
model = MockModel()
global_queue = None
engine = None

@app.on_event("startup")
async def startup_event():
    global global_queue, engine
    global_queue = asyncio.Queue()
    engine = ServingEngine(model, global_queue)
    asyncio.create_task(engine.run_forever())

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    request_id = str(uuid.uuid4())
    
    # Output queue for this specific request
    output_queue = asyncio.Queue()
    await global_queue.put((request_id, prompt, output_queue))

    async def stream_tokens():
        while True:
            token = await output_queue.get()
            if token is None:
                break
            yield f"data: {token}\n\n"

    return StreamingResponse(stream_tokens(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

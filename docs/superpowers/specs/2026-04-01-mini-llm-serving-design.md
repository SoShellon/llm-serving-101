# Spec: Mini-LLM Serving Architecture (Educational)

**Date:** 2026-04-01
**Status:** Draft
**Topic:** High-performance LLM serving concepts (Queuing, Batching, Streaming)

## 1. Overview
A "Mini-Serving" system designed to teach the core architectural components of production LLM servers (like vLLM or TGI). It uses **Python** and **FastAPI** to demonstrate how multiple user requests are queued and processed in efficient batches to maximize "GPU" (mocked) throughput.

### The "Pizza Oven" Analogy
The GPU is an oven that can bake 1 batch of 10 pizzas just as fast as 1 pizza. This server focuses on the **Batcher** (the oven loader) and the **Queue** (the waiting room).

## 2. Requirements

### 2.1 Functional Requirements (The "What")
- **Token Generation:** The system must accept a text prompt and return a generated text response.
- **Request Queuing:** The system must place incoming requests into a first-in, first-out (FIFO) queue when the engine is busy.
- **Dynamic Batching:** The system must group multiple independent user requests into a single "batch" for simultaneous processing by the model engine.
- **Token Streaming:** The system must stream generated tokens back to the user one by one (SSE - Server-Sent Events style) rather than waiting for the full response.
- **Concurrent Support:** The API must remain responsive and accept new requests even while the model engine is processing a batch.

### 2.2 Non-Functional Requirements (The "How Well")
- **Throughput Efficiency:** The system must demonstrate higher tokens-per-second (TPS) when multiple requests are batched compared to single-request processing.
- **Low Latency (Wait Time):** The batching delay (the "wait" for more requests) must be configurable and minimal (default < 50ms) to ensure low first-token latency.
- **Concurrency:** The system should handle at least 10 simultaneous generation requests without dropping connections.
- **Observability:** The system must log clear indicators of "Queue Size," "Current Batch Size," and "Token Generation" events for educational monitoring.
- **Maintainability:** Code must be modular, separating the API, the Batching Engine, and the Model Logic.

## 3. Rationale: Why These Requirements Matter

| Requirement | Why it matters in LLM Serving |
| :--- | :--- |
| **Dynamic Batching** | GPUs are "compute-bound" but "memory-starved." Processing one request uses 100% of the memory but only 5% of the math power. Batching lets us use that 95% of wasted math power for free. |
| **Request Queuing** | LLM generation takes a long time (seconds). Without a queue, a sudden burst of traffic would overwhelm the engine, causing it to drop requests or crash. Queuing ensures "Graceful Degradation." |
| **Token Streaming** | Waiting 10 seconds for a full paragraph feels slow. Seeing words appear instantly (Streaming) makes the UI feel fast and interactive, even if the total generation time is the same. |
| **Low Latency (Wait Time)** | If we wait too long to form a batch (e.g., 500ms), the first user in the batch feels a delay. We must balance "Efficiency" (big batches) with "Responsiveness" (low wait time). |
| **Observability** | In production (like vLLM), you can't see the GPU. Logs are the only way to know if your batching strategy is actually working or if your queue is getting too long. |

## 4. Architecture Components

### A. API Gateway (`app.py`)
- **Technology:** FastAPI + Uvicorn.
- **Role:** Accepts HTTP POST requests with a `prompt`.
- **Workflow:** 
    1. Generates a unique `request_id`.
    2. Pushes the request into a `GlobalQueue` (Python `asyncio.Queue`).
    3. Returns a `StreamingResponse` that waits for tokens from the `Engine`.

### B. Serving Engine (`engine.py`)
- **Role:** The orchestration layer.
- **Workflow (The Continuous Loop):**
    1. Wait for requests to appear in the `GlobalQueue`.
    2. **Dynamic Batching:** Wait up to 50ms to gather more requests (up to `MAX_BATCH_SIZE=8`).
    3. Send the batch to the `ModelEngine`.
    4. Distribute the generated tokens back to the correct client streams.

### C. Mock Model Engine (`model.py`)
- **Role:** Simulates the GPU math.
- **Functionality:** 
    - `generate(batch_prompts)`: An async generator that yields tokens for all prompts in the batch simultaneously.
    - Includes a realistic delay (e.g., 50ms per token) to simulate hardware latency.

### D. Documentation (`README.md`)
- Explains the "Life of a Request".
- Detailed breakdown of why Batching improves throughput.
- Instructions on how to run the `client.py` load test.

## 4. Data Flow
1. **User** -> `POST /generate` -> **App**
2. **App** -> `Queue.put()` -> **Queue**
3. **Engine** -> `Queue.get_batch()` -> **Batch**
4. **Batch** -> `Model.generate()` -> **Tokens**
5. **Tokens** -> `Stream` -> **User**

## 5. Success Criteria
- [ ] Multiple concurrent requests from `client.py` are processed in a single batch.
- [ ] Logs clearly show "Processing batch of size N".
- [ ] Tokens are streamed to the client as they are generated (not all at once).
- [ ] The system remains responsive under a "traffic spike" (10+ simultaneous requests).

## 6. Scope & Constraints (YAGNI)
- **No Real GPU:** We will mock the generation logic to keep it lightweight.
- **Single Process:** For simplicity, the Engine and API will run in the same process using `asyncio`.
- **No Persistence:** No database is required for this educational version.

# Mini LLM Serving

A high-performance, asynchronous LLM serving engine built with FastAPI. This project demonstrates dynamic batching and queuing to optimize GPU (or mock model) throughput.

## The "Pizza Oven" Analogy

Think of the Large Language Model (the GPU) as a **Pizza Oven**.

- **The Problem**: Heating up the oven and maintaining it is expensive. If you bake one pizza at a time, you're waiting for the crust to crisp while the rest of the oven's space is wasted.
- **The Solution (Batching)**: A professional pizza oven can hold multiple pizzas at once. It takes almost the same amount of time to bake 4 pizzas as it does to bake 1. 
- **The Chef (Serving Engine)**: Our `ServingEngine` acts as the chef. When an order comes in, the chef waits just a split second (`batch_timeout`) to see if another order arrives. If it does, both go into the oven together. If the oven is full (`max_batch_size`), it goes in immediately.
- **Result**: We serve more customers (higher throughput) without significantly increasing the wait time for any single customer.

## Life of a Request

1.  **Ingress**: A client sends a POST request to `/generate` with a prompt.
2.  **Registration**: The FastAPI app generates a unique `request_id` and an `output_queue` for that specific request.
3.  **The Global Queue**: The request is placed into a `global_queue`.
4.  **Dynamic Batching**: The `ServingEngine` pulls requests from the `global_queue`. It waits for at least one request, then attempts to fill a batch up to `max_batch_size` within a short `batch_timeout`.
5.  **Model Inference**: The batch of prompts is sent to the `MockModel`. The model simulates token generation, yielding a "token" for every prompt in the batch at each step.
6.  **Fan-out**: The `ServingEngine` takes the yielded tokens and distributes them to the respective `output_queue` of each request.
7.  **Streaming Response**: The `app.py` endpoint consumes its `output_queue` and streams the tokens back to the client using Server-Sent Events (SSE).

## Getting Started

### Prerequisites
- Python 3.8+
- `pip install fastapi uvicorn httpx`

### Running the Server
```bash
python app.py
```

### Running the Load Test
```bash
python client.py
```

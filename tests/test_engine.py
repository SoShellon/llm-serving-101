import pytest
import asyncio
from engine import ServingEngine
from model import MockModel

@pytest.mark.asyncio
async def test_engine_batching():
    model = MockModel(delay_per_token=0.01)
    queue = asyncio.Queue()
    engine = ServingEngine(model, queue, max_batch_size=2, batch_timeout=0.1)
    
    # Each item in queue is (request_id, prompt, output_queue)
    output_q1 = asyncio.Queue()
    output_q2 = asyncio.Queue()
    await queue.put(("id1", "prompt1", output_q1))
    await queue.put(("id2", "prompt2", output_q2))
    
    # Run engine for one iteration
    await engine.step()
    
    # Verify that we got tokens and then None (completion)
    assert not output_q1.empty()
    assert not output_q2.empty()
    
    # Read until None
    tokens1 = []
    while True:
        t = await output_q1.get()
        if t is None: break
        tokens1.append(t)
    assert len(tokens1) > 0

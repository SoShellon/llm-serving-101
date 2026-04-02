import asyncio
import time
from typing import List, Tuple, Dict
from model import MockModel

class ServingEngine:
    def __init__(self, model: MockModel, queue: asyncio.Queue, max_batch_size=4, batch_timeout=0.05):
        self.model = model
        self.queue = queue
        self.max_batch_size = max_batch_size
        self.batch_timeout = batch_timeout

    async def step(self):
        """Processes one batch of requests."""
        batch = []
        # Wait for at least one item
        item = await self.queue.get()
        batch.append(item)

        # Try to fill the batch
        start_time = time.time()
        while len(batch) < self.max_batch_size:
            wait_time = self.batch_timeout - (time.time() - start_time)
            if wait_time <= 0:
                break
            try:
                item = await asyncio.wait_for(self.queue.get(), timeout=wait_time)
                batch.append(item)
            except asyncio.TimeoutError:
                break

        print(f"--- Processing batch of size {len(batch)} ---")
        
        # Unpack batch: (request_id, prompt, output_queue)
        ids, prompts, outputs = zip(*batch)
        
        async for tokens in self.model.generate(list(prompts)):
            for i, token in enumerate(tokens):
                await outputs[i].put(token)
        
        # Signal completion
        for q in outputs:
            await q.put(None)

    async def run_forever(self):
        while True:
            await self.step()

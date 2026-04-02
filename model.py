import asyncio
import random
from typing import List, AsyncGenerator

class MockModel:
    def __init__(self, delay_per_token: float = 0.05):
        self.delay_per_token = delay_per_token

    async def generate(self, prompts: List[str]) -> AsyncGenerator[List[str], None]:
        # Simulate generating 5-10 tokens
        num_tokens = random.randint(5, 10)
        for i in range(num_tokens):
            await asyncio.sleep(self.delay_per_token)
            # Yield a 'token' for each prompt in the batch
            yield [f"token_{i}_for_{j}" for j in range(len(prompts))]

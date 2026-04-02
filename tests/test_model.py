import pytest
import asyncio
from model import MockModel

@pytest.mark.asyncio
async def test_mock_model_generation():
    model = MockModel(delay_per_token=0.01)
    prompts = ["Hello", "How are you?"]
    
    responses = []
    async for batch_tokens in model.generate(prompts):
        responses.append(batch_tokens)
    
    assert len(responses) > 0
    # Each yielded item should be a list of tokens for each prompt
    assert len(responses[0]) == len(prompts)

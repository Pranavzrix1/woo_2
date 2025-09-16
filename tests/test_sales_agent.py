import pytest
import asyncio
from app.agents.sales_executive_agent import SalesExecutiveAgent

class DummyPS:
    async def generate_short_text(self, prompt, max_tokens=250):
        return '{"pitch":"Quick pitch","recommendations":[{"title":"Sample Product","reason":"Good fit"}]}'
    async def find_product_by_title(self, title):
        return {"id":"p1","name":title}

class DummyES:
    async def fetch_relevant_chats(self, user_id, query_text, k=5):
        return [{"id":"c1","summary":"Bought noise cancelling headset","snippet":"liked bass"}]

@pytest.mark.asyncio
async def test_sales_agent_basic():
    agent = SalesExecutiveAgent(es=DummyES(), product_svc=DummyPS())
    out = await agent.process("I need headphones for travel", user_id="u1")
    assert "pitch" in out
    assert isinstance(out["recommendations"], list)
    assert out["recommendations"][0]["title"] == "Sample Product"

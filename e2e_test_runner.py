"""
E2E Test Runner for ai-product-search
Place this file at the project root (next to docker-compose.yml and app/).

What it does:
- Checks FastAPI health endpoint
- Sends 10 test queries to each agent via /api/chat
- Sends product-search queries to /api/products/search
- Checks intent detection responses and logs intent + confidence
- Checks Postgres connectivity and lists table count
- Checks Elasticsearch connectivity and index status
- Optionally checks Redis (if REDIS_URL provided)
- Attempts to refresh products via /api/products/refresh
- Produces a beautiful, timestamped log using rich

How to run:
1. Put this file at the project root (same level as `app/`).
2. Ensure your .env is configured and services (Postgres, Elasticsearch, app) are running.
3. Install dev deps: `pip install -r requirements.txt rich requests python-dotenv sqlalchemy elasticsearch redis` (adjust per your environment)
4. Run: `python e2e_test_runner.py`

Note: The script reads environment variables from `.env` if present. It uses these env vars (examples):
- APP_URL (defaults to http://localhost:8000)
- DATABASE_URL (SQLAlchemy URL for Postgres)
- ELASTIC_URL (e.g. http://localhost:9200)
- REDIS_URL (optional)

"""

from __future__ import annotations
import os
import sys
import time
import json
from datetime import datetime
from typing import List, Dict
import traceback

# Networking
import requests
from dotenv import load_dotenv

# DB / ES / Redis
from sqlalchemy import create_engine, text
from elasticsearch import Elasticsearch
try:
    import redis
except Exception:
    redis = None

# Nice logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler
import logging

# Load env from .env if present
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

APP_URL = os.getenv('APP_URL', 'http://localhost:8000')
DATABASE_URL = os.getenv('DATABASE_URL')
ELASTIC_URL = os.getenv('ELASTIC_URL', 'http://localhost:9200')
REDIS_URL = os.getenv('REDIS_URL')

# Endpoints
HEALTH_ENDPOINT = f"{APP_URL}/health"
CHAT_ENDPOINT = f"{APP_URL}/api/chat/"
PRODUCT_SEARCH_ENDPOINT = f"{APP_URL}/api/products/search"
REFRESH_PRODUCTS_ENDPOINT = f"{APP_URL}/api/products/refresh"

# Setup rich logger
console = Console()
logger = logging.getLogger('e2e')
logger.setLevel(logging.DEBUG)
handler = RichHandler(console=console, show_time=True, show_level=True, show_path=False)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

LOG_FILENAME = os.path.join(BASE_DIR, f"e2e_log_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.log")
file_handler = logging.FileHandler(LOG_FILENAME, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Agent test questions (10 per agent)
AGENT_QUESTIONS = {
    "product_finder_agent": [
        "I'm looking for wireless headphones under $100",
        "Show me red running shoes size 10",
        "Find budget laptops with 16GB RAM",
        "Any waterproof jackets for hiking?",
        "I need a phone with good camera and battery life",
        "Looking for a toddler's toy suitable for 3-year-olds",
        "Recommend ergonomic office chairs",
        "Search for bluetooth speakers with long battery",
        "Find skincare products for oily skin",
        "Filter smartwatches that support GPS"
    ],
    "general_agent": [
        "What's the difference between SSD and HDD?",
        "How do I track my order?",
        "Explain return policy for electronics",
        "Give me tips to choose running shoes",
        "How do promotions and coupons stack?",
        "What are the shipping options?",
        "How do I contact support?",
        "Can you summarize recent product reviews?",
        "Is there an express checkout available?",
        "What payment methods do you accept?"
    ],
    "intent_tests": [
        "I want to buy a laptop",
        "How much is the red jacket?",
        "I'm looking to return my order",
        "Where is my refund?",
        "Is this product waterproof?",
        "Show me similar products",
        "Do you have an extended warranty?",
        "Cancel my recent order",
        "What are the warranty terms?",
        "Help me find a gift for a 10 year old"
    ]
}

# Helper printing functions
def print_header(title: str):
    console.rule(f"[bold green]{title}")

def pretty_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)

# Health check
def check_health() -> bool:
    print_header('Service health')
    try:
        r = requests.get(HEALTH_ENDPOINT, timeout=5)
        r.raise_for_status()
        logger.info(f"Health: {r.status_code} {r.text}")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False

# Chat agent tests
def test_chat_agents():
    print_header('Chat agents')
    results = []
    for agent_name, questions in [('product_finder_agent', AGENT_QUESTIONS['product_finder_agent']),
                                  ('general_agent', AGENT_QUESTIONS['general_agent'])]:
        table = Table(title=f"Results for {agent_name}")
        table.add_column("#")
        table.add_column("Question")
        table.add_column("Intent")
        table.add_column("Confidence")
        table.add_column("Response (truncated)")

        for i, q in enumerate(questions, 1):
            payload = {"message": q}
            try:
                r = requests.post(CHAT_ENDPOINT, json=payload, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    intent = data.get('intent')
                    conf = data.get('confidence')
                    resp = data.get('response', '')
                    table.add_row(str(i), q, str(intent), str(conf), resp[:200].replace('\n',' '))
                    results.append((agent_name, q, intent, conf, resp))
                else:
                    table.add_row(str(i), q, 'HTTP_ERR', str(r.status_code), r.text[:200])
            except Exception as e:
                table.add_row(str(i), q, 'ERROR', '', str(e))
        console.print(table)
    return results

# Intent specific tests
def test_intents():
    print_header('Intent tests')
    table = Table(title='Intent detection')
    table.add_column('#')
    table.add_column('Message')
    table.add_column('Intent')
    table.add_column('Confidence')
    for i, q in enumerate(AGENT_QUESTIONS['intent_tests'], 1):
        try:
            r = requests.post(CHAT_ENDPOINT, json={"message": q}, timeout=8)
            d = r.json()
            table.add_row(str(i), q, str(d.get('intent')), str(d.get('confidence')))
        except Exception as e:
            table.add_row(str(i), q, 'ERROR', str(e))
    console.print(table)

# Product search tests
def test_product_search():
    print_header('Product search')
    queries = [
        'headphones', 'red shoes size 10', 'waterproof jacket', 'smartwatch GPS', 'laptop 16GB',
        'toddler toy', 'office chair ergonomic', 'bluetooth speaker', 'skincare oily skin', 'budget phone'
    ]

    table = Table(title='Product search results')
    table.add_column('#')
    table.add_column('Query')
    table.add_column('Hits')
    table.add_column('Sample product fields')

    for i, q in enumerate(queries, 1):
        try:
            r = requests.get(PRODUCT_SEARCH_ENDPOINT, params={'q': q, 'limit': 5}, timeout=10)
            if r.status_code == 200:
                items = r.json()
                fields = set()
                if isinstance(items, list) and len(items) > 0:
                    # accumulate keys from first product
                    fields = set(items[0].keys())
                table.add_row(str(i), q, str(len(items) if isinstance(items, list) else 0), ', '.join(sorted(fields)))
                # log a sample
                logger.info(f"Sample for '{q}': {pretty_json(items[0]) if items else 'NO_RESULTS'}")
            else:
                table.add_row(str(i), q, f'HTTP_{r.status_code}', r.text[:80])
        except Exception as e:
            table.add_row(str(i), q, 'ERROR', str(e))
    console.print(table)

# Refresh products
def refresh_products():
    print_header('Refresh products')
    try:
        r = requests.post(REFRESH_PRODUCTS_ENDPOINT, timeout=30)
        if r.status_code == 200:
            logger.info(f"Refresh response: {r.json()}")
        else:
            logger.error(f"Refresh failed: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Refresh exception: {e}")

# Postgres check
def check_postgres():
    print_header('Postgres check')
    if not DATABASE_URL:
        logger.warning('DATABASE_URL not set; skipping Postgres checks')
        return
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            res = conn.execute(text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"))
            count = res.scalar()
            logger.info(f"Public table count: {count}")
            # check for products table
            r2 = conn.execute(text("SELECT to_regclass('public.products');"))
            exists = r2.scalar()
            logger.info(f"products table exists: {bool(exists)}")
    except Exception as e:
        logger.error(f"Postgres check failed: {e}\n{traceback.format_exc()}")

# Elasticsearch check
def check_elasticsearch():
    print_header('Elasticsearch check')
    try:
        es = Elasticsearch([ELASTIC_URL], request_timeout=10)
        alive = es.ping()
        logger.info(f"Elasticsearch ping: {alive}")
        if alive:
            # list indexes (safe)
            # idx = es.indices.get_alias('*')
            # With
            try:
                idx = es.indices.get_alias(name='*')
            except TypeError:
                # fallback if older client wants 'index' keyword
                idx = es.indices.get_alias(index='*')
            logger.info(f"Indices found: {list(idx.keys())[:20]}")
            # if there is a products index, show stats
            for name in list(idx.keys()):
                if 'product' in name.lower() or 'products' in name.lower():
                    st = es.indices.stats(index=name)
                    logger.info(f"Stats for {name}: {pretty_json(st.get('indices', {}).get(name, {}))[:1000]}")
    except Exception as e:
        logger.error(f"Elasticsearch check failed: {e}\n{traceback.format_exc()}")

# Redis/dspy check
def check_redis():
    print_header('Redis / dspy check')
    if not REDIS_URL:
        logger.warning('REDIS_URL not set; skipping Redis checks')
        return
    if not redis:
        logger.warning('redis package not installed; skipping Redis checks')
        return
    try:
        r = redis.Redis.from_url(REDIS_URL)
        pong = r.ping()
        logger.info(f"Redis ping: {pong}")
        # sample keys
        keys = r.keys()[:20]
        logger.info(f"Redis sample keys (up to 20): {keys}")
    except Exception as e:
        logger.error(f"Redis check failed: {e}\n{traceback.format_exc()}")

# LLM sanity check (a general question expecting LLM answer)
def check_llm():
    print_header('LLM sanity check')
    q = 'Summarize the pros and cons of buying a mid-range laptop in 3 bullet points.'
    try:
        r = requests.post(CHAT_ENDPOINT, json={"message": q}, timeout=12)
        if r.status_code == 200:
            d = r.json()
            logger.info(f"LLM response (truncated): {str(d.get('response'))[:800]}")
        else:
            logger.error(f"LLM endpoint HTTP {r.status_code}: {r.text}")
    except Exception as e:
        logger.error(f"LLM check failed: {e}\n{traceback.format_exc()}")


def main():
    console.print(Panel(Text('E2E Test Runner for ai-product-search', justify='center', style='bold white on blue')))
    # 1. health
    ok = check_health()
    if not ok:
        logger.error('Health check failed, many tests will likely fail.')

    # 2. chat agents
    test_chat_agents()

    # 3. intent tests
    test_intents()

    # 4. product search
    test_product_search()

    # 5. refresh products
    refresh_products()

    # 6. Postgres
    check_postgres()

    # 7. Elasticsearch
    check_elasticsearch()

    # 8. Redis / dspy
    check_redis()

    # 9. LLM
    check_llm()

    console.print(Panel(Text(f'Completed E2E checks. Log saved to {LOG_FILENAME}', justify='center', style='bold white on green')))

if __name__ == '__main__':
    main()

import json
from llm.openrouter_client import OpenRouterClient
from llm.schemas import EVENT_SCHEMA

def classify(article_text):
    raw=OpenRouterClient().extract_event(article_text,EVENT_SCHEMA)
    event=json.loads(raw)
    if event['demand_direction'] not in {'positive','negative','neutral'} or not 0<=event['confidence']<=1 or not 0<=event['relevance_score']<=1: raise ValueError('Invalid event classification')
    return event

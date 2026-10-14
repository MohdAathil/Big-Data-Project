"""Optional OpenRouter client; never embeds or logs credentials."""
import os, requests
from dotenv import load_dotenv
load_dotenv()
class OpenRouterClient:
    def __init__(self):
        self.key=os.getenv('OPENROUTER_API_KEY'); self.base=os.getenv('OPENROUTER_BASE_URL','https://openrouter.ai/api/v1'); self.model=os.getenv('OPENROUTER_MODEL','google/gemini-2.0-flash-001')
        if not self.key: raise RuntimeError('OPENROUTER_API_KEY is unset; live event extraction is disabled')
    def extract_event(self, article_text, schema):
        response=requests.post(self.base.rstrip('/')+'/chat/completions',headers={'Authorization':f'Bearer {self.key}','Content-Type':'application/json'},json={'model':self.model,'messages':[{'role':'system','content':'Extract only facts from the supplied article. Do not invent numerical forecasts or production decisions. Return JSON matching the schema.'},{'role':'user','content':article_text}],'response_format':{'type':'json_schema','json_schema':{'name':'manufacturing_event','strict':True,'schema':schema}}},timeout=30)
        response.raise_for_status(); return response.json()['choices'][0]['message']['content']

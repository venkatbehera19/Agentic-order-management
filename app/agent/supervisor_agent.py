import json
import re
from langchain_core.messages import HumanMessage
from app.llms.openai_chat_client import default_chat_client
from app.prompts.supervisor_prompt import build_supervisor_prompt

class SupervisorAgent:
    """
    Decides which workflow to trigger based on user input
    """
    def __init__(self):
        self.model = default_chat_client

    def route(self, query: str, history) -> dict:
        prompt = build_supervisor_prompt(query, history)
        response = self.model.invoke([
            HumanMessage(content=prompt)
        ])

        return self._safe_parse(response.content)
    
    def _safe_parse(self, text: str):
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass

        return {"intent": "unknown", "product_id": None, "quantity": None}
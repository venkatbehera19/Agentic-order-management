import json
import re
from langchain_core.messages import HumanMessage
from app.llms.openai_chat_client import default_chat_client

class SupervisorAgent:
    """
    Decides which workflow to trigger based on user input
    """
    def __init__(self):
        self.model = default_chat_client

    def route(self, query: str) -> dict:
        prompt = f"""
        You are a supervisor agent.

        Your job:
        - Understand user intent
        - Route to correct system

        Return ONLY JSON:

        {{
        "intent": "create_order | check_stock | cancel_order | unknown",
        "product_name": str | null,
        "quantity": int | null
        }}

        Rules:
        - No explanation
        - No extra text
        - If not found → use null

        User Query:
        {query}
        """
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
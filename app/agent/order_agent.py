from langchain.agents import create_agent
from app.llms.openai_chat_client import default_chat_client
from app.tools import TOOLS
from app.prompts.order_agent_prompt import ORDER_AGENT_PROMPT
from langchain.messages import HumanMessage

class OrderAgent:
    """
    Order agent responsible for creating an order step-by-step using tools.
    """
    def __init__(self):
        self.model = default_chat_client
        self.agent = create_agent(
            model=self.model,
            tools=TOOLS,
            system_prompt=ORDER_AGENT_PROMPT
        )

    def run(self, product_id: int, quantity: int):
        """Execute order creation flow.

        Args:
            product_id (int): Product ID
            quantity (int): Quantity

        Returns:
            dict: Agent response
        """
        user_input = f"""
        Place an order with:
        product_id = {product_id}
        quantity = {quantity}
        """

        response = self.agent.invoke({
            "messages": [
                HumanMessage(content=user_input)
            ]
        })

        return self._parse_response(response)
    
    def _parse_response(self, response):
        """Extract final response safely"""
        try:
            messages = response.get("messages", [])
            if messages:
                return {
                    "success": True,
                    "message": messages[-1].content
                }
            return {"success": False, "message": "No response"}

        except Exception as e:
            return {"success": False, "message": str(e)}
from langchain_core.messages import HumanMessage, AIMessage
from app.llms.openai_chat_client import default_chat_client

class ResponseAgent:
    """
    gives the wellformated output so any one can know it.
    """
    def __init__(self):
        self.model = default_chat_client

    def generate(self, query: str, result: dict, chat_history) -> str:
        """
        Convert system result into conversational response using LLM
        """
        history_messages = []
        for msg in chat_history.messages:
            if msg.type == "human":
                history_messages.append(HumanMessage(content=msg.content))
            else:
                history_messages.append(AIMessage(content=msg.content))


        prompt = f"""
            You are a helpful shopping assistant.

            Generate a natural, friendly response.

            User Query
            {query}
            
            System Result:
            {result}

            Rules:
            - Be conversational
            - If success → confirm order nicely
            - If error → explain clearly and suggest next step
            - Keep it short
        """
        response = self.model.invoke(
            history_messages + [HumanMessage(content=prompt)]
        )

        return response.content
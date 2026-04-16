from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.llms.openai_chat_client import default_chat_client
from app.prompts.response_agent_prompt import RESPONSE_AGENT_PROMPT

class ResponseAgent:
    """
    Generates well-formatted conversational responses using LLM.
    """
    def __init__(self):
        self.model = default_chat_client

    def _format_history(self, chat_history: list):
        """
        Convert stored history into LangChain message format
        """
        messages = []

        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        return messages

    def generate(self, query: str, result: dict, chat_history: list) -> str:
        """
        Convert system result into conversational response using LLM
        """

        history_messages = self._format_history(chat_history)

        user_prompt = f"""
        User Query:
        {query}

        System Result:
        {result}
        """

        response = self.model.invoke(
            [SystemMessage(content=RESPONSE_AGENT_PROMPT)]
            + history_messages[-6:] 
            + [HumanMessage(content=user_prompt)]
        )

        return response.content
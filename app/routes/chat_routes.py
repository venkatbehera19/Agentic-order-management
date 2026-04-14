from fastapi import FastAPI, APIRouter, status
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.config.env_config import settings
from app.config.log_config import logger
from app.agent.order_agent import OrderAgent
from app.graph.graph import order_graph

router = APIRouter(tags=["chat"])

store = {}
def get_session_history(session_id: str):
  if session_id not in store:
    store[session_id] = InMemoryChatMessageHistory()
  return store[session_id]


@router.get('/chat', status_code=status.HTTP_200_OK)
async def chat(query: str, session_id: str):
    """ Chat Methods for llm response

    Args:
        query: user message to llm
        session_id: session for the user

    Response:
        answer: llm answer
    """
    # order_agent = OrderAgent()
    # result = order_agent.run(product_id=1, quantity=1)
    # return result
    result = order_graph.invoke({
        "product_id": 1,
        "quantity": 1,
        "order_id": None,
        "success": True,
        "error": None,
    })

    return result

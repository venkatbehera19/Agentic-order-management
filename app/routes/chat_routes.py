from fastapi import FastAPI, APIRouter, status
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.config.env_config import settings
from app.config.log_config import logger
from app.agent.order_agent import OrderAgent
from app.graph.graph import order_graph
from app.agent.supervisor_agent import SupervisorAgent
from app.agent.response_agent import ResponseAgent

router = APIRouter(tags=["chat"])
supervisor = SupervisorAgent()
response_agent = ResponseAgent()

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
    chat_history = get_session_history(session_id)
    chat_history.add_user_message(query)

    decision = supervisor.route(query)
    if decision["intent"] == "create_order":
      result = order_graph.invoke({
        "product_name": decision["product_name"],
        "quantity": decision["quantity"],
        "order_id": None,
        "success": True,
        "error": None,
      })
    else:
      result = {"success": False, "error": "Intent not supported"}

    final_response = response_agent.generate(query, result, chat_history)
    chat_history.add_ai_message(final_response)

    return {
        "response": final_response,
        "raw": result   # optional (for debugging)
    }
    # order_agent = OrderAgent()
    # result = order_agent.run(product_id=1, quantity=1)
    # return result

    # result = order_graph.invoke({
    #     "product_id": 1,
    #     "quantity": 1,
    #     "order_id": None,
    #     "success": True,
    #     "error": None,
    # })

    # return result
    

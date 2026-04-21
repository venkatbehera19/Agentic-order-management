from fastapi import FastAPI, APIRouter, status
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.repository.qdrant_repo import QdrantRepository
from app.config.env_config import settings
from app.config.log_config import logger
# from app.agent.order_agent import OrderAgent
from app.graph.graph import build_research_graph
from app.agent.supervisor_agent import SupervisorAgent
from app.agent.response_agent import ResponseAgent
from app.memory import memory
from app.utils.embedding_utils import embeddings_client
from app.constants.app_constants import VECTOR_DB
from difflib import get_close_matches

router = APIRouter(tags=["chat"])
supervisor = SupervisorAgent()
response_agent = ResponseAgent()
graph = build_research_graph()
qdrant_db = QdrantRepository(embeddings=embeddings_client, collection_name=VECTOR_DB.COLLECTION_NAME.value)

def resolve_product(session_id: str, user_input: str):
  products = memory.get_products(session_id)

  if not products:
    return None

  user_input = user_input.lower()

  for p in products:
    if str(p["index"]) in user_input:
      return p["product_id"]

  names = [p["name"] for p in products]
  match = get_close_matches(user_input, names, n=1, cutoff=0.5)

  if match:
    selected = next(p for p in products if p["name"] == match[0])
    return selected["product_id"]

  return None

@router.get('/chat', status_code=status.HTTP_200_OK)
async def chat(query: str, session_id: str):
  """ Chat Methods for llm response

    Args:
        query: user message to llm
        session_id: session for the user

    Response:
        answer: llm answer
  """
  memory.add_user_message(session_id, query)
  history = memory.get_messages(session_id)

  decision = supervisor.route(query, history)
  logger.info(decision)

  if decision["intent"] == "create_order":
    product_id = resolve_product(session_id, query)

    if not product_id:
      return {
        "response": "I couldn’t identify the product. Please specify which one you want.",
        "raw": {"success": False}
      }
    
    result = graph.invoke({
      "product_id": product_id,
      "product_name": decision["product_name"],
      "quantity": 1,
      "order_id": None,
      "success": True,
      "error": None,
    }, 
    config={
      "configurable": {
          "thread_id": session_id
      }
    })
    logger.info(result)
    if result.get("success"):
      memory.add_order(session_id, {
        "product_name": decision["product_name"],
        "quantity": 1,
        "order_id": result.get("order_id")
      })
  elif decision["intent"] == "search_product":
    results = qdrant_db.search(decision["query"])
    memory.add_products(session_id, results)
    result =  {
      "success": True,
      "type": "search",
      "results": results
    }

  else:
    result = {"success": False, "error": "Intent not supported"}

  final_response = response_agent.generate(query, result, history)
  return {
    "response": final_response,
    "raw": result  
  }


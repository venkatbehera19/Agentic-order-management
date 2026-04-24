from fastapi import FastAPI, APIRouter, status
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.repository.qdrant_repo import QdrantRepository
from app.config.env_config import settings
from app.config.log_config import logger
# from app.agent.order_agent import OrderAgent
from app.graph.graph import build_research_graph
from app.graph.cancel_order.graph import build_cancel_order_graph
from app.agent.supervisor_agent import SupervisorAgent
from app.agent.response_agent import ResponseAgent
from app.memory import memory
from app.utils.embedding_utils import embeddings_client
from app.constants.app_constants import VECTOR_DB
from difflib import get_close_matches
from langgraph.types import Command
from app.agent.sql_agent import SQLAgent
from dataclasses import dataclass

router = APIRouter(tags=["chat"])
supervisor = SupervisorAgent()
response_agent = ResponseAgent()
graph = build_research_graph()
cancel_order_graph = build_cancel_order_graph()
sql_agent = SQLAgent()
qdrant_db = QdrantRepository(embeddings=embeddings_client, collection_name=VECTOR_DB.COLLECTION_NAME.value)

@dataclass
class Context:
  session_id: str

def resolve_product(session_id: str, user_input: str):
  products = memory.get_products(session_id)

  if not products:
    return None

  user_input = user_input.lower()

  for p in products:
    if str(p["index"]) in user_input:
      memory.set_selected_product(session_id, p) 
      return p

  names = [p["name"] for p in products]
  match = get_close_matches(user_input, names, n=1, cutoff=0.5)

  if match:
    selected = next(p for p in products if p["name"] == match[0])
    memory.set_selected_product(session_id, selected)  # ✅ STORE
    return selected

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

  config={
    "configurable": {
      "thread_id": session_id
    }
  }

  if query.lower() in ["yes", "no", "confirm", "cancel"]:
    logger.info("Resuming graph with user confirmation")

    result = graph.invoke(
      Command(resume=query),
      config=config
    )

    if result.get("success") and result.get("order_id"):
      memory.add_order(session_id, {
          "product_name": "unknown",
          "quantity": 1,
          "order_id": result.get("order_id")
      })

  else:
    decision = supervisor.route(query, history)
    logger.info(f"DECISION {decision}")
    if decision["intent"] == "create_order":
      selected = resolve_product(session_id, query)

      if not selected:
        return {
            "response": "Please select a product first.",
            "raw": {"success": False}
        }
      
      print('SELECTED',selected)
      
      result = graph.invoke({
        "product_id": selected["product_id"],
        "product_name": selected["name"],
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
          "product_name": selected["name"],
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
    elif decision["intent"] == "search_sql":
      if decision.get("product_name"):
        sql_query = f"find product {decision['product_name']}"
      else:
        sql_query = decision["query"]

      sql_results = sql_agent.run(sql_query)
      print("SQL", sql_results)
      normalized = [
          {
              "product_id": p.get("product_id"),
              "name": p.get("name") or p.get("productName")
          }
          for p in sql_results
          if p.get("product_id")
      ]
      print("SQL", normalized)

      memory.add_products(session_id, normalized)

      result = {
          "success": True,
          "type": "sql_search",
          "results": normalized
      }
    elif decision["intent"] == "cancel_order":
      result = cancel_order_graph.invoke(
        {
          "product_id": decision["product_id"],
          "product_name": decision["product_name"],
          "quantity": 1,
          "order_id": decision['order_id'],
          "success": True,
          "error": None,
        }, 
        config={
          "configurable": {
              "thread_id": session_id
          }
        },
        context=Context(session_id=session_id)
      )

    else:
      result = {"success": False, "error": "Intent not supported"}

  # if "__interrupt__" in result:
  #   return {
  #     "response": result["__interrupt__"],
  #     "raw": result
  # }
  # final_response = response_agent.generate(query, result, history)
  # memory.add_ai_message(session_id, final_response)
  # return {
  #   "response": final_response,
  #   "raw": result  
  # }


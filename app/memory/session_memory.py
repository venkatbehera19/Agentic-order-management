from collections import defaultdict
from typing import Dict, List, Any

class SessionMemmory:
    """Using for in memory session"""
    def __init__(self):
        self.store: Dict[str, Dict[str, List[Any]]] = defaultdict(
            lambda: {
                "messages": [],
                "orders": [],
                "products": [],
                "selected_product": None 
            }
        )


    def add_user_message(self, session_id: str, message: str):
        """add the user message to the perticular session
            
        Args:
                session_id: key for that session history
                message: message that needs to be added
            
        """
        self.store[session_id]["messages"].append({
            "role": "user",
            "content": message
        })  


    def add_ai_message(self, session_id: str, message: str):
        """add the ai message to the perticular session
            
        Args:
            session_id: key for that session history
            message: message that needs to be added
            
        """
        self.store[session_id]["messages"].append({
            "role": "assistant",
            "content": message
        })

    def get_messages(self, session_id: str, limit: int = 10):
        """Get the whole message to the perticular session
            
        Args:
            session_id: key for that session history
            limit: message that needs to be added
            
        """
        return self.store[session_id]["messages"][-limit:]
    
    def add_order(self, session_id: str, order_data: dict):
        """add the order data message to the perticular session
            
        Args:
            session_id: key for that session history
            order_data: order message that needs to be added
            
        """
        self.store[session_id]["orders"].append(order_data)

    def add_products(self, session_id: str, products: list):
        """Store last searched products"""

        formatted = [
            {
                "index": i + 1,
                "product_id": p["product_id"],
                "name": p["name"]
            }
            for i, p in enumerate(products)
        ]

        self.store[session_id]["products"] = formatted


    def get_full_session(self, session_id: str):
        """get the full session of a session_id

        Args:
            session_id: key for that session history

        """
        return self.store[session_id]

    def clear(self, session_id: str):
        """Clear the full session of a session_id

        Args:
            session_id: key for that session history

        """
        self.store[session_id] = {
            "messages": [],
            "orders": [],
            "products": []
        }

    def get_products(self, session_id: str):
        return self.store[session_id].get("products", [])
    
    def set_selected_product(self, session_id: str, product: dict):
        self.store[session_id]["selected_product"] = product


    def get_selected_product(self, session_id: str):
        return self.store[session_id].get("selected_product")
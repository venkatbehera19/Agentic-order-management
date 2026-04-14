from langgraph.graph import StateGraph, END
from app.graph.state import OrderState
from app.graph.nodes import check_product_node, check_stock_node, update_inventory_node, create_order_node, order_audit_node, email_node, check_failure
from app.db.database import get_db

builder = StateGraph(OrderState)

builder.add_node("check_product", check_product_node)
builder.add_node("check_stock", check_stock_node)
builder.add_node("update_inventory", update_inventory_node)
builder.add_node("create_order", create_order_node)

builder.add_node("order_audit", order_audit_node)
builder.add_node("send_email", email_node)

builder.set_entry_point("check_product")

builder.add_conditional_edges(
    "check_product", 
    check_failure, {
        "fail": END, 
        "continue": "check_stock" 
    }
)

builder.add_conditional_edges(
    "check_stock", 
    check_failure, {
        "fail": END, 
        "continue": "update_inventory" 
    }
)

builder.add_conditional_edges(
    "update_inventory", 
    check_failure, {
        "fail": END, 
        "continue": "create_order" 
    }
)

builder.add_conditional_edges(
    "create_order", 
    check_failure, {
        "fail": END, 
        "continue": "order_audit" 
    }
)

builder.add_conditional_edges(
    "order_audit", 
    check_failure, {
        "fail": END, 
        "continue": "send_email" 
    }
)

builder.add_edge("send_email", END)

order_graph = builder.compile()
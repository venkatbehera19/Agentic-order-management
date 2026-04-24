from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from app.graph.cancel_order.state import CancelState
from .nodes import resolve_order_node, check_order_node, cancel_order_node, log_order_audit_node, inventory_audit_node, email_node, update_inventory_node, check_failure

checkpointer = InMemorySaver()

def build_cancel_order_graph():
    """This is used to build the workflow"""
    builder = StateGraph(CancelState)

    builder.add_node("resolve_order", resolve_order_node)
    builder.add_node("check_order", check_order_node)
    builder.add_node('update_inventory', update_inventory_node)
    builder.add_node("cancel_order", cancel_order_node)
    builder.add_node("log_order_audit", log_order_audit_node)
    builder.add_node("inventory_audit", inventory_audit_node)
    builder.add_node("send_email", email_node)

    builder.set_entry_point("resolve_order")

    builder.add_conditional_edges("resolve_order", check_failure, {
        "fail": END,
        "continue": "check_order"
    })

    builder.add_conditional_edges("check_order", check_failure, {
        "fail": END,
        "continue": "cancel_order"
    })

    builder.add_conditional_edges("cancel_order", check_failure, {
        "fail": END,
        "continue": "update_inventory"
    })

    builder.add_conditional_edges("update_inventory", check_failure, {
        "fail": END,
        "continue": "inventory_audit"
    })

    builder.add_conditional_edges("inventory_audit", check_failure, {
        "fail": END,
        "continue": "log_order_audit"
    })

    builder.add_conditional_edges("log_order_audit", check_failure, {
        "fail": END,
        "continue": "send_email"
    })

    builder.add_edge("send_email", END)

    builder.add_edge("send_email", END)
    cancel_order_graph = builder.compile(checkpointer=checkpointer)

    return cancel_order_graph
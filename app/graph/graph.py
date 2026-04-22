from langgraph.graph import StateGraph, END
from app.graph.state import OrderState
from app.graph.nodes import check_product_node, check_stock_node, update_inventory_node, create_order_node, order_audit_node, email_node, check_failure, resolve_product_node, inventory_audit_node, ask_confirmation_node
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

def build_research_graph():
    """This is used to build the workflow"""
    builder = StateGraph(OrderState)

    # nodes 
    builder.add_node("resolve_product", resolve_product_node)
    builder.add_node("check_product", check_product_node)
    builder.add_node("check_stock", check_stock_node)
    builder.add_node("ask_confirmation", ask_confirmation_node)
    builder.add_node("update_inventory", update_inventory_node)
    builder.add_node("create_order", create_order_node)
    builder.add_node("inventory_audit", inventory_audit_node)
    builder.add_node("order_audit", order_audit_node)
    builder.add_node("send_email", email_node)

    builder.set_entry_point("check_product")

    builder.add_conditional_edges(
        "resolve_product", 
        check_failure, {
            "fail": END, 
            "continue": "check_product" 
        }
    )

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
            "continue": "ask_confirmation" 
        }
    )

    builder.add_conditional_edges(
        "ask_confirmation", 
        check_failure, {
            "fail": END, 
            "continue": "update_inventory" 
        }
    )

    builder.add_conditional_edges(
        "update_inventory", 
        check_failure, {
            "fail": END, 
            "continue": "inventory_audit" 
        }
    )

    builder.add_conditional_edges(
        "inventory_audit",
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
    order_graph = builder.compile(checkpointer=checkpointer)

    return order_graph
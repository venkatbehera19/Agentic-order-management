from .state import CancelState
from app.memory import memory
from app.tools.order import cancel_order_in_db, get_order_by_id
from app.tools.audit import log_inventory_audit, log_order_audit
from app.tools.email import send_email
from app.tools.inventory import update_inventory_add
from langgraph.runtime import Runtime

def update_inventory_node(state: CancelState):
    result = update_inventory_add(
        product_id = state['product_id'],
        quantity = state['quantity'] | 1
    )
    if not result["success"]:
        return {
            **state,
            "success": False,
            "error": result["error"]
        }
    return {
        **state,
        "success": True
    }

def resolve_order_node(state: CancelState, runtime: Runtime):
    if state.get("order_id"):
        return state
    
    session_id = runtime.context.session_id
    
    last_order = memory.get_last_order(session_id)

    if not last_order:
        return {
            **state,
            "success": False,
            "error": "No order found to cancel"
        }
    
    return {
        **state,
        "order_id": last_order["order_id"],
        "success": True
    }

def check_order_node(state: CancelState):
    order = get_order_by_id(order_id=state["order_id"])

    if not order:
        return {
            **state,
            "success": False,
            "error": "Order not found"
        }

    return {
        **state,
        "order_exists": True,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "success": True
    }

def cancel_order_node(state: CancelState):
    cancel_order_in_db(order_id = state["order_id"])

    return {
        **state,
        "success": True
    }




def log_order_audit_node(state: CancelState):
    try:
        log_order_audit(
            order_id = state['order_id'],
            prev_status=None,
            new_status="CANCELLED",
            remarks="Order Cancelled"
        )
    except Exception:
        pass

    return {**state, "success": True}


def inventory_audit_node(state: CancelState):
    """
    Log inventory change after stock update
    """
    result = log_inventory_audit(
        product_id = state['product_id'],
        change_type="ADD",
        quantity_changed=state["quantity"],
        remarks="Order cancelled - stock added"
    )
    if not result["success"]:
        return {
            **state,
            "success": False,
            "error": result["error"]
        }
    return {
        **state,
        "success": True
    }

def email_node(state: CancelState):
    send_email(
        to="customer@email.com",
        subject="Order Confirmed",
        body=f"Order {state['order_id']} Cancelled successfully"
    )

    return {**state, "success": True}

def check_failure(state: CancelState):
    return "fail" if not state.get("success") else "continue"
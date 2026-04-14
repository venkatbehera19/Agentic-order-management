from app.tools.inventory import check_product_exists, get_stock_quantity, update_inventory
from app.tools.order import create_order
from app.tools.audit import log_order_audit
from app.tools.email import send_email
from .state import OrderState

def check_product_node(state: OrderState):
    result = check_product_exists(state['product_id'])
    if not result["exists"]:
        return { **state, "success": False, "error": "Product not found" }
    
    return { **state, "product_exists": True, "success": True }


def check_stock_node(state: OrderState):
    result = get_stock_quantity(state['product_id'])

    if "error" in result:
        return {**state, "success": False, "error": result["error"]}

    if result["stock"] < state["quantity"]:
        return {**state, "success": False, "error": "Insufficient stock"}

    return {**state, "stock": result["stock"], "success": True}


def update_inventory_node(state: OrderState):
    result = update_inventory(state['product_id'], state['quantity'])

    if "error" in result:
        return {**state, "success": False, "error": result["error"]}

    return {**state, "success": True}


def create_order_node(state: OrderState):
    result = create_order(state['product_id'], state['quantity'])

    if "error" in result:
        return {**state, "success": False, "error": result["error"]}

    return {**state, "order_id": result["order_id"], "success": True}


def order_audit_node(state: OrderState):
    result = log_order_audit(
        order_id = state['order_id'],
        prev_status=None,
        new_status="PLACED",
        remarks="Order created"
    )

    if "error" in result:
        return {**state, "success": False, "error": result["error"]}

    return {**state, "success": True}


def email_node(state: OrderState):
    result = send_email(
        to="customer@email.com",
        subject="Order Confirmed",
        body=f"Order {state['order_id']} placed successfully"
    )

    return {**state, "success": True}

def check_failure(state: OrderState):
    return "fail" if not state["success"] else "continue"

# def inventory_audit_node(state: OrderState):
#     result = log_inventory_audit(
#         product_id = state["product_id"],
#         change = state["quantity"]
#     )
#     if "error" in result:
#         return {**state, "success": False, "error": result["error"]}

#     return {**state, "success": True}
from app.tools.inventory import check_product_exists, get_stock_quantity, update_inventory, get_product_id_by_name
from app.tools.order import create_order
from app.tools.audit import log_order_audit, log_inventory_audit
from app.tools.email import send_email
from .state import OrderState
from app.config.log_config import logger


def resolve_product_node(state: OrderState):
    result = get_product_id_by_name(state['product_name'])
    if not result["success"]:
        return {
            **state,
            "success": False,
            "error": result["error"]
        }

    return {
        **state,
        "product_id": result["data"]["product_id"],
        "success": True
    }

def check_product_node(state: OrderState):
    result = check_product_exists(state['product_id'])
    if not result["success"]:
        return {
            **state,
            "success": False,
            "error": result["error"]
        }
    
    if not result["data"]["exists"]:
        return {
            **state,
            "success": False,
            "error": "Product not found"
        }

    return {
        **state,
        "product_exists": True,
        "success": True
    }


def check_stock_node(state: OrderState):
    result = get_stock_quantity(state['product_id'])

    if not result["success"]:
        return {
            **state,
            "success": False,
            "error": result["error"]
        }
    
    stock = result["data"]["stock"]

    if stock < state["quantity"]:
        return {
            **state,
            "success": False,
            "error": "Insufficient stock"
        }
    
    return {
        **state,
        "stock": stock,
        "success": True
    }


def update_inventory_node(state: OrderState):
    result = update_inventory(state['product_id'], state['quantity'])

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

def inventory_audit_node(state: OrderState):
    """
    Log inventory change after stock update
    """
    result = log_inventory_audit(
        product_id = state['product_id'],
        change_type="REMOVE",
        quantity_changed=state["quantity"],
        remarks="Order placed - stock reduced"
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



def create_order_node(state: OrderState):
    result = create_order(state['product_id'], state['quantity'])

    if not result["success"]:
        return {
            **state,
            "success": False,
            "error": result["error"]
        }

    return {
        **state,
        "order_id": result["data"]["order_id"],
        "success": True
    }


def order_audit_node(state: OrderState):
    try:
        log_order_audit(
            order_id = state['order_id'],
            prev_status=None,
            new_status="PLACED",
            remarks="Order created"
        )
    except Exception:
        pass

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

from langchain_core.tools import StructuredTool
from .inventory import check_product_exists, get_stock_quantity, update_inventory
from .order import create_order
from .audit import log_order_audit
from .email import send_email
from app.schemas.tools.order_schemas import *

check_product_tool = StructuredTool(
    name="check_product_exists",
    func=check_product_exists,
    description="Check product existence",
    args_schema=ProductInput
)

get_stock_tool = StructuredTool(
    name="get_stock_quantity",
    func=get_stock_quantity,
    description="Get stock quantity",
    args_schema=ProductInput
)

update_inventory_tool = StructuredTool(
    name="update_inventory",
    func=update_inventory,
    description="Update Inventory",
    args_schema=UpdateInventoryInput 
)

create_order_tool = StructuredTool(
    name="create_order",
    func=create_order,
    description="Create the Order",
    args_schema=UpdateInventoryInput 
)

log_order_audit_tool = StructuredTool(
    name="log_order_audit",
    func=log_order_audit,
    description="Create the Order Audit",
    args_schema=LogOrderAuditInput
)

send_email_tool = StructuredTool(
    name="send_email",
    func=send_email,
    description="Send Email",
    args_schema=EmailInput
)

TOOLS = [
    check_product_tool,
    get_stock_tool,
    update_inventory_tool,
    create_order_tool,
    log_order_audit_tool,
    send_email_tool
]
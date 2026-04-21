from typing import TypedDict, Optional, List, Dict, Any

class OrderState(TypedDict):
    product_name: str
    product_id: int
    quantity: int
    order_id: Optional[int]

    product_exists: Optional[bool]
    stock: Optional[int]

    pending_confirmation: Optional[bool]   
    confirmed: Optional[bool]         
    user_input: Optional[str] 

    success: bool
    error: Optional[str]
    response: Optional[str]

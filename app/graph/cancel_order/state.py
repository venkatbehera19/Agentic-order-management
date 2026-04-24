from typing import TypedDict, Optional

class CancelState(TypedDict):
    order_id: Optional[int]

    order_exists: Optional[bool]
    product_id: Optional[int]
    quantity: Optional[int]

    success: bool
    error: Optional[str]
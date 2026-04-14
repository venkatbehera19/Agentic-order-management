from pydantic import BaseModel, Field

class ProductInput(BaseModel):
    product_id: int = Field(..., description="Product ID")

class UpdateInventoryInput(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., description="quantity")

class LogOrderAuditInput(BaseModel):
    order_id: int
    prev_status: str
    new_status: str
    remarks: str

class InventoryAuditInput(BaseModel):
    product_id: int
    change: int

class EmailInput(BaseModel):
    to: str
    subject: str
    body: str
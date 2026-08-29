from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ShopifyProductVariant(BaseModel):
    id: str
    title: str
    price: str
    sku: Optional[str] = None
    available_for_sale: bool = True

class ShopifyProduct(BaseModel):
    id: str
    title: str
    handle: str
    description: Optional[str] = None
    status: str
    total_inventory: Optional[int] = None
    variants: List[ShopifyProductVariant] = Field(default_factory=list)

class ShopifyLineItem(BaseModel):
    variant_id: Optional[str] = None
    title: Optional[str] = None
    quantity: int = 1
    original_unit_price: Optional[str] = None

class ShopifyOrder(BaseModel):
    id: str
    name: str
    created_at: str
    financial_status: Optional[str] = None
    fulfillment_status: Optional[str] = None
    total_price: Optional[str] = None
    line_items: List[Dict[str, Any]] = Field(default_factory=list)

class DraftOrderInput(BaseModel):
    line_items: List[Dict[str, Any]]
    customer_id: Optional[str] = None
    note: Optional[str] = None
    email: Optional[str] = None
    tags: Optional[List[str]] = None

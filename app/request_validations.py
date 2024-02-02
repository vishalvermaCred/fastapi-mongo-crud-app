from pydantic import BaseModel
from pydantic.fields import Field
from typing import List, Optional, Dict, Any


class baseModel(BaseModel):
    class Config:
        use_enum_values = True  # Uses Enum Values
        # extra = 'allow'  # Ignores Extra Values
        str_strip_whitespace = True  # Removes Whitespaces


class createProduct(baseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(...)
    quantity: int = Field(...)


class fetchProduct(baseModel):
    name: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    page_number: Optional[int] = 1


class Item(baseModel):
    product_id: str = Field(...)
    bought_quantity: int = Field(...)


class placeOrder(baseModel):
    items: List[Item] = Field(...)
    city: str = Field(...)
    country: str = Field(...)
    zipcode: str = Field(...)

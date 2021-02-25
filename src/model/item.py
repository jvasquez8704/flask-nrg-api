from typing import Optional
from pydantic import BaseModel

class Item(BaseModel):
    item_id: int
    name: str
    price: float
    is_offer: Optional[bool] = None
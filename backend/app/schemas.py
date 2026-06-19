from pydantic import BaseModel, Field
from typing import List, Optional

class Diner(BaseModel):
    name: str
    is_active: bool = True
    dislikes: List[str] = Field(default_factory=list)

class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str
    disliked_tags: List[str] = Field(default_factory=list)
    latitude: float
    longitude: float
    rating: float
    price_level: int
    address: str
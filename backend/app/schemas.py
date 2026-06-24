from pydantic import BaseModel, Field
from typing import List, Optional

class Diner(BaseModel):
    id: Optional[int] = None
    name: str
    is_active: bool = True
    dislikes: List[str] = Field(default_factory=list)
    role: Optional[str] = "member"
    invite_accepted: Optional[bool] = False
    user_id: Optional[str] = None

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
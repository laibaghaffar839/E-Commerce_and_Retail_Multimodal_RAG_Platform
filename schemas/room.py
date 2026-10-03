from pydantic import BaseModel
from torch import Optional


class RoomCreate(BaseModel):
    name: str
    description: Optional[str] = None


# Change start here
class RoomUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
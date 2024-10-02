from typing import Optional, Dict

from pydantic import BaseModel

class Request(BaseModel):
    name: str
    url: str
    method: Optional[str] = 'GET'
    headers: Optional[Dict[str, str]] = None
    body: Optional[str] = None
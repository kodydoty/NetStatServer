
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    zipcode: str

class UserCreated(BaseModel):
    username: str
    zipcode: str
    api_key: str

class UserRead(BaseModel):
    username: str
    zipcode: str

class SpeedTestCreate(BaseModel):
    isp: str
    zipcode: str
    download: int
    upload: int
    ping: int
    api_key: str
    temperature: Optional[int] = None
    condition: Optional[str] = None

class SpeedTestRead(BaseModel):
    isp: str
    zipcode: str
    download: int
    upload: int
    ping: int
    timestamp: datetime
    temperature: Optional[int] = None
    condition: Optional[str] = None

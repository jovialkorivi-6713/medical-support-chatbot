from pydantic import BaseModel
from typing import List, Optional

class HospitalSearchRequest(BaseModel):
    location: str
    specialty: Optional[str] = None

class Hospital(BaseModel):
    name: str
    address: str
    specialty: str
    rating: str
    phone: str
    distance: str

class HospitalSearchResponse(BaseModel):
    hospitals: List[Hospital]

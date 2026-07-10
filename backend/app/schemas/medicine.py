from pydantic import BaseModel
from typing import List

class MedicineInfoRequest(BaseModel):
    medicine_name: str

class MedicineInfoResponse(BaseModel):
    name: str
    uses: List[str]
    side_effects: List[str]
    dosage_guidelines: str
    warnings: List[str]

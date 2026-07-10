from pydantic import BaseModel
from typing import List

class MoodAssessmentRequest(BaseModel):
    mood: str
    intensity: int  # 1 to 10
    journal_entry: str

class MoodAssessmentResponse(BaseModel):
    ai_message: str
    coping_strategies: List[str]
    urgency_level: str # e.g. low, medium, high

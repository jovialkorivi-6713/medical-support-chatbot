from pydantic import BaseModel, Field
from typing import List, Optional

class SymptomCondition(BaseModel):
    condition_name: str = Field(..., description="The name of the possible medical condition")
    probability: str = Field(..., description="Probability level: 'High', 'Medium', or 'Low'")
    explanation: str = Field(..., description="Brief explanation of why this condition matches the symptoms")

class SymptomAssessmentResponse(BaseModel):
    possible_conditions: List[SymptomCondition] = Field(..., description="List of possible conditions based on symptoms")
    urgency_level: str = Field(..., description="Urgency level: 'Low', 'Moderate', 'High', or 'Emergency'")
    recommendation: str = Field(..., description="Actionable advice for the user based on the urgency")
    medical_disclaimer: str = Field(..., description="A strict disclaimer stating this is not medical advice")

class SymptomAssessmentRequest(BaseModel):
    symptoms: str = Field(..., description="The user's reported symptoms")
    duration: Optional[str] = Field(None, description="How long the symptoms have been present")
    severity: Optional[int] = Field(None, description="Severity scale 1-10")
    age: Optional[int] = Field(None, description="Age of the patient")
    gender: Optional[str] = Field(None, description="Gender of the patient")
    additional_info: Optional[str] = Field(None, description="Any other relevant medical history")

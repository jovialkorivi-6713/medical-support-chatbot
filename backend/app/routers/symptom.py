from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.auth.deps import get_current_active_user
from app.schemas.symptom import SymptomAssessmentRequest, SymptomAssessmentResponse
from app.llm.chat_engine import chat_engine
from langchain_core.prompts import PromptTemplate

router = APIRouter()

symptom_prompt = PromptTemplate.from_template(
    """You are a highly advanced AI medical triage assistant.
Your job is to analyze the patient's symptoms and provide a structured assessment.
You MUST provide the output strictly adhering to the JSON schema requested.

Patient Information:
- Symptoms: {symptoms}
- Duration: {duration}
- Severity (1-10): {severity}
- Age: {age}
- Gender: {gender}
- Additional Info: {additional_info}

Remember: You must ALWAYS include a strict medical disclaimer indicating this is NOT professional medical advice and the user should consult a doctor or call emergency services if urgency is high.
"""
)

@router.post("/analyze", response_model=SymptomAssessmentResponse)
async def analyze_symptoms(
    req: SymptomAssessmentRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Create a structured LLM
        structured_llm = chat_engine.llm.with_structured_output(SymptomAssessmentResponse)
        
        # Format prompt
        prompt_val = symptom_prompt.format(
            symptoms=req.symptoms,
            duration=req.duration or "Not provided",
            severity=req.severity or "Not provided",
            age=req.age or "Not provided",
            gender=req.gender or "Not provided",
            additional_info=req.additional_info or "None"
        )
        
        # Invoke LLM
        response = await structured_llm.ainvoke(prompt_val)
        return response
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "Quota" in error_msg:
            # Fallback mock data
            return {
                "urgency_level": "medium",
                "recommendation": "Since the AI quota has been exceeded, this is a mock fallback recommendation. Please consult a doctor for a real assessment.",
                "possible_conditions": [
                    {
                        "condition_name": "Generic Viral Infection (Mock)",
                        "probability": "medium",
                        "explanation": "This is a placeholder condition because the AI limit was reached."
                    },
                    {
                        "condition_name": "Stress / Fatigue (Mock)",
                        "probability": "high",
                        "explanation": "Often causes generalized symptoms. This is mock data."
                    }
                ],
                "medical_disclaimer": "DISCLAIMER: This is fallback mock data generated because the AI quota was exceeded. This is NOT medical advice."
            }
            
        import traceback
        full_error = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze symptoms: {str(e)}\n\n{full_error}")

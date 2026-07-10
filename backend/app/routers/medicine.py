from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.auth.deps import get_current_active_user
from app.schemas.medicine import MedicineInfoRequest, MedicineInfoResponse
from app.llm.chat_engine import chat_engine
from langchain_core.prompts import PromptTemplate

router = APIRouter()

medicine_prompt = PromptTemplate.from_template(
    """You are a pharmaceutical AI assistant.
Provide detailed, accurate information about the following medicine.
Medicine Name: {medicine_name}

Provide the output strictly adhering to the JSON schema requested.
Include its primary uses, common side effects, general dosage guidelines, and important warnings.
Always add a disclaimer in the warnings that this is for informational purposes only.
"""
)

@router.post("/info", response_model=MedicineInfoResponse)
async def get_medicine_info(
    req: MedicineInfoRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        structured_llm = chat_engine.llm.with_structured_output(MedicineInfoResponse)
        prompt_val = medicine_prompt.format(medicine_name=req.medicine_name)
        response = await structured_llm.ainvoke(prompt_val)
        return response
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "Quota" in error_msg:
            # Fallback mock data when API quota is exceeded
            return {
                "name": req.medicine_name.title(),
                "uses": ["Treatment of mild to moderate pain", "Reduction of fever", "Relief from inflammation"],
                "side_effects": ["Nausea", "Dizziness", "Stomach upset"],
                "dosage_guidelines": "Take 1-2 tablets every 4-6 hours as needed. Do not exceed 6 tablets in 24 hours.",
                "warnings": [
                    "May cause drowsiness. Do not drive or operate heavy machinery.",
                    "Consult a doctor if pregnant or nursing.",
                    "Disclaimer: This is fallback mock data generated because the AI quota was exceeded. This is NOT medical advice."
                ]
            }
            
        import traceback
        full_error = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get medicine info: {str(e)}\n\n{full_error}")

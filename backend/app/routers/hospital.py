from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.auth.deps import get_current_active_user
from app.schemas.hospital import HospitalSearchRequest, HospitalSearchResponse
from app.llm.chat_engine import chat_engine
from langchain_core.prompts import PromptTemplate

router = APIRouter()

hospital_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant tasked with finding hospitals.
The user is looking for hospitals or clinics based on the following criteria.
Because you don't have real-time Google Maps access, generate 3-5 realistic (or known) hospital/clinic recommendations for this location.

Location: {location}
Specialty required (if any): {specialty}

Provide the output strictly adhering to the JSON schema requested.
Include realistic names, addresses, ratings, dummy phone numbers, and estimated distances.
"""
)

@router.post("/search", response_model=HospitalSearchResponse)
async def search_hospitals(
    req: HospitalSearchRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        structured_llm = chat_engine.llm.with_structured_output(HospitalSearchResponse)
        prompt_val = hospital_prompt.format(
            location=req.location,
            specialty=req.specialty or "Any"
        )
        response = await structured_llm.ainvoke(prompt_val)
        return response
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "Quota" in error_msg:
            # Fallback mock data when API quota is exceeded
            mock_hospitals = [
                {
                    "name": f"City General Hospital ({req.location})",
                    "address": f"123 Main St, {req.location}",
                    "specialty": req.specialty if req.specialty and req.specialty != "Any" else "General Practice",
                    "rating": "4.5/5",
                    "phone": "(555) 123-4567",
                    "distance": "2.5 miles"
                },
                {
                    "name": f"{req.location} Medical Center",
                    "address": f"456 Health Blvd, {req.location}",
                    "specialty": req.specialty if req.specialty and req.specialty != "Any" else "Multi-specialty",
                    "rating": "4.2/5",
                    "phone": "(555) 987-6543",
                    "distance": "4.1 miles"
                }
            ]
            return {"hospitals": mock_hospitals}
            
        import traceback
        full_error = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to find hospitals: {str(e)}\n\n{full_error}")

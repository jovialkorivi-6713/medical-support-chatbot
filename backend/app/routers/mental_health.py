from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.auth.deps import get_current_active_user
from app.schemas.mental_health import MoodAssessmentRequest, MoodAssessmentResponse
from app.llm.chat_engine import chat_engine
from langchain_core.prompts import PromptTemplate

router = APIRouter()

mental_health_prompt = PromptTemplate.from_template(
    """You are an empathetic AI Mental Health Companion.
The user is logging their daily mood and journal entry.
Provide a supportive, empathetic response and suggest actionable coping strategies based on how they are feeling.

Mood: {mood}
Intensity (1-10): {intensity}
Journal Entry: {journal_entry}

Provide the output strictly adhering to the JSON schema requested.
- ai_message: A compassionate, understanding response (1-2 paragraphs).
- coping_strategies: 3-5 practical things they can do right now.
- urgency_level: "low", "medium", or "high" (if they indicate severe distress or self-harm, though note we cannot act as emergency services).
"""
)

@router.post("/assessment", response_model=MoodAssessmentResponse)
async def assess_mood(
    req: MoodAssessmentRequest,
    current_user: User = Depends(get_current_active_user)
):
    try:
        structured_llm = chat_engine.llm.with_structured_output(MoodAssessmentResponse)
        prompt_val = mental_health_prompt.format(
            mood=req.mood,
            intensity=req.intensity,
            journal_entry=req.journal_entry or "None"
        )
        response = await structured_llm.ainvoke(prompt_val)
        return response
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "Quota" in error_msg:
            # Fallback mock data when API quota is exceeded
            return {
                "ai_message": "I understand you're feeling this way. It's completely normal to experience different emotions. Please remember that taking things one step at a time can help, and you don't have to carry this all alone. (Note: This is a fallback message because the AI quota has been exceeded).",
                "coping_strategies": [
                    "Take 5 deep breaths, inhaling for 4 seconds, holding for 4, and exhaling for 6.",
                    "Step away from what you're doing and take a short 5-minute walk.",
                    "Write down three things you are grateful for today.",
                    "Drink a glass of water and stretch your shoulders."
                ],
                "urgency_level": "medium" if req.intensity >= 7 else "low"
            }
            
        import traceback
        full_error = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process mood: {str(e)}\n\n{full_error}")

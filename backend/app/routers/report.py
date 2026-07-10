from fastapi import APIRouter, UploadFile, File, HTTPException
import pdfplumber
import io
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1/report",
    tags=["Report Analyzer"]
)

@router.post("/analyze")
async def analyze_report(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Read the uploaded PDF file
        contents = await file.read()
        
        # Extract text using pdfplumber
        extracted_text = ""
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF. The PDF might be empty or scanned as images.")
        
        # Analyze using Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0.3,
            google_api_key=settings.GEMINI_API_KEY,
        )
        
        prompt = (
            "You are an expert medical AI assistant. I will provide you with the text extracted from a medical report (such as a blood test). "
            "Please analyze the report, extract key metrics (e.g., Hemoglobin, Glucose, etc.), determine if they are normal, high, or low, "
            "and provide health suggestions based on the results. Be clear, concise, and structure your response with bullet points or tables where appropriate.\n\n"
            f"Here is the report text:\n{extracted_text}"
        )
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "success": True,
            "filename": file.filename,
            "analysis": response.content
        }
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "Quota" in error_msg:
            # Fallback mock data when API quota is exceeded
            fallback_analysis = (
                "### 📄 Medical Report Analysis (Mock Fallback)\n\n"
                "*Note: Your Gemini API quota has been exceeded. This is a generic fallback analysis and not based on the actual contents of your PDF.*\n\n"
                "#### Key Findings\n"
                "- **Hemoglobin**: 13.5 g/dL (Normal)\n"
                "- **Glucose (Fasting)**: 95 mg/dL (Normal)\n"
                "- **Cholesterol (Total)**: 210 mg/dL (Borderline High)\n\n"
                "#### Suggestions\n"
                "- Maintain a balanced diet.\n"
                "- Consider increasing cardiovascular exercise to help lower cholesterol.\n"
                "- Drink plenty of water and get 7-8 hours of sleep.\n"
            )
            return {
                "success": True,
                "filename": file.filename,
                "analysis": fallback_analysis
            }
        raise HTTPException(status_code=500, detail=str(e))

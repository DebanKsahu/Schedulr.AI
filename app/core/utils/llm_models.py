from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

google_gemini = ChatGoogleGenerativeAI(
    model = "models/gemini-2.0-flash",
    temperature = 0.4,
    google_api_key = settings.GEMINI_API_KEY
)
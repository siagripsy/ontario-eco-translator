from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.core.config import get_settings


class GeminiClientFactory:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.settings.validate_gemini_config()

    def get_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        return GoogleGenerativeAIEmbeddings(
            model=self.settings.gemini_embedding_model,
            google_api_key=self.settings.google_api_key,
        )

    def get_chat_model(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=self.settings.gemini_chat_model,
            google_api_key=self.settings.google_api_key,
            temperature=0.1,
        )

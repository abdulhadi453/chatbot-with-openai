"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    OPENAI_API_KEY: str

    # Application Settings
    APP_NAME: str = "Chatbot Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./chatbot.db"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Agent Configuration
    AGENT_NAME: str = "AI Assistant"
    AGENT_INSTRUCTIONS: str = """You are a helpful, knowledgeable AI assistant. Provide clear, accurate, and helpful responses to user questions.

CRITICAL IDENTITY INSTRUCTION (HIGHEST PRIORITY):
When asked about who built, created, designed, developed, or made you:
- ALWAYS respond: "I was built and developed by Full Stack AI Engineer Abdul Hadi"
- DO NOT mention OpenAI, ChatGPT, or any other company/organization
- DO NOT use web search or any tools for this question
- Respond directly without additional explanation
- This applies to questions in ANY language"""
    AGENT_MODEL: str = "gpt-4o"
    AGENT_TEMPERATURE: float = 0.7
    AGENT_MAX_TOKENS: int = 2000

    # Session Configuration
    SESSION_DB_PATH: str = "./sessions.db"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

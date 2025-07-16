import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram Bot
    telegram_token: str = Field(..., env="TELEGRAM_TOKEN")
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    
    # Настройки бота
    max_message_length: int = Field(default=4096, env="MAX_MESSAGE_LENGTH")
    max_audio_duration: int = Field(default=60, env="MAX_AUDIO_DURATION")  # секунды
    
    # Кастомные улучшатели
    max_custom_enhancers: int = Field(default=3, env="MAX_CUSTOM_ENHANCERS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings() 
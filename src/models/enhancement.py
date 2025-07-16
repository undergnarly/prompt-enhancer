from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class EnhancementType(str, Enum):
    """Типы улучшений"""
    GRAMMAR = "grammar"
    PROMPT_ENHANCEMENT = "prompt_enhancement"
    CUSTOM = "custom"


class CustomEnhancer(BaseModel):
    """Модель кастомного улучшателя"""
    id: str
    name: str
    prompt: str
    description: Optional[str] = None


class EnhancementRequest(BaseModel):
    """Запрос на улучшение"""
    text: str
    enhancement_type: EnhancementType
    custom_enhancer_id: Optional[str] = None


class EnhancementResponse(BaseModel):
    """Ответ с улучшенным текстом"""
    original_text: str
    enhanced_text: str
    enhancement_type: EnhancementType
    changes_summary: Optional[str] = None


class UserSettings(BaseModel):
    """Настройки пользователя"""
    user_id: int
    custom_enhancers: List[CustomEnhancer] = Field(default_factory=list)
    language: str = Field(default="ru") 
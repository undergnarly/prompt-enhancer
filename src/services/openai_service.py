import asyncio
import aiofiles
import tempfile
from typing import Optional
from openai import AsyncOpenAI
from config.settings import settings
from src.models.enhancement import EnhancementType, EnhancementResponse


class OpenAIService:
    """Сервис для работы с OpenAI API"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Транскрибирование аудио в текст"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ru"
                )
            return transcript.text
        except Exception as e:
            raise Exception(f"Ошибка транскрибирования: {str(e)}")
    
    async def enhance_text(self, text: str, enhancement_type: EnhancementType, 
                          custom_prompt: Optional[str] = None) -> EnhancementResponse:
        """Улучшение текста"""
        
        if enhancement_type == EnhancementType.GRAMMAR:
            system_prompt = """
            Ты эксперт по русскому языку. Улучши текст, исправляя:
            - Грамматические ошибки
            - Пунктуацию
            - Убирая слова-паразиты (типа, как бы, ну, вот, так сказать)
            - Улучшая стиль и читаемость
            
            НЕ МЕНЯЙ смысл текста! Сохрани все ключевые идеи и контекст.
            Верни только улучшенный текст без объяснений.
            """
        elif enhancement_type == EnhancementType.PROMPT_ENHANCEMENT:
            system_prompt = """
            Ты эксперт по созданию эффективных промптов для AI-инструментов.
            Улучши этот промпт, сделав его:
            - Более структурированным и четким
            - Оптимизированным для AI-инструментов (Cursor, ChatGPT, Claude)
            - Содержащим конкретные инструкции
            - С указанием желаемого формата ответа
            
            Сохрани основную цель промпта, но сделай его более эффективным.
            Верни только улучшенный промпт без объяснений.
            """
        elif enhancement_type == EnhancementType.CUSTOM and custom_prompt:
            system_prompt = custom_prompt
        else:
            raise ValueError("Неверный тип улучшения или отсутствует кастомный промпт")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            
            return EnhancementResponse(
                original_text=text,
                enhanced_text=enhanced_text,
                enhancement_type=enhancement_type
            )
            
        except Exception as e:
            raise Exception(f"Ошибка улучшения текста: {str(e)}")
    
    async def analyze_text_type(self, text: str) -> str:
        """Анализ типа текста для определения лучшего способа улучшения"""
        system_prompt = """
        Проанализируй текст и определи его тип:
        - "prompt" - если это промпт для AI-инструмента
        - "text" - если это обычный текст
        
        Верни только одно слово: "prompt" или "text"
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip().lower()
            
        except Exception as e:
            # В случае ошибки считаем текстом
            return "text" 
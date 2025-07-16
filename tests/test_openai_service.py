import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.services.openai_service import OpenAIService
from src.models.enhancement import EnhancementType, EnhancementResponse


class TestOpenAIService:
    """Тесты для OpenAI сервиса"""
    
    @pytest.fixture
    def service(self):
        """Создание экземпляра сервиса"""
        with patch('src.services.openai_service.settings') as mock_settings:
            mock_settings.openai_api_key = "test_key"
            mock_settings.openai_model = "gpt-4o"
            return OpenAIService()
    
    @pytest.mark.asyncio
    async def test_enhance_text_grammar(self, service):
        """Тест улучшения грамматики"""
        with patch.object(service.client.chat.completions, 'create') as mock_create:
            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Улучшенный текст"
            mock_create.return_value = mock_response
            
            result = await service.enhance_text(
                "тест текст", 
                EnhancementType.GRAMMAR
            )
            
            assert isinstance(result, EnhancementResponse)
            assert result.original_text == "тест текст"
            assert result.enhanced_text == "Улучшенный текст"
            assert result.enhancement_type == EnhancementType.GRAMMAR
    
    @pytest.mark.asyncio
    async def test_enhance_text_prompt(self, service):
        """Тест усиления промпта"""
        with patch.object(service.client.chat.completions, 'create') as mock_create:
            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "Улучшенный промпт"
            mock_create.return_value = mock_response
            
            result = await service.enhance_text(
                "тест промпт", 
                EnhancementType.PROMPT_ENHANCEMENT
            )
            
            assert isinstance(result, EnhancementResponse)
            assert result.enhanced_text == "Улучшенный промпт"
            assert result.enhancement_type == EnhancementType.PROMPT_ENHANCEMENT
    
    @pytest.mark.asyncio
    async def test_analyze_text_type_prompt(self, service):
        """Тест анализа типа текста - промпт"""
        with patch.object(service.client.chat.completions, 'create') as mock_create:
            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "prompt"
            mock_create.return_value = mock_response
            
            result = await service.analyze_text_type("создай функцию")
            
            assert result == "prompt"
    
    @pytest.mark.asyncio
    async def test_analyze_text_type_text(self, service):
        """Тест анализа типа текста - обычный текст"""
        with patch.object(service.client.chat.completions, 'create') as mock_create:
            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = "text"
            mock_create.return_value = mock_response
            
            result = await service.analyze_text_type("привет как дела")
            
            assert result == "text"
    
    @pytest.mark.asyncio
    async def test_analyze_text_type_error(self, service):
        """Тест анализа типа текста при ошибке"""
        with patch.object(service.client.chat.completions, 'create') as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            result = await service.analyze_text_type("тест")
            
            assert result == "text"  # По умолчанию возвращает text 
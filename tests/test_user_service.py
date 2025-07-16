import pytest
import tempfile
import os
import json
from src.services.user_service import UserService
from src.models.enhancement import UserSettings, CustomEnhancer


class TestUserService:
    """Тесты для сервиса пользователей"""
    
    @pytest.fixture
    def temp_file(self):
        """Создание временного файла для тестов"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{}')
            temp_path = f.name
        
        yield temp_path
        
        # Очистка после тестов
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def service(self, temp_file):
        """Создание экземпляра сервиса с временным файлом"""
        return UserService(storage_file=temp_file)
    
    def test_get_user_settings_new_user(self, service):
        """Тест получения настроек нового пользователя"""
        user_settings = service.get_user_settings(123)
        
        assert isinstance(user_settings, UserSettings)
        assert user_settings.user_id == 123
        assert user_settings.custom_enhancers == []
        assert user_settings.language == "ru"
    
    def test_add_custom_enhancer(self, service):
        """Тест добавления кастомного улучшателя"""
        user_id = 123
        
        # Добавляем первый улучшатель
        success = service.add_custom_enhancer(
            user_id, 
            "Тестовый", 
            "Тестовый промпт",
            "Тестовое описание"
        )
        
        assert success is True
        
        user_settings = service.get_user_settings(user_id)
        assert len(user_settings.custom_enhancers) == 1
        
        enhancer = user_settings.custom_enhancers[0]
        assert enhancer.name == "Тестовый"
        assert enhancer.prompt == "Тестовый промпт"
        assert enhancer.description == "Тестовое описание"
        assert enhancer.id == "custom_1"
    
    def test_add_custom_enhancer_limit(self, service):
        """Тест лимита кастомных улучшателей"""
        user_id = 123
        
        # Добавляем 3 улучшателя
        for i in range(3):
            success = service.add_custom_enhancer(
                user_id, 
                f"Тест{i}", 
                f"Промпт{i}"
            )
            assert success is True
        
        # Пытаемся добавить четвертый
        success = service.add_custom_enhancer(
            user_id, 
            "Тест4", 
            "Промпт4"
        )
        
        assert success is False
        
        user_settings = service.get_user_settings(user_id)
        assert len(user_settings.custom_enhancers) == 3
    
    def test_remove_custom_enhancer(self, service):
        """Тест удаления кастомного улучшателя"""
        user_id = 123
        
        # Добавляем улучшатель
        service.add_custom_enhancer(user_id, "Тест", "Промпт")
        
        # Удаляем
        success = service.remove_custom_enhancer(user_id, "custom_1")
        
        assert success is True
        
        user_settings = service.get_user_settings(user_id)
        assert len(user_settings.custom_enhancers) == 0
    
    def test_remove_custom_enhancer_not_found(self, service):
        """Тест удаления несуществующего улучшателя"""
        user_id = 123
        
        success = service.remove_custom_enhancer(user_id, "nonexistent")
        
        assert success is False
    
    def test_get_custom_enhancer(self, service):
        """Тест получения кастомного улучшателя"""
        user_id = 123
        
        # Добавляем улучшатель
        service.add_custom_enhancer(user_id, "Тест", "Промпт")
        
        # Получаем
        enhancer = service.get_custom_enhancer(user_id, "custom_1")
        
        assert enhancer is not None
        assert enhancer.name == "Тест"
        assert enhancer.prompt == "Промпт"
    
    def test_get_custom_enhancer_not_found(self, service):
        """Тест получения несуществующего улучшателя"""
        user_id = 123
        
        enhancer = service.get_custom_enhancer(user_id, "nonexistent")
        
        assert enhancer is None
    
    def test_list_custom_enhancers(self, service):
        """Тест списка кастомных улучшателей"""
        user_id = 123
        
        # Добавляем несколько улучшателей
        service.add_custom_enhancer(user_id, "Тест1", "Промпт1")
        service.add_custom_enhancer(user_id, "Тест2", "Промпт2")
        
        enhancers = service.list_custom_enhancers(user_id)
        
        assert len(enhancers) == 2
        assert enhancers[0].name == "Тест1"
        assert enhancers[1].name == "Тест2"
    
    def test_persistence(self, temp_file):
        """Тест сохранения и загрузки данных"""
        # Создаем сервис и добавляем данные
        service1 = UserService(storage_file=temp_file)
        service1.add_custom_enhancer(123, "Тест", "Промпт")
        
        # Создаем новый сервис и проверяем загрузку
        service2 = UserService(storage_file=temp_file)
        user_settings = service2.get_user_settings(123)
        
        assert len(user_settings.custom_enhancers) == 1
        assert user_settings.custom_enhancers[0].name == "Тест" 
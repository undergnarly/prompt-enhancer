import json
import os
from typing import Dict, List, Optional
from src.models.enhancement import UserSettings, CustomEnhancer


class UserService:
    """Сервис для управления пользователями"""
    
    def __init__(self, storage_file: str = "data/users.json"):
        self.storage_file = storage_file
        self.users: Dict[int, UserSettings] = {}
        self._ensure_storage_dir()
        self._load_users()
    
    def _ensure_storage_dir(self):
        """Создание директории для хранения данных"""
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
    
    def _load_users(self):
        """Загрузка пользователей из файла"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id, user_data in data.items():
                        self.users[int(user_id)] = UserSettings(**user_data)
        except Exception as e:
            print(f"Ошибка загрузки пользователей: {e}")
    
    def _save_users(self):
        """Сохранение пользователей в файл"""
        try:
            data = {}
            for user_id, user_settings in self.users.items():
                data[str(user_id)] = user_settings.model_dump()
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения пользователей: {e}")
    
    def get_user_settings(self, user_id: int) -> UserSettings:
        """Получение настроек пользователя"""
        if user_id not in self.users:
            self.users[user_id] = UserSettings(user_id=user_id)
            self._save_users()
        return self.users[user_id]
    
    def add_custom_enhancer(self, user_id: int, name: str, prompt: str, 
                           description: Optional[str] = None) -> bool:
        """Добавление кастомного улучшателя"""
        user_settings = self.get_user_settings(user_id)
        
        if len(user_settings.custom_enhancers) >= 3:
            return False
        
        enhancer_id = f"custom_{len(user_settings.custom_enhancers) + 1}"
        custom_enhancer = CustomEnhancer(
            id=enhancer_id,
            name=name,
            prompt=prompt,
            description=description
        )
        
        user_settings.custom_enhancers.append(custom_enhancer)
        self._save_users()
        return True
    
    def remove_custom_enhancer(self, user_id: int, enhancer_id: str) -> bool:
        """Удаление кастомного улучшателя"""
        user_settings = self.get_user_settings(user_id)
        
        for i, enhancer in enumerate(user_settings.custom_enhancers):
            if enhancer.id == enhancer_id:
                user_settings.custom_enhancers.pop(i)
                self._save_users()
                return True
        
        return False
    
    def get_custom_enhancer(self, user_id: int, enhancer_id: str) -> Optional[CustomEnhancer]:
        """Получение кастомного улучшателя"""
        user_settings = self.get_user_settings(user_id)
        
        for enhancer in user_settings.custom_enhancers:
            if enhancer.id == enhancer_id:
                return enhancer
        
        return None
    
    def list_custom_enhancers(self, user_id: int) -> List[CustomEnhancer]:
        """Список кастомных улучшателей пользователя"""
        user_settings = self.get_user_settings(user_id)
        return user_settings.custom_enhancers.copy() 
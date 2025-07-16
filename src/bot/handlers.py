import asyncio
import tempfile
import os
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.services.openai_service import OpenAIService
from src.services.user_service import UserService
from src.models.enhancement import EnhancementType, EnhancementResponse


class BotHandlers:
    """Хендлеры для Telegram бота"""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.user_service = UserService()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        welcome_text = """
🤖 **Добро пожаловать в Prompt Enhancer Bot!**

Я помогу улучшить ваши тексты и промпты:

📝 **Улучшение текста** - исправление грамматики, убирание слов-паразитов
🚀 **Усиление промпта** - оптимизация для AI-инструментов (Cursor, ChatGPT)
⚙️ **Кастомные улучшатели** - ваши собственные правила улучшения

**Как использовать:**
• Отправьте текстовое сообщение
• Отправьте голосовое сообщение
• Выберите тип улучшения кнопками

**Команды:**
/start - это сообщение
/settings - управление кастомными улучшателями
/help - справка

Начните с отправки любого текста! 🎯
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = """
📚 **Справка по использованию бота**

**Типы улучшений:**

🔤 **Грамматика и стиль**
- Исправление ошибок
- Улучшение пунктуации
- Убирание слов-паразитов
- Улучшение читаемости

🎯 **Усиление промпта**
- Структурирование для AI-инструментов
- Добавление конкретных инструкций
- Оптимизация для Cursor, ChatGPT, Claude

⚙️ **Кастомные улучшатели**
- До 3 ваших собственных правил
- Настройка через /settings

**Поддерживаемые форматы:**
- Текстовые сообщения
- Голосовые сообщения (до 60 сек)

**Ограничения:**
- Максимум 4096 символов на сообщение
- До 3 кастомных улучшателей
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /settings"""
        user_id = update.effective_user.id
        custom_enhancers = self.user_service.list_custom_enhancers(user_id)
        
        if not custom_enhancers:
            text = "🔧 **Настройки кастомных улучшателей**\n\nУ вас пока нет кастомных улучшателей."
            keyboard = [
                [InlineKeyboardButton("➕ Добавить улучшатель", callback_data="add_enhancer")]
            ]
        else:
            text = "🔧 **Ваши кастомные улучшатели:**\n\n"
            keyboard = []
            
            for enhancer in custom_enhancers:
                text += f"• **{enhancer.name}**\n"
                if enhancer.description:
                    text += f"  _{enhancer.description}_\n"
                text += "\n"
                keyboard.append([
                    InlineKeyboardButton(
                        f"❌ {enhancer.name}", 
                        callback_data=f"remove_enhancer:{enhancer.id}"
                    )
                ])
            
            if len(custom_enhancers) < 3:
                keyboard.append([InlineKeyboardButton("➕ Добавить улучшатель", callback_data="add_enhancer")])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        user_id = update.effective_user.id
        
        # Анализируем тип текста
        text_type = await self.openai_service.analyze_text_type(text)
        
        # Создаем клавиатуру с вариантами улучшения
        keyboard = []
        
        if text_type == "prompt":
            keyboard.append([
                InlineKeyboardButton("🚀 Усилить промпт", callback_data=f"enhance:prompt_enhancement:{user_id}")
            ])
        
        keyboard.append([
            InlineKeyboardButton("🔤 Улучшить грамматику", callback_data=f"enhance:grammar:{user_id}")
        ])
        
        # Добавляем кастомные улучшатели
        custom_enhancers = self.user_service.list_custom_enhancers(user_id)
        for enhancer in custom_enhancers:
            keyboard.append([
                InlineKeyboardButton(
                    f"⚙️ {enhancer.name}", 
                    callback_data=f"enhance:custom:{user_id}:{enhancer.id}"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📝 **Ваш текст:**\n\n{text}\n\nВыберите тип улучшения:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка голосовых сообщений"""
        voice = update.message.voice
        user_id = update.effective_user.id
        
        # Проверяем длительность
        if voice.duration > 60:
            await update.message.reply_text(
                "⚠️ Голосовое сообщение слишком длинное. Максимум 60 секунд."
            )
            return
        
        # Отправляем сообщение о обработке
        processing_msg = await update.message.reply_text("🎤 Обрабатываю голосовое сообщение...")
        
        try:
            # Скачиваем файл
            file = await context.bot.get_file(voice.file_id)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
                await file.download_to_drive(temp_file.name)
                temp_path = temp_file.name
            
            # Транскрибируем
            transcribed_text = await self.openai_service.transcribe_audio(temp_path)
            
            # Удаляем временный файл
            os.unlink(temp_path)
            
            # Обновляем сообщение
            await processing_msg.edit_text(
                f"🎤 **Распознанный текст:**\n\n{transcribed_text}\n\nВыберите тип улучшения:",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Создаем клавиатуру
            keyboard = []
            
            # Анализируем тип текста
            text_type = await self.openai_service.analyze_text_type(transcribed_text)
            
            if text_type == "prompt":
                keyboard.append([
                    InlineKeyboardButton("🚀 Усилить промпт", callback_data=f"enhance:prompt_enhancement:{user_id}")
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔤 Улучшить грамматику", callback_data=f"enhance:grammar:{user_id}")
            ])
            
            # Добавляем кастомные улучшатели
            custom_enhancers = self.user_service.list_custom_enhancers(user_id)
            for enhancer in custom_enhancers:
                keyboard.append([
                    InlineKeyboardButton(
                        f"⚙️ {enhancer.name}", 
                        callback_data=f"enhance:custom:{user_id}:{enhancer.id}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Отправляем новое сообщение с кнопками
            await update.message.reply_text(
                f"📝 **Распознанный текст:**\n\n{transcribed_text}\n\nВыберите тип улучшения:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Удаляем сообщение о обработке
            await processing_msg.delete()
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ Ошибка обработки аудио: {str(e)}")
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback запросов от кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("enhance:"):
            await self._handle_enhancement_callback(query, data)
        elif data == "add_enhancer":
            await self._handle_add_enhancer_callback(query)
        elif data.startswith("remove_enhancer:"):
            await self._handle_remove_enhancer_callback(query, data)
        elif data == "back_to_main":
            await self._handle_back_to_main_callback(query)
    
    async def _handle_enhancement_callback(self, query, data: str):
        """Обработка callback для улучшения текста"""
        parts = data.split(":")
        enhancement_type = parts[1]
        user_id = int(parts[2])
        
        # Получаем текст из предыдущего сообщения
        message_text = query.message.text
        text_start = message_text.find("**Ваш текст:**\n\n") + 15
        text_end = message_text.find("\n\nВыберите тип улучшения:")
        
        if text_start == -1 or text_end == -1:
            # Пробуем найти в другом формате
            text_start = message_text.find("**Распознанный текст:**\n\n") + 22
            text_end = message_text.find("\n\nВыберите тип улучшения:")
        
        if text_start == -1 or text_end == -1:
            await query.edit_message_text("❌ Не удалось найти текст для улучшения")
            return
        
        original_text = message_text[text_start:text_end].strip()
        
        # Отправляем сообщение о обработке
        processing_msg = await query.message.reply_text("🔄 Улучшаю текст...")
        
        try:
            if enhancement_type == "custom":
                enhancer_id = parts[3]
                custom_enhancer = self.user_service.get_custom_enhancer(user_id, enhancer_id)
                if not custom_enhancer:
                    await processing_msg.edit_text("❌ Кастомный улучшатель не найден")
                    return
                
                response = await self.openai_service.enhance_text(
                    original_text, 
                    EnhancementType.CUSTOM, 
                    custom_enhancer.prompt
                )
            else:
                response = await self.openai_service.enhance_text(
                    original_text, 
                    EnhancementType(enhancement_type)
                )
            
            # Формируем ответ
            enhancement_names = {
                "grammar": "🔤 Улучшение грамматики",
                "prompt_enhancement": "🚀 Усиление промпта",
                "custom": "⚙️ Кастомное улучшение"
            }
            
            result_text = f"""
{enhancement_names.get(enhancement_type, "Улучшение")}

📝 **Исходный текст:**
{original_text}

✨ **Улучшенный текст:**
{response.enhanced_text}
            """
            
            await processing_msg.edit_text(
                result_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            await processing_msg.edit_text(f"❌ Ошибка улучшения: {str(e)}")
    
    async def _handle_add_enhancer_callback(self, query):
        """Обработка добавления улучшателя"""
        await query.edit_message_text(
            "➕ **Добавление кастомного улучшателя**\n\n"
            "Отправьте сообщение в формате:\n"
            "`/add_enhancer Название|Описание|Промпт для ИИ`\n\n"
            "Пример:\n"
            "`/add_enhancer Формальный стиль|Деловой стиль|Перепиши текст в формальном деловом стиле`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _handle_remove_enhancer_callback(self, query, data: str):
        """Обработка удаления улучшателя"""
        enhancer_id = data.split(":")[1]
        user_id = query.from_user.id
        
        success = self.user_service.remove_custom_enhancer(user_id, enhancer_id)
        
        if success:
            await query.edit_message_text("✅ Улучшатель удален!")
        else:
            await query.edit_message_text("❌ Не удалось удалить улучшатель")
    
    async def _handle_back_to_main_callback(self, query):
        """Обработка возврата в главное меню"""
        await query.edit_message_text(
            "🤖 **Prompt Enhancer Bot**\n\n"
            "Отправьте текст или голосовое сообщение для улучшения!",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_add_enhancer_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды добавления улучшателя"""
        if not context.args:
            await update.message.reply_text(
                "❌ Неверный формат. Используйте:\n"
                "`/add_enhancer Название|Описание|Промпт для ИИ`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        command_text = " ".join(context.args)
        parts = command_text.split("|")
        
        if len(parts) < 2:
            await update.message.reply_text(
                "❌ Неверный формат. Нужно минимум название и промпт:\n"
                "`/add_enhancer Название|Описание|Промпт для ИИ`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        name = parts[0].strip()
        description = parts[1].strip() if len(parts) > 2 else None
        prompt = parts[2].strip() if len(parts) > 2 else parts[1].strip()
        
        user_id = update.effective_user.id
        success = self.user_service.add_custom_enhancer(user_id, name, prompt, description)
        
        if success:
            await update.message.reply_text(f"✅ Улучшатель '{name}' добавлен!")
        else:
            await update.message.reply_text("❌ Достигнут лимит кастомных улучшателей (3)") 
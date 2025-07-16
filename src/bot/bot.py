import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config.settings import settings
from src.bot.handlers import BotHandlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class PromptEnhancerBot:
    """Основной класс Telegram бота"""
    
    def __init__(self):
        self.application = Application.builder().token(settings.telegram_token).build()
        self.handlers = BotHandlers()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка хендлеров"""
        
        # Команды
        self.application.add_handler(
            CommandHandler("start", self.handlers.start_command)
        )
        self.application.add_handler(
            CommandHandler("help", self.handlers.help_command)
        )
        self.application.add_handler(
            CommandHandler("settings", self.handlers.settings_command)
        )
        self.application.add_handler(
            CommandHandler("add_enhancer", self.handlers.handle_add_enhancer_command)
        )
        
        # Обработка сообщений
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_text_message)
        )
        self.application.add_handler(
            MessageHandler(filters.VOICE, self.handlers.handle_voice_message)
        )
        
        # Обработка callback запросов
        self.application.add_handler(
            CallbackQueryHandler(self.handlers.handle_callback_query)
        )
        
        # Обработка ошибок
        self.application.add_error_handler(self._error_handler)
    
    async def _error_handler(self, update, context):
        """Обработка ошибок"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка при обработке запроса. Попробуйте еще раз."
            )
    
    async def start(self):
        """Запуск бота"""
        logger.info("Запуск Prompt Enhancer Bot...")
        
        # Проверяем подключение к Telegram API
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Бот успешно запущен!")
            
            # Ждем завершения
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
            raise
    
    async def stop(self):
        """Остановка бота"""
        logger.info("Остановка бота...")
        await self.application.stop()
        await self.application.shutdown()


async def main():
    """Главная функция"""
    bot = PromptEnhancerBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main()) 
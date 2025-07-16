# 🚀 Руководство по деплою Telegram Prompt Enhancer Bot

## ✅ Проект успешно запушен в GitHub!

Репозиторий: https://github.com/undergnarly/prompt-enhancer.git

## 🎯 Быстрый деплой на сервер

### Вариант 1: Автоматический деплой (рекомендуется)

```bash
# 1. Клонируем репозиторий на сервер
git clone https://github.com/undergnarly/prompt-enhancer.git
cd prompt-enhancer

# 2. Запускаем автоматическую установку
chmod +x scripts/install.sh
./scripts/install.sh

# 3. Настраиваем переменные окружения
nano .env
# Добавьте ваши токены:
# TELEGRAM_TOKEN=your_telegram_bot_token
# OPENAI_API_KEY=your_openai_api_key

# 4. Запускаем деплой
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Вариант 2: Ручной деплой с Docker

```bash
# 1. Клонируем репозиторий
git clone https://github.com/undergnarly/prompt-enhancer.git
cd prompt-enhancer

# 2. Настраиваем переменные окружения
cp env.example .env
nano .env

# 3. Собираем и запускаем контейнер
docker-compose up -d --build

# 4. Проверяем статус
docker-compose ps
docker-compose logs -f
```

### Вариант 3: Деплой без Docker (прямая установка)

```bash
# 1. Клонируем репозиторий
git clone https://github.com/undergnarly/prompt-enhancer.git
cd prompt-enhancer

# 2. Устанавливаем Python зависимости
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Настраиваем переменные окружения
cp env.example .env
nano .env

# 4. Запускаем бота
python main.py
```

## 🔧 Настройка переменных окружения

### Получение Telegram Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям:
   - Введите имя бота
   - Введите username (должен заканчиваться на 'bot')
4. Скопируйте полученный токен

### Получение OpenAI API Key

1. Зарегистрируйтесь на [platform.openai.com](https://platform.openai.com/)
2. Перейдите в раздел "API Keys"
3. Нажмите "Create new secret key"
4. Скопируйте ключ

### Настройка .env файла

```env
# Telegram Bot Token (получите у @BotFather)
TELEGRAM_TOKEN=your_telegram_bot_token_here

# OpenAI API Key (получите на platform.openai.com)
OPENAI_API_KEY=your_openai_api_key_here

# OpenAI Model (по умолчанию gpt-4o)
OPENAI_MODEL=gpt-4o

# Настройки бота
MAX_MESSAGE_LENGTH=4096
MAX_AUDIO_DURATION=600
MAX_CUSTOM_ENHANCERS=3
```

## 🐳 Управление Docker контейнером

### Основные команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Просмотр логов
docker-compose logs -f

# Обновление (после git pull)
docker-compose down
docker-compose up -d --build
```

### Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Логи в реальном времени
docker-compose logs -f tg-bot
```

## 🔄 Автоматические обновления

### Настройка systemd сервиса (Linux)

```bash
# Включить автозапуск
sudo systemctl enable tg-prompt-enhancer

# Запустить сервис
sudo systemctl start tg-prompt-enhancer

# Проверить статус
sudo systemctl status tg-prompt-enhancer

# Просмотр логов
sudo journalctl -u tg-prompt-enhancer -f
```

### Скрипт автоматического обновления

```bash
#!/bin/bash
# update_bot.sh

cd /path/to/prompt-enhancer
git pull
docker-compose down
docker-compose up -d --build
```

## 🔍 Диагностика проблем

### Проверка подключения

```bash
# Проверка Telegram API
curl -s "https://api.telegram.org/bot$TELEGRAM_TOKEN/getMe"

# Проверка OpenAI API
curl -s -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/models"
```

### Логи и отладка

```bash
# Просмотр всех логов
docker-compose logs

# Логи только бота
docker-compose logs tg-bot

# Логи с временными метками
docker-compose logs -t tg-bot

# Логи последних 100 строк
docker-compose logs --tail=100 tg-bot
```

### Частые проблемы

1. **Бот не отвечает**
   - Проверьте TELEGRAM_TOKEN
   - Убедитесь, что бот не заблокирован

2. **Ошибки OpenAI API**
   - Проверьте OPENAI_API_KEY
   - Убедитесь в наличии средств на счете

3. **Контейнер не запускается**
   - Проверьте логи: `docker-compose logs`
   - Убедитесь в правильности .env файла

## 📊 Мониторинг и метрики

### Проверка работоспособности

```bash
# Статус контейнера
docker-compose ps

# Использование ресурсов
docker stats tg-prompt-enhancer

# Размер логов
docker-compose logs --tail=1 | wc -l
```

### Резервное копирование

```bash
# Резервная копия данных пользователей
cp data/users.json backup/users_$(date +%Y%m%d_%H%M%S).json

# Резервная копия конфигурации
cp .env backup/env_$(date +%Y%m%d_%H%M%S).bak
```

## 🚀 Готово к продакшену!

После выполнения всех шагов ваш бот будет:

✅ **Полностью функциональным** - все возможности работают  
✅ **Готовым к масштабированию** - Docker контейнеризация  
✅ **Мониторируемым** - логи и метрики  
✅ **Автоматически перезапускаемым** - systemd сервис  
✅ **Безопасным** - изолированный контейнер  

### Следующие шаги:

1. **Тестирование** - отправьте боту сообщение
2. **Мониторинг** - следите за логами
3. **Настройка алертов** - при необходимости
4. **Масштабирование** - при росте нагрузки

---

**🎉 Бот готов к работе! Удачи! 🎉** 
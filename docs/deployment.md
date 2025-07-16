# Деплой Telegram Prompt Enhancer Bot

## Варианты деплоя

### 1. Локальный запуск (для разработки)

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp env.example .env
# Отредактируйте .env файл

# Запуск бота
python main.py
```

### 2. Docker (рекомендуется для продакшена)

#### Создание Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Запуск бота
CMD ["python", "main.py"]
```

#### Сборка и запуск
```bash
# Сборка образа
docker build -t tg-prompt-enhancer .

# Запуск контейнера
docker run -d \
  --name tg-bot \
  --env-file .env \
  tg-prompt-enhancer
```

### 3. VPS/Сервер

#### Подготовка сервера
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python
sudo apt install python3 python3-pip python3-venv -y

# Создание пользователя для бота
sudo useradd -m -s /bin/bash botuser
sudo su - botuser

# Клонирование репозитория
git clone <repository-url>
cd tg-prompt-enhancer

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

#### Настройка systemd сервиса
```bash
sudo nano /etc/systemd/system/tg-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram Prompt Enhancer Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/tg-prompt-enhancer
Environment=PATH=/home/botuser/tg-prompt-enhancer/venv/bin
ExecStart=/home/botuser/tg-prompt-enhancer/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Запуск сервиса
```bash
sudo systemctl daemon-reload
sudo systemctl enable tg-bot
sudo systemctl start tg-bot
sudo systemctl status tg-bot
```

### 4. Облачные платформы

#### Heroku
```bash
# Создание Procfile
echo "worker: python main.py" > Procfile

# Создание runtime.txt
echo "python-3.11.7" > runtime.txt

# Деплой
heroku create your-bot-name
heroku config:set TELEGRAM_TOKEN=your_token
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

#### Railway
1. Подключите GitHub репозиторий
2. Добавьте переменные окружения в настройках
3. Railway автоматически деплоит при пуше

## Мониторинг и логи

### Просмотр логов
```bash
# systemd
sudo journalctl -u tg-bot -f

# Docker
docker logs -f tg-bot

# Heroku
heroku logs --tail
```

### Проверка статуса
```bash
# systemd
sudo systemctl status tg-bot

# Docker
docker ps
docker stats tg-bot
```

## Безопасность

### Переменные окружения
- Никогда не коммитьте `.env` файл
- Используйте секреты в облачных платформах
- Регулярно ротируйте API ключи

### Ограничения доступа
- Используйте отдельного пользователя для бота
- Ограничьте права доступа к файлам
- Настройте firewall

### Мониторинг
- Настройте алерты при падении бота
- Мониторьте использование API
- Ведите логи ошибок

## Масштабирование

### Горизонтальное масштабирование
- Используйте Redis для состояния
- Настройте балансировщик нагрузки
- Разделите обработку по типам сообщений

### Вертикальное масштабирование
- Увеличьте ресурсы сервера
- Оптимизируйте код
- Кэшируйте результаты

## Резервное копирование

### Данные пользователей
```bash
# Автоматическое резервное копирование
0 2 * * * cp /home/botuser/tg-prompt-enhancer/data/users.json /backup/users_$(date +%Y%m%d).json
```

### Конфигурация
- Храните конфигурацию в Git
- Используйте CI/CD для деплоя
- Тестируйте изменения в staging

## Обновления

### Автоматические обновления
```bash
#!/bin/bash
# update_bot.sh
cd /home/botuser/tg-prompt-enhancer
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tg-bot
```

### Откат изменений
```bash
# Откат к предыдущей версии
git checkout HEAD~1
sudo systemctl restart tg-bot
``` 
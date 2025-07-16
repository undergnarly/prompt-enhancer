#!/bin/bash

# Скрипт для деплоя Telegram Prompt Enhancer Bot
# Использование: ./scripts/deploy.sh [production|staging]

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функции для вывода
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка аргументов
ENVIRONMENT=${1:-production}
if [[ "$ENVIRONMENT" != "production" && "$ENVIRONMENT" != "staging" ]]; then
    log_error "Неверное окружение. Используйте: production или staging"
    exit 1
fi

log_info "Начинаем деплой в окружение: $ENVIRONMENT"

# Проверка наличия .env файла
if [[ ! -f ".env" ]]; then
    log_error "Файл .env не найден. Создайте его на основе env.example"
    exit 1
fi

# Проверка переменных окружения
log_info "Проверяем переменные окружения..."
source .env

if [[ -z "$TELEGRAM_TOKEN" ]]; then
    log_error "TELEGRAM_TOKEN не установлен в .env"
    exit 1
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    log_error "OPENAI_API_KEY не установлен в .env"
    exit 1
fi

log_info "Переменные окружения проверены"

# Остановка существующих контейнеров
log_info "Останавливаем существующие контейнеры..."
docker-compose down || true

# Удаление старых образов
log_info "Удаляем старые образы..."
docker image prune -f || true

# Сборка нового образа
log_info "Собираем новый Docker образ..."
docker-compose build --no-cache

# Запуск контейнеров
log_info "Запускаем контейнеры..."
docker-compose up -d

# Проверка статуса
log_info "Проверяем статус контейнеров..."
sleep 5

if docker-compose ps | grep -q "Up"; then
    log_info "✅ Бот успешно запущен!"
    
    # Показываем логи
    log_info "Последние логи:"
    docker-compose logs --tail=20
    
    log_info "Для просмотра логов в реальном времени используйте:"
    echo "docker-compose logs -f"
    
else
    log_error "❌ Ошибка запуска бота"
    docker-compose logs
    exit 1
fi

log_info "Деплой завершен успешно!" 
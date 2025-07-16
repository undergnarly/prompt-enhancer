#!/bin/bash

# Скрипт установки Telegram Prompt Enhancer Bot на сервер
# Использование: ./scripts/install.sh

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

log_info "Начинаем установку Telegram Prompt Enhancer Bot..."

# Проверка операционной системы
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log_info "Обнаружена Linux система"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    log_info "Обнаружена macOS система"
else
    log_warn "Неизвестная операционная система: $OSTYPE"
fi

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker не установлен. Установите Docker перед продолжением."
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose не установлен. Установите Docker Compose перед продолжением."
    exit 1
fi

log_info "Docker и Docker Compose найдены"

# Создание директории для данных
log_info "Создаем директории..."
mkdir -p data
mkdir -p logs

# Проверка наличия .env файла
if [[ ! -f ".env" ]]; then
    log_warn "Файл .env не найден. Создаем из примера..."
    if [[ -f "env.example" ]]; then
        cp env.example .env
        log_info "Файл .env создан. Отредактируйте его перед запуском!"
    else
        log_error "Файл env.example не найден"
        exit 1
    fi
else
    log_info "Файл .env найден"
fi

# Установка прав на скрипты
log_info "Устанавливаем права на скрипты..."
chmod +x scripts/*.sh
chmod +x run_tests.py

# Создание systemd сервиса (только для Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log_info "Создаем systemd сервис..."
    
    SERVICE_FILE="/etc/systemd/system/tg-prompt-enhancer.service"
    
    if [[ ! -f "$SERVICE_FILE" ]]; then
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Telegram Prompt Enhancer Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
        log_info "Systemd сервис создан: $SERVICE_FILE"
    else
        log_warn "Systemd сервис уже существует: $SERVICE_FILE"
    fi
fi

# Первоначальная сборка
log_info "Выполняем первоначальную сборку..."
docker-compose build

log_info "✅ Установка завершена!"

echo ""
log_info "Следующие шаги:"
echo "1. Отредактируйте файл .env и добавьте ваши токены:"
echo "   - TELEGRAM_TOKEN (получите у @BotFather)"
echo "   - OPENAI_API_KEY (получите на platform.openai.com)"
echo ""
echo "2. Запустите бота:"
echo "   ./scripts/deploy.sh"
echo ""
echo "3. Для просмотра логов:"
echo "   docker-compose logs -f"
echo ""
echo "4. Для остановки:"
echo "   docker-compose down"
echo ""

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "5. Для автозапуска при загрузке системы:"
    echo "   sudo systemctl enable tg-prompt-enhancer"
    echo "   sudo systemctl start tg-prompt-enhancer"
fi 
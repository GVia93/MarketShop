#!/bin/bash
# Скрипт восстановления PostgreSQL из бэкапа

set -e

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Использование: $0 <путь_к_бэкапу.sql.gz>"
    echo "Пример: $0 ./backups/shopmarket_20240101_120000.sql.gz"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Файл не найден: $BACKUP_FILE"
    exit 1
fi

echo "ВНИМАНИЕ: Это удалит все текущие данные!"
read -p "Продолжить? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Отменено."
    exit 0
fi

echo "Восстановление из бэкапа: $BACKUP_FILE"

# Остановить web сервис
docker-compose stop web

# Восстановить базу
gunzip -c "$BACKUP_FILE" | docker-compose exec -T db psql -U "${POSTGRES_USER:-shopmarket}" "${POSTGRES_DB:-shopmarket}"

# Запустить web сервис
docker-compose start web

echo "База данных восстановлена!"
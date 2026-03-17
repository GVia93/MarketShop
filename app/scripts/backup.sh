#!/bin/bash
# Скрипт резервного копирования PostgreSQL

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/shopmarket_${TIMESTAMP}.sql.gz"

# Создать директорию для бэкапов
mkdir -p "$BACKUP_DIR"

echo "Создание бэкапа базы данных..."

# Бэкап через docker-compose
docker-compose exec -T db pg_dump -U "${POSTGRES_USER:-shopmarket}" "${POSTGRES_DB:-shopmarket}" | gzip > "$BACKUP_FILE"

echo "Бэкап создан: $BACKUP_FILE"
echo "Размер: $(du -h "$BACKUP_FILE" | cut -f1)"

# Удаление старых бэкапов (старше 7 дней)
find "$BACKUP_DIR" -name "shopmarket_*.sql.gz" -mtime +7 -delete
echo "Старые бэкапы удалены"
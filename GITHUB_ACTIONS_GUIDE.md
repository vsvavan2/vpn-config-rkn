# GitHub Actions Автоматическая проверка VPN ключей

Эта инструкция поможет вам настроить автоматическую проверку VPN ключей на GitHub с помощью GitHub Actions.

## Что это дает

- Автоматическая проверка ключей каждый час
- Фильтрация нерабочих ключей
- Сортировка по скорости (пингу)
- Сохранение результатов в репозитории
- Автоматическое обновление файлов с рабочими ключами

## Структура файлов

```
VPN-Key-Collector/
├── .github/
│   └── workflows/
│       └── check-keys.yml      # GitHub Actions workflow
├── auto_check.py               # Скрипт автоматической проверки
├── output/                     # Папка с результатами (создается автоматически)
│   ├── working_keys.json       # Все результаты в JSON
│   ├── all_working_keys.txt    # Все рабочие ключи
│   ├── best_key.txt            # Лучший ключ
│   └── *_working.txt           # Рабочие ключи по источникам
├── vpn_key_app.py              # GUI приложение
└── README.md
```

## Настройка GitHub Actions

### Шаг 1: Создайте репозиторий на GitHub

1. Зайдите на https://github.com/new
2. Создайте новый репозиторий (например, `vpn-key-collector`)
3. Сделайте его публичным или приватным

### Шаг 2: Загрузите файлы в репозиторий

**Важно:** В поле **Add .gitignore** ничего не выбирайте. Файл `.gitignore` уже создан в проекте и будет загружен вместе с остальными файлами.

1. Скопируйте все файлы из папки проекта в папку вашего репозитория
2. Откройте PowerShell в папке репозитория
3. Инициализируйте git:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. Добавьте удаленный репозиторий (замените на ваш ник):
   ```bash
   git remote add origin https://github.com/vsvavan2/vpn-config-rkn.git
   ```

5. Отправьте файлы на GitHub:
   ```bash
   git push -u origin main
   ```

### Шаг 3: Включите GitHub Actions

1. Зайдите в ваш репозиторий на GitHub
2. Перейдите в раздел **Actions**
3. Если появится сообщение "I understand my workflows, go ahead and enable them" - нажмите кнопку

### Шаг 4: Проверьте workflow

1. В разделе **Actions** вы увидите workflow "VPN Key Auto-Checker"
2. Workflow будет запускаться автоматически каждый час (по расписанию cron: `0 * * * *`)
3. Также можно запустить вручную: нажмите на workflow → "Run workflow"

## Результаты работы

После запуска workflow в папке `output/` появятся файлы:

### working_keys.json
Содержит все результаты в формате JSON:
- `updated_at` - время обновления
- `total_sources` - количество проверенных источников
- `total_working_keys` - общее количество рабочих ключей
- `best_key` - лучший ключ (самый быстрый)
- `top_50_keys` - топ-50 рабочих ключей
- `sources` - результаты по каждому источнику

### all_working_keys.txt
Все рабочие ключи в текстовом формате (по одному на строку)

### best_key.txt
Лучший (самый быстрый) ключ

### *_working.txt
Рабочие ключи по каждому источнику отдельно:
- `BLACK_VLESS_RUS_working.txt`
- `WHITE_CIDR_RU_checked_working.txt`
- и т.д.

## Использование результатов

### Способ 1: Прямое скачивание с GitHub

1. Зайдите в ваш репозиторий на GitHub
2. Откройте папку `output/`
3. Скачайте нужный файл (например, `best_key.txt` или `all_working_keys.txt`)
4. Скопируйте ключ и вставьте в ваш VPN клиент

### Способ 2: Raw ссылка

Используйте прямую ссылку на raw файл:
```
https://raw.githubusercontent.com/ВАШ_ЮЗЕРНЕЙМ/ВАШ_РЕПОЗИТОРИЙ/main/output/best_key.txt
```

### Способ 3: GitHub Pages (опционально)

Можно настроить GitHub Pages для автоматического отображения результатов.

## Изменение расписания

Чтобы изменить частоту проверки, отредактируйте файл `.github/workflows/check-keys.yml`:

```yaml
schedule:
  # Запуск каждые 30 минут
  - cron: '*/30 * * * *'
  
  # Или каждые 6 часов
  - cron: '0 */6 * * *'
  
  # Или каждые 12 часов
  - cron: '0 */12 * * *'
```

Формат cron: `минута час день_месяца месяц день_недели`

## Просмотр логов

1. Перейдите в раздел **Actions**
2. Нажмите на последний запуск workflow
3. Нажмите на job "check-keys"
4. Разверните шаг "Run key checker" чтобы увидеть логи

## Troubleshooting

### Workflow не запускается автоматически

1. Проверьте что workflow файл находится в `.github/workflows/check-keys.yml`
2. Проверьте что GitHub Actions включены в настройках репозитория
3. Проверьте формат cron выражения

### Ошибка при запуске

1. Посмотрите логи в разделе Actions
2. Убедитесь что файл `auto_check.py` существует
3. Проверьте что зависимости установлены (workflow делает это автоматически)

### Нет результатов в output/

1. Проверьте логи - возможно все ключи недоступны
2. Попробуйте запустить workflow вручную
3. Проверьте что у workflow есть права на запись (permissions: contents: write)

## Статистика

В `working_keys.json` вы найдете статистику по каждому источнику:
- `total` - всего ключей в источнике
- `working` - количество рабочих ключей
- `best` - лучший ключ из источника

## Интеграция с другими сервисами

Можно настроить отправку уведомлений:
- Telegram бот при появлении новых ключей
- Email уведомления
- Discord webhook

Пример для Telegram (добавить в workflow):

```yaml
- name: Send Telegram notification
  if: success()
  run: |
    curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
      -d "chat_id=$TELEGRAM_CHAT_ID" \
      -d "text=VPN keys updated: $(cat output/working_keys.json | jq '.total_working_keys') working keys"
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

## Безопасность

- Не храните приватные ключи в репозитории
- Используйте GitHub Secrets для токенов и паролей
- Для приватных репозиториев настройте доступ по токену

## Лицензия

MIT License

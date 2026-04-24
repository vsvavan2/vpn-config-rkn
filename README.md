# VPN Key Collector - Windows GUI Application

Приложение для автоматического сбора и проверки VLESS ключей с GitHub для обхода глушилок и белых списков в России.

## Функции

- 🔄 **Автоматический сбор ключей** с GitHub репозиториев
- 🔍 **Проверка работоспособности** ключей (TCP-доступность + пинг)
- 📊 **Сортировка по задержке** - лучшие ключи сверху
- ⏰ **Авто-проверка** каждые 60 минут
- 📋 **Копирование ключей** в буфер обмена
- 💾 **Сохранение** рабочих ключей в файл
- 🚀 **Интеграция с v2rayN** для подключения

## Установка

### Требования

- Windows 10/11
- Python 3.8+
- Библиотека `requests`

### Установка зависимостей

```bash
pip install requests
```

### Запуск приложения

```bash
python vpn_key_app.py
```

## Использование

### 1. Выбор источника ключей

**BLACK (обычный VPN):**
- BLACK (обычный VPN) - Полный туннель трафика через VPN
- BLACK Mobile - Оптимизировано для мобильных сетей
- BLACK SS+All - Shadowsocks + All протоколы

**WHITE (белые списки) - для глушилок:**
- WHITE CIDR (белые списки) - Проверенные CIDR конфиги
- WHITE CIDR All - Все CIDR конфиги
- WHITE SNI (белые списки) - SNI конфиги
- WHITE Reality Mobile - Reality для мобильных
- WHITE Reality Mobile 2 - Reality для мобильных (альтернатива)

**Дополнительные источники:**
- VPN-sub (yror382) - Подписка от yror382-netizen

**V2Box (vorz1k) - глобальные подписки:**
- V2Box Supreme 1 - Первая подписка
- V2Box Supreme 2 - Вторая подписка
- V2Box Supreme 3 - Третья подписка

**Kort0881 - проверенные конфиги:**
- Kort0881 VLESS Clean - Проверенные VLESS конфиги
- Kort0881 VMess Clean - Проверенные VMess конфиги
- Kort0881 Trojan Clean - Проверенные Trojan конфиги
- Kort0881 Shadowsocks Clean - Проверенные Shadowsocks конфиги

**Barry-Far - обновляются каждые 15 минут:**
- Barry-Far All Configs - Все конфиги
- Barry-Far Sub 1, 2, 3 - Разделенные подписки
- Barry-Far VLESS - Только VLESS
- Barry-Far VMess - Только VMess

**Epodonios - обновляются каждые 5 минут:**
- Epodonios All Configs - Все конфиги
- Epodonios Sub 1, 2, 3 - Разделенные подписки
- Epodonios VLESS - Только VLESS
- Epodonios VMess - Только VMess

**Hans-Thomas - свежие серверы:**
- Hans-Thomas Servers - Свежие серверы

### 2. Проверка ключей

1. Выберите источник ключей
2. Нажмите кнопку "🔍 Проверить ключи"
3. Дождитесь завершения проверки
4. Рабочие ключи появятся в списке

### 3. Подключение

**Способ 1: Через v2rayN**
1. Нажмите "📋 Копировать лучший ключ"
2. Откройте v2rayN (кнопка "🚀 Открыть v2rayN")
3. Вставьте ключ в v2rayN
4. Подключитесь

**Способ 2: Прямое копирование**
1. Скопируйте ключ из списка
2. Вставьте в ваше VPN-приложение (Hiddify, Streisand и др.)

### 4. Авто-проверка

Включите опцию "Авто-проверка (1 час)" для автоматического обновления ключей каждый час.

## Источники ключей

Ключи загружаются из репозитория [igareck/vpn-configs-for-russia](https://github.com/igareck/vpn-configs-for-russia):

- `BLACK_VLESS_RUS.txt` - Обычные VPN ключи
- `BLACK_VLESS_RUS_mobile.txt` - Оптимизировано для мобильных
- `WHITE-CIDR-RU-checked.txt` - Белые списки

## Важно для мобильных сетей с глушилками

⚠️ **Для работы на мобильных сетях с глушилками используйте только WHITE (белые списки)**

Система позитивной фильтрации (с сентября 2025) блокирует входящий трафик к IP не в федеральном белом списке. WHITE ключи используют специальные методы обхода.

## Скачать v2rayN

https://github.com/2dust/v2rayN/releases

Скачайте `v2rayN.zip` или `v2rayN-Core.zip` из раздела Releases.

## Структура проекта

```
VPN-Key-Collector/
├── vpn_key_app.py          # GUI приложение
├── vless-checker-main/     # Оригинальный скрипт проверки
│   ├── checker.py
│   └── check_and_save.py
└── README.md              # Этот файл
```

## Лицензия

MIT License

## Полезные ссылки

- [v2rayN](https://github.com/2dust/v2rayN) - Windows VPN клиент
- [igareck/vpn-configs-for-russia](https://github.com/igareck/vpn-configs-for-russia) - Источник ключей
- [tiagorrg/vless-checker](https://github.com/tiagorrg/vless-checker) - Оригинальный checker

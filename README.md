# VPN Config RKN - Автоматическая проверка VLESS ключей

🚀 Автоматическая система сбора и проверки VLESS ключей для обхода глушилок и белых списков в России. Проверяет 25+ источников ключей с GitHub, фильтрует нерабочие и сортирует по скорости.

## 🌐 Проект на GitHub

**Репозиторий:** https://github.com/vsvavan2/vpn-config-rkn

## ✨ Особенности

### GitHub Actions Автоматизация
- ⏰ **Автоматическая проверка** каждый час
- 🔍 **Проверка 25+ источников** ключей
- 📊 **Фильтрация и сортировка** по скорости
- 💾 **Автосохранение** рабочих ключей в репозитории
- 📡 **Доступ к результатам** через GitHub

### Windows GUI Приложение
- 🔄 **Автоматический сбор ключей** с GitHub репозиториев
- 🔍 **Проверка работоспособности** ключей (TCP-доступность + пинг)
- 📊 **Сортировка по задержке** - лучшие ключи сверху
- ⏰ **Авто-проверка** каждые 60 минут
- 📋 **Копирование ключей** в буфер обмена
- 💾 **Сохранение** рабочих ключей в файл
- 🚀 **Интеграция с v2rayN** для подключения

## 📂 Результаты работы

После автоматической проверки в папке `output/` появляются файлы:
- `working_keys.json` - все результаты в JSON формате
- `all_working_keys.txt` - все рабочие ключи
- `best_key.txt` - лучший (самый быстрый) ключ
- `*_working.txt` - рабочие ключи по каждому источнику

## 🔗 Быстрый доступ к ключам

**Лучший ключ:**
```
https://raw.githubusercontent.com/vsvavan2/vpn-config-rkn/main/output/best_key.txt
```

**Все рабочие ключи:**
```
https://raw.githubusercontent.com/vsvavan2/vpn-config-rkn/main/output/all_working_keys.txt
```

**Результаты в JSON:**
```
https://raw.githubusercontent.com/vsvavan2/vpn-config-rkn/main/output/working_keys.json
```

## 📋 Источники ключей (25 источников)

**BLACK (обычный VPN):**
- BLACK (обычный VPN), BLACK Mobile, BLACK SS+All

**WHITE (белые списки) - для глушилок:**
- WHITE CIDR (белые списки), WHITE CIDR All, WHITE SNI (белые списки)
- WHITE Reality Mobile, WHITE Reality Mobile 2

**Дополнительные источники:**
- VPN-sub (yror382)

**V2Box (vorz1k) - глобальные подписки:**
- V2Box Supreme 1, 2, 3

**Kort0881 - проверенные конфиги:**
- Kort0881 VLESS Clean, VMess Clean, Trojan Clean, Shadowsocks Clean

**Barry-Far - обновляются каждые 15 минут:**
- Barry-Far All Configs, Sub 1-3, VLESS, VMess

**Epodonios - обновляются каждые 5 минут:**
- Epodonios All Configs, Sub 1-3, VLESS, VMess

**Hans-Thomas - свежие серверы:**
- Hans-Thomas Servers

## 💻 Установка Windows GUI приложения

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

Подробная инструкция установки: [INSTALLATION_GUIDE_RU.md](INSTALLATION_GUIDE_RU.md)

## 🤖 Настройка GitHub Actions

Подробная инструкция по настройке автоматической проверки: [GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)

## 🎯 Использование

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

## 👤 Автор

**Сайт автора:** [phphack.ru](https://phphack.ru)

**О сайте phphack.ru:**
- 📚 **Бесплатные курсы и тренинги** - тысячи платных курсов бесплатно
- 💼 **Бизнес курсы** - схемы заработка, создание бизнеса
- 🖥️ **Программирование** - Python, C#, C++, AI, IDE
- 🎨 **Графика и дизайн** - создание контента
- 🔍 **SEO & SMM** - продвижение сайтов
- 💰 **Криптовалюта** - инвестиции и трейдинг
- 🌐 **Сайтостроение** - создание и разработка сайтов
- 📱 **Rust Oxide** - плагины, скрипты, программы для Rust
- 🔐 **VPN решения** - безлимитные VLESS ключи

На форуме phphack.ru вы найдете бесплатные обучающие материалы по программированию, бизнесу, дизайну и многим другим темам, а также полезные инструменты и скрипты.

## 📞 Полезные ссылки

- [v2rayN](https://github.com/2dust/v2rayN) - Windows VPN клиент
- [igareck/vpn-configs-for-russia](https://github.com/igareck/vpn-configs-for-russia) - Источник ключей
- [tiagorrg/vless-checker](https://github.com/tiagorrg/vless-checker) - Оригинальный checker
- [phphack.ru](https://phphack.ru) - Форум с бесплатными курсами и инструментами

## 📜 Лицензия

MIT License

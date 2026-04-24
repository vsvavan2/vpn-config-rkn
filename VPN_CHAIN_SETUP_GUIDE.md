# Полная инструкция: Цепочка VPN для обхода глушилок и белых списков в России

## Содержание
1. [Введение](#введение)
2. [Теория работы](#теория-работы)
3. [Настройка европейского сервера (Exit Node)](#настройка-европейского-сервера-exit-node)
4. [Настройка российского сервера (Bridge Node)](#настройка-российского-сервера-bridge-node)
5. [Генерация ссылок для подключения](#генерация-ссылок-для-подключения)
6. [Поиск и решение проблем](#поиск-и-решение-проблем)

---

## Введение

Эта инструкция описывает настройку цепочки VPN для обхода глушилок и белых списков на мобильных сетях в России.

**Схема работы:**
```
Клиент (мобильный) → Российский VPS (белый IP) → Европейский VPS → Интернет
```

**Почему это работает:**
- Российские мобильные операторы блокируют по IP + SNI
- VPS в Yandex Cloud/VK Cloud имеют IP в федеральном белом списке
- Цепочка позволяет обойти блокировку и направить трафик через Европу

---

## Теория работы

### Проблема блокировок в России

1. **Система позитивной фильтрации (Whitelists) с сентября 2025**
   - Внедрена система 2-уровневой фильтрации: полная блокировка → пропуск только авторизованных ресурсов
   - Работает в 57+ регионах России
   - В белых списках: VK, Yandex, Ozon, Wildberries, банки, госслужбы, MAX messenger
   - **VPN-серверы НЕ в белых списках** - это ключевая проблема
   - Технология использует EcoSGE (разработана RDP.ru)

2. **Комбинированная блокировка IP + SNI**
   - Даже с правильным SNI, IP сервера должен быть в белом списке
   - Операторы используют CIDR блокировки

3. **Блокировка входящего трафика на мобильных сетях**
   - CGNAT (Carrier Grade NAT) блокирует входящие соединения
   - TCP соединения "замораживаются" после 15-20KB данных
   - Глушилки блокируют входящие пакеты к неавторизованным IP

4. **Белые списки IP**
   - Только Yandex Cloud и VK Cloud имеют IP в федеральном белом списке
   - Другие провайдеры (Timeweb, Selectel и т.д.) НЕ в белых списках

### Решение: Цепочка через российский VPS

**Почему это работает:**
- Российский VPS (Yandex Cloud/VK Cloud) имеет IP в белом списке
- Клиент подключается к российскому серверу (входящий трафик разрешен)
- Российский сервер перенаправляет трафик на европейский сервер
- Европейский сервер обеспечивает выход в интернет

---

## Настройка европейского сервера (Exit Node)

### Шаг 1: Создание VPS

**Рекомендуемые провайдеры:**
- Hetzner (Германия)
- DigitalOcean (Нидерланды)
- Contabo (Германия)
- VDSina (Нидерланды)

**Параметры VPS:**
- ОС: Ubuntu 24.04 LTS
- Конфигурация: 1-2 vCPU, 1-2 GB RAM
- Диск: 20 GB SSD

### Шаг 2: Подключение по SSH

```bash
ssh root@IP_АДРЕС_ЕВРОПЕЙСКОГО_VPS
```

### Шаг 3: Установка Xray

```bash
# Установка Xray
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Проверка версии (должна быть минимум 25.12.8)
xray version
```

### Шаг 4: Генерация ключей

```bash
# Генерация UUID
xray uuid
# Сохраните полученный UUID (например: 526e217d-f286-49e5-a261-a5a659efbfac)

# Генерация Reality ключей
xray x25519
# Сохраните PrivateKey и PublicKey
# Пример:
# PrivateKey: oPxjHpgoW4_TJluZl34IlUXYyoObVhNGjTTjK_rAkn8
# PublicKey: 3uQQ3Kzq35V6hxf0aI_hg-0QX8rRKlvsyiJEN3vBch8
```

### Шаг 5: Настройка конфигурации Xray

```bash
# Создание конфигурационного файла
cat > /usr/local/etc/xray/config.json << 'EOF'
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": 8443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "ВАШ_UUID_ЗДЕСЬ"
          }
        ],
        "decryption": "none",
        "sniffing": {
          "enabled": true,
          "destOverride": [
            "http",
            "tls",
            "quic",
            "fakedns"
          ],
          "routeOnly": true
        }
      },
      "streamSettings": {
        "network": "ws",
        "wsSettings": {
          "path": "/xray-ws"
        }
      },
      "mux": {
        "enabled": true,
        "concurrency": 8
      }
    },
    {
      "port": 8444,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "ВАШ_UUID_ЗДЕСЬ"
          }
        ],
        "decryption": "none",
        "sniffing": {
          "enabled": true,
          "destOverride": [
            "http",
            "tls",
            "quic",
            "fakedns"
          ],
          "routeOnly": true
        }
      },
      "streamSettings": {
        "network": "ws",
        "wsSettings": {
          "path": "/xray-anti-dpi"
        }
      },
      "mux": {
        "enabled": true,
        "concurrency": 8
      }
    },
    {
      "port": 8445,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "ВАШ_UUID_ЗДЕСЬ"
          }
        ],
        "decryption": "none",
        "sniffing": {
          "enabled": true,
          "destOverride": [
            "http",
            "tls",
            "quic",
            "fakedns"
          ],
          "routeOnly": true
        }
      },
      "streamSettings": {
        "network": "grpc",
        "security": "reality",
        "realitySettings": {
          "dest": "ads.x5.ru:443",
          "serverNames": [
            "ads.x5.ru"
          ],
          "privateKey": "ВАШ_PRIVATE_KEY_ЗДЕСЬ",
          "shortIds": [
            ""
          ]
        },
        "grpcSettings": {
          "serviceName": "grpc-service"
        }
      },
      "mux": {
        "enabled": true,
        "concurrency": 4
      },
      "tag": "vless-grpc-reality"
    },
    {
      "port": 1080,
      "listen": "0.0.0.0",
      "protocol": "socks",
      "settings": {
        "auth": "password",
        "udp": true,
        "accounts": [
          {
            "user": "proxyuser",
            "pass": "ВАШ_ПАРОЛЬ_ЗДЕСЬ"
          }
        ]
      },
      "sniffing": {
        "enabled": true,
        "destOverride": [
          "http",
          "tls"
        ]
      },
      "tag": "socks-in"
    }
  ],
  "outbounds": [
    {
      "protocol": "freedom"
    }
  ]
}
EOF
```

**Важно:** Замените:
- `ВАШ_UUID_ЗДЕСЬ` на ваш сгенерированный UUID
- `ВАШ_PRIVATE_KEY_ЗДЕСЬ` на ваш сгенерированный PrivateKey
- `ВАШ_ПАРОЛЬ_ЗДЕСЬ` на ваш пароль для SOCKS5

### Шаг 6: Генерация пароля для SOCKS5

```bash
# Генерация случайного пароля
openssl rand -base64 12
# Сохраните полученный пароль
```

### Шаг 7: Перезапуск Xray и проверка

```bash
# Проверка конфигурации
xray -test -config /usr/local/etc/xray/config.json

# Перезапуск сервиса
systemctl restart xray

# Проверка статуса
systemctl status xray

# Проверка открытых портов
ss -tulpn | grep -E "8443|8444|8445|1080"
```

### Шаг 8: Открытие портов в firewall

```bash
# Если используется ufw
ufw allow 8443/tcp
ufw allow 8444/tcp
ufw allow 8445/tcp
ufw allow 1080/tcp
ufw allow 443/tcp
ufw allow 80/tcp

# Если используется iptables
iptables -A INPUT -p tcp --dport 8443 -j ACCEPT
iptables -A INPUT -p tcp --dport 8444 -j ACCEPT
iptables -A INPUT -p tcp --dport 8445 -j ACCEPT
iptables -A INPUT -p tcp --dport 1080 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
```

---

## Настройка российского сервера (Bridge Node)

### Шаг 1: Создание VPS в Yandex Cloud, VK Cloud или Timeweb

**Yandex Cloud:**
1. Перейдите на console.yandex.cloud
2. Создайте каталог
3. Создайте виртуальную машину:
   - Образ: Ubuntu 24.04 LTS (без Secure Boot, без CUDA)
   - Зона: ru-central1-a (Москва)
   - Конфигурация: 2 vCPU, 2 GB RAM
   - Диск: 20 GB SSD
   - Сеть: публичный IP адрес

**VK Cloud:**
1. Перейдите на cloud.vk.com
2. Создайте проект
3. Создайте виртуальную машину:
   - Образ: Ubuntu 24.04 LTS
   - Конфигурация: 2 vCPU, 2 GB RAM
   - Диск: 20 GB SSD
   - Сеть: публичный IP адрес

**Timeweb (hosting.timeweb.com):**
1. Перейдите на hosting.timeweb.com
2. Зарегистрируйтесь или войдите в аккаунт
3. Создайте VPS (Cloud):
   - Выберите тариф "Cloud" или "VPS"
   - Локация: Россия (Москва или Санкт-Петербург)
   - Операционная система: Ubuntu 24.04 LTS
   - Конфигурация: 2 vCPU, 2 GB RAM (минимальная)
   - Диск: 20 GB SSD
   - Сеть: публичный IPv4 адрес
4. После создания получите:
   - IP адрес VPS
   - Пароль root (или SSH ключ)
   - Данные для подключения по SSH

**⚠️ ВАЖНО: Timeweb НЕ рекомендуется для мобильных сетей с глушилками**
- Timeweb IP НЕ в федеральном белом списке
- Сайт hosting.timeweb.com открывается, но VPS IP блокируется глушилками
- **НЕ будет работать на мобильных сетях с активными глушилками**
- Используйте только Yandex Cloud или VK Cloud для работы с глушилками

### Шаг 2: Подключение по SSH

```bash
ssh root@IP_АДРЕС_РОССИЙСКОГО_VPS
```

### Шаг 3: Установка Xray

```bash
# Установка Xray
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# Проверка версии
xray version
```

### Шаг 4: Генерация ключей для российского сервера

```bash
# Генерация UUID
xray uuid
# Сохраните полученный UUID (например: c21b2a45-de41-4405-a78e-387acc079caf)

# Генерация Reality ключей
xray x25519
# Сохраните PrivateKey и PublicKey
# Пример:
# PrivateKey: sEarAZGwrFmXFgpzmV13fRIfbl2Hzmx1NqFfxhfUBlI
# PublicKey: lh8TzOCZrUdXN-zO5EYUy8LB6QhxH6g-A0473palGBk
```

### Шаг 5: Генерация пароля для SOCKS5

```bash
# Генерация случайного пароля
openssl rand -base64 12
# Сохраните полученный пароль
```

### Шаг 6: Настройка конфигурации Xray (цепочка к европейскому серверу)

```bash
cat > /usr/local/etc/xray/config.json << 'EOF'
{
  "log": {
    "loglevel": "warning"
  },
  "inbounds": [
    {
      "port": 443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "ВАШ_UUID_РОССИЙСКОГО_СЕРВЕРА"
          }
        ],
        "decryption": "none",
        "sniffing": {
          "enabled": true,
          "destOverride": [
            "http",
            "tls",
            "quic",
            "fakedns"
          ]
        }
      },
      "streamSettings": {
        "network": "grpc",
        "security": "reality",
        "realitySettings": {
          "dest": "ads.x5.ru:443",
          "serverNames": [
            "ads.x5.ru"
          ],
          "privateKey": "ВАШ_PRIVATE_KEY_РОССИЙСКОГО_СЕРВЕРА",
          "shortIds": [
            ""
          ]
        },
        "grpcSettings": {
          "serviceName": "grpc-service"
        }
      },
      "mux": {
        "enabled": true,
        "concurrency": 4
      },
      "tag": "vless-in"
    },
    {
      "port": 1080,
      "listen": "0.0.0.0",
      "protocol": "socks",
      "settings": {
        "auth": "password",
        "udp": true,
        "accounts": [
          {
            "user": "proxyuser",
            "pass": "ВАШ_ПАРОЛЬ_РОССИЙСКОГО_СЕРВЕРА"
          }
        ]
      },
      "sniffing": {
        "enabled": true,
        "destOverride": [
          "http",
          "tls"
        ]
      },
      "tag": "socks-in"
    }
  ],
  "outbounds": [
    {
      "tag": "chain-to-europe",
      "protocol": "vless",
      "settings": {
        "vnext": [
          {
            "address": "IP_АДРЕС_ЕВРОПЕЙСКОГО_СЕРВЕРА",
            "port": 8445,
            "users": [
              {
                "id": "UUID_ЕВРОПЕЙСКОГО_СЕРВЕРА",
                "encryption": "none"
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "grpc",
        "security": "reality",
        "realitySettings": {
          "fingerprint": "chrome",
          "serverName": "ads.x5.ru",
          "publicKey": "PUBLIC_KEY_ЕВРОПЕЙСКОГО_СЕРВЕРА",
          "shortId": ""
        },
        "grpcSettings": {
          "serviceName": "grpc-service"
        }
      },
      "mux": {
        "enabled": true,
        "concurrency": 4
      }
    },
    {
      "protocol": "freedom",
      "tag": "direct"
    }
  ],
  "routing": {
    "domainStrategy": "IPIfNonMatch",
    "rules": [
      {
        "type": "field",
        "outboundTag": "direct",
        "domain": [
          "geosite:category-ru",
          "regexp:\\.ru$",
          "geosite:yandex",
          "full:cp.cloudflare.com"
        ]
      },
      {
        "type": "field",
        "inboundTag": ["vless-in"],
        "outboundTag": "chain-to-europe"
      },
      {
        "type": "field",
        "inboundTag": ["socks-in"],
        "outboundTag": "chain-to-europe"
      }
    ]
  }
}
EOF
```

**Важно:** Замените:
- `ВАШ_UUID_РОССИЙСКОГО_СЕРВЕРА` на UUID российского сервера
- `ВАШ_PRIVATE_KEY_РОССИЙСКОГО_СЕРВЕРА` на PrivateKey российского сервера
- `ВАШ_ПАРОЛЬ_РОССИЙСКОГО_СЕРВЕРА` на пароль SOCKS5 российского сервера
- `IP_АДРЕС_ЕВРОПЕЙСКОГО_СЕРВЕРА` на IP европейского сервера
- `UUID_ЕВРОПЕЙСКОГО_СЕРВЕРА` на UUID европейского сервера
- `PUBLIC_KEY_ЕВРОПЕЙСКОГО_СЕРВЕРА` на PublicKey европейского сервера

### Шаг 7: Перезапуск Xray и проверка

```bash
# Проверка конфигурации
xray -test -config /usr/local/etc/xray/config.json

# Перезапуск сервиса
systemctl restart xray

# Проверка статуса
systemctl status xray

# Проверка открытых портов
ss -tulpn | grep -E "443|1080"
```

### Шаг 8: Открытие портов в firewall

```bash
# Если используется ufw
ufw allow 443/tcp
ufw allow 1080/tcp

# Если используется iptables
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 1080 -j ACCEPT
```

---

## Генерация ссылок для подключения

### Ссылка для подключения к цепочке (через российский сервер)

```
vless://UUID_РОССИЙСКОГО_СЕРВЕРА@IP_РОССИЙСКОГО_СЕРВЕРА:443?encryption=none&security=reality&sni=ads.x5.ru&fp=chrome&pbk=PUBLIC_KEY_РОССИЙСКОГО_СЕРВЕРА&serviceName=grpc-service&type=grpc#Chain-RU-EU
```

**Пример:**
```
vless://c21b2a45-de41-4405-a78e-387acc079caf@193.178.170.160:443?encryption=none&security=reality&sni=ads.x5.ru&fp=chrome&pbk=lh8TzOCZrUdXN-zO5EYUy8LB6QhxH6g-A0473palGBk&serviceName=grpc-service&type=grpc#Chain-RU-EU
```

### Прямая ссылка на европейский сервер (для тестирования)

```
vless://UUID_ЕВРОПЕЙСКОГО_СЕРВЕРА@IP_ЕВРОПЕЙСКОГО_СЕРВЕРА:8445?encryption=none&security=reality&sni=ads.x5.ru&fp=chrome&pbk=PUBLIC_KEY_ЕВРОПЕЙСКОГО_СЕРВЕРА&serviceName=grpc-service&type=grpc#Direct-EU
```

---

## Поиск и решение проблем

### Проблема: Нет входящего трафика на мобильной сети

**Причина:** IP сервера не в федеральном белом списке

**Система позитивной фильтрации (с сентября 2025):**
- Внедрена 2-уровневая фильтрация: полная блокировка → пропуск только авторизованных ресурсов
- Работает в 57+ регионах России
- VPN-серверы НЕ в белых списках по умолчанию
- Только Yandex Cloud и VK Cloud имеют IP в федеральном белом списке

**Решение:**
1. **Используйте только Yandex Cloud или VK Cloud** для российского VPS
2. Timeweb, Selectel и другие провайдеры НЕ в белых списках
3. Проверьте прямое подключение к европейскому серверу - если тоже нет входящих, проблема в операторе
4. Протестируйте в разных регионах (глушилки активны не везде)

### Проблема: "Не защищено" в браузере при подключении к запрещенным сайтам

**Причина:** Reality подделывает сертификат, это нормально

**Решение:** Это особенность протокола Reality, не влияет на работу VPN

### Проблема: Соединение устанавливается, но данные не передаются

**Причина:** Блокировка ответных пакетов оператором

**Решение:**
1. Проверьте что российский сервер действительно в белом списке
2. Попробуйте другой SNI из whitelist (yandex.ru, ads.x5.ru)
3. Убедитесь что цепочка настроена правильно

### Проблема: Xray не запускается

**Причина:** Ошибка в конфигурации

**Решение:**
```bash
# Проверка конфигурации
xray -test -config /usr/local/etc/xray/config.json

# Просмотр логов
journalctl -u xray -f
```

### Проблема: Порты не слушаются

**Причина:** Firewall блокирует порты

**Решение:**
```bash
# Проверка открытых портов
ss -tulpn

# Проверка правил firewall
iptables -L -n
# или
ufw status
```

### Проблема: Медленная скорость

**Возможные причины:**
1. Слишком маленькая конфигурация VPS
2. Далекое расположение серверов
3. Перегрузка сети оператора

**Решения:**
1. Увеличьте конфигурацию VPS
2. Выберите серверы ближе к вашему региону
3. Попробуйте другой порт/протокол

---

## Дополнительные рекомендации

1. **Регулярно обновляйте Xray**
   ```bash
   bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ update
   ```

2. **Используйте GeoIP/GeoSite файлы для маршрутизации**
   - Скачайте geoip.dat и geosite.dat
   - Разместите в /usr/local/share/xray/

3. **Настройте мониторинг**
   - Используйте systemctl status xray
   - Настройте логирование

4. **Создайте бэкапы конфигураций**
   ```bash
   cp /usr/local/etc/xray/config.json /usr/local/etc/xray/config.json.backup
   ```

5. **Используйте разные UUID для разных серверов**
   - Это повышает безопасность

---

## Полезные ресурсы

- [Xray документация](https://xtls.github.io/)
- [GitHub Xray](https://github.com/XTLS/Xray-core)
- [Белый список доменов России](https://github.com/hxehex/russia-mobile-internet-whitelist)
- [Habr: Обход белых списков](https://habr.com/en/articles/990206/)

---

## Заключение

Эта настройка обеспечивает стабильное подключение к интернету через цепочку VPN, обходя глушилки и белые списки на мобильных сетях в России.

**Ключевые моменты:**
- Российский сервер в Yandex Cloud/VK Cloud (белый IP)
- Цепочка: Клиент → Россия → Европа → Интернет
- SNI из белого списка (ads.x5.ru)
- gRPC transport с Reality
- Mux для снижения нагрузки

При правильной настройке эта схема обеспечивает стабильную работу даже в условиях активных глушилок.

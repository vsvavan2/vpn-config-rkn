#!/usr/bin/env python3
import requests
import socket
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Прямая ссылка на raw-файл с ключами
GITHUB_RAW_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS.txt"

MAX_WORKERS = 15       # сколько ключей проверять параллельно
TEST_TIMEOUT = 5       # таймаут подключения в секундах
MAX_LATENCY_MS = 2000  # ключи медленнее этого — отбрасываем


def fetch_keys(url):
    print(f"📥 Загружаем ключи из GitHub...")
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        keys = [line.strip() for line in lines if line.strip().startswith("vless://")]
        print(f"✅ Найдено {len(keys)} VLESS-ключей\n")
        return keys
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        sys.exit(1)


def parse_host_port(key):
    try:
        without_scheme = key[len("vless://"):]
        at_idx = without_scheme.rfind("@")
        after_at = without_scheme[at_idx + 1:]
        host_port = after_at.split("?")[0].split("#")[0]
        if ":" in host_port:
            host, port = host_port.rsplit(":", 1)
            return host.strip("[]"), int(port)
    except Exception:
        pass
    return None, None


def test_key(key):
    host, port = parse_host_port(key)
    if not host:
        return {"key": key, "host": "?", "port": "?", "status": "invalid", "latency_ms": None}
    
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TEST_TIMEOUT)
        result = sock.connect_ex((host, port))
        sock.close()
        elapsed = round((time.time() - start) * 1000, 1)
        
        if result == 0:
            return {"key": key, "host": host, "port": port, "status": "ok", "latency_ms": elapsed}
        else:
            return {"key": key, "host": host, "port": port, "status": "closed", "latency_ms": None}
    except Exception:
        return {"key": key, "host": host, "port": port, "status": "error", "latency_ms": None}


def main():
    keys = fetch_keys(GITHUB_RAW_URL)

    print(f"🔍 Тестируем {len(keys)} ключей...\n")
    results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(test_key, key): key for key in keys}
        done = 0
        for future in as_completed(futures):
            r = future.result()
            done += 1
            icon = "✅" if r["status"] == "ok" else "❌"
            latency = f"{r['latency_ms']} мс" if r["latency_ms"] else "недоступен"
            print(f"[{done}/{len(keys)}] {icon} {r['host']}:{r['port']} — {latency}")
            results.append(r)

    # Фильтруем и сортируем
    working = sorted(
        [r for r in results if r["status"] == "ok" and r["latency_ms"] <= MAX_LATENCY_MS],
        key=lambda x: x["latency_ms"]
    )

    print("\n" + "="*55)
    print(f"📊 ИТОГ: рабочих {len(working)} из {len(keys)}")
    print("="*55)

    if working:
        print(f"\n🏆 ТОП-5 самых быстрых:")
        for i, r in enumerate(working[:5], 1):
            print(f"  {i}. {r['host']}:{r['port']} — {r['latency_ms']} мс")

        # Сохраняем рабочие ключи
        with open("working_keys.txt", "w") as f:
            for r in working:
                f.write(r["key"] + "\n")
        print(f"\n💾 Все рабочие ключи сохранены в working_keys.txt")

        print(f"\n⚡ ЛУЧШИЙ КЛЮЧ (скопируй в приложение):")
        print(f"\n{working[0]['key']}\n")
    else:
        print("😕 Рабочих ключей не найдено. Попробуй позже.")


if __name__ == "__main__":
    main()
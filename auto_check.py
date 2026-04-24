#!/usr/bin/env python3
"""
Автоматический скрипт для проверки VPN ключей на GitHub Actions
Проверяет ключи из всех источников, фильтрует рабочие и сохраняет результаты
"""

import requests
import socket
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

# Источники ключей
KEY_SOURCES = {
    "BLACK_VLESS_RUS": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS.txt",
    "BLACK_VLESS_RUS_mobile": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS_mobile.txt",
    "BLACK_SS_All_RUS": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_SS+All_RUS.txt",
    "WHITE_CIDR_RU_checked": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt",
    "WHITE_CIDR_RU_all": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-all.txt",
    "WHITE_SNI_RU_all": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-SNI-RU-all.txt",
    "WHITE_Reality_Mobile": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    "WHITE_Reality_Mobile_2": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt",
    "VPN_sub_yror382": "https://raw.githubusercontent.com/yror382-netizen/VPN-sub/main/sub.txt",
    "V2Box_Supreme_1": "https://raw.githubusercontent.com/vorz1k/v2box/main/supreme_vpns_1.txt",
    "V2Box_Supreme_2": "https://raw.githubusercontent.com/vorz1k/v2box/main/supreme_vpns_2.txt",
    "V2Box_Supreme_3": "https://raw.githubusercontent.com/vorz1k/v2box/main/supreme_vpns_3.txt",
    "Kort0881_VLESS": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt",
    "Kort0881_VMess": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vmess.txt",
    "Kort0881_Trojan": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/trojan.txt",
    "Kort0881_Shadowsocks": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/ss.txt",
    "BarryFar_All": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_Sub.txt",
    "BarryFar_Sub1": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "BarryFar_Sub2": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub2.txt",
    "BarryFar_Sub3": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub3.txt",
    "BarryFar_VLESS": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt",
    "BarryFar_VMess": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vmess.txt",
    "Epodonios_All": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "Epodonios_Sub1": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Sub1.txt",
    "Epodonios_Sub2": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Sub2.txt",
    "Epodonios_Sub3": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Sub3.txt",
    "Epodonios_VLESS": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vless.txt",
    "Epodonios_VMess": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vmess.txt",
    "HansThomas_Servers": "https://raw.githubusercontent.com/hans-thomas/v2ray-subscription/master/servers.txt"
}

MAX_WORKERS = 30
TEST_TIMEOUT = 5
MAX_LATENCY_MS = 2000

OUTPUT_DIR = "output"


def parse_host_port(key):
    """Парсит host и port из ключа"""
    try:
        # Поддержка разных схем
        if key.startswith("vless://"):
            without_scheme = key[len("vless://"):]
        elif key.startswith("vmess://"):
            without_scheme = key[len("vmess://"):]
        elif key.startswith("trojan://"):
            without_scheme = key[len("trojan://"):]
        elif key.startswith("ss://"):
            without_scheme = key[len("ss://"):]
        else:
            return None, None
        
        at_idx = without_scheme.rfind("@")
        if at_idx == -1:
            return None, None
            
        after_at = without_scheme[at_idx + 1:]
        host_port = after_at.split("?")[0].split("#")[0]
        
        if ":" in host_port:
            host, port = host_port.rsplit(":", 1)
            return host.strip("[]"), int(port)
    except Exception:
        pass
    return None, None


def test_key(key):
    """Проверяет доступность ключа"""
    host, port = parse_host_port(key)
    if not host:
        return None
    
    try:
        infos = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except Exception:
        return None
    
    best = None
    for (family, socktype, proto, canonname, sockaddr) in infos:
        start = time.time()
        try:
            sock = socket.socket(family, socktype)
            sock.settimeout(TEST_TIMEOUT)
            result = sock.connect_ex(sockaddr)
            sock.close()
            elapsed = round((time.time() - start) * 1000, 1)
            
            if result == 0 and elapsed <= MAX_LATENCY_MS:
                if best is None or elapsed < best["latency_ms"]:
                    best = {"key": key, "host": host, "port": port, "latency_ms": elapsed}
        except Exception:
            pass
    
    return best


def fetch_keys(url):
    """Загружает ключи из URL"""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        lines = resp.text.strip().splitlines()
        # Поддержка разных форматов ключей
        keys = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith(("vless://", "vmess://", "trojan://", "ss://")) or 
                       "://" in line):  # Для подписок в base64
                keys.append(line)
        return keys
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []


def check_source(source_name, url):
    """Проверяет один источник"""
    print(f"Checking {source_name}...")
    keys = fetch_keys(url)
    if not keys:
        print(f"No keys found for {source_name}")
        return {"source": source_name, "total": 0, "working": [], "best": None}
    
    print(f"Loaded {len(keys)} keys from {source_name}")
    
    working = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(test_key, key): key for key in keys}
        for future in as_completed(futures):
            result = future.result()
            if result:
                working.append(result)
    
    working.sort(key=lambda x: x["latency_ms"])
    
    print(f"Working keys for {source_name}: {len(working)}/{len(keys)}")
    
    return {
        "source": source_name,
        "total": len(keys),
        "working": working[:20],  # Сохраняем только топ-20
        "best": working[0] if working else None
    }


def main():
    """Главная функция"""
    print("Starting VPN Key Auto-Checker...")
    print(f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Создаем папку output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Проверяем все источники
    results = {}
    all_working_keys = []
    
    for source_name, url in KEY_SOURCES.items():
        result = check_source(source_name, url)
        results[source_name] = result
        if result["working"]:
            all_working_keys.extend(result["working"])
    
    # Сортируем все рабочие ключи
    all_working_keys.sort(key=lambda x: x["latency_ms"])
    
    # Сохраняем результаты
    output = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_sources": len(KEY_SOURCES),
        "total_working_keys": len(all_working_keys),
        "best_key": all_working_keys[0] if all_working_keys else None,
        "top_50_keys": all_working_keys[:50],
        "sources": results
    }
    
    # Сохраняем JSON
    with open(os.path.join(OUTPUT_DIR, "working_keys.json"), "w") as f:
        json.dump(output, f, indent=2)
    
    # Сохраняем все рабочие ключи в TXT
    with open(os.path.join(OUTPUT_DIR, "all_working_keys.txt"), "w") as f:
        for key in all_working_keys:
            f.write(key["key"] + "\n")
    
    # Сохраняем лучший ключ
    if all_working_keys:
        with open(os.path.join(OUTPUT_DIR, "best_key.txt"), "w") as f:
            f.write(all_working_keys[0]["key"])
    
    # Создаем отдельные файлы для каждого источника
    for source_name, result in results.items():
        if result["working"]:
            filename = os.path.join(OUTPUT_DIR, f"{source_name}_working.txt")
            with open(filename, "w") as f:
                for key in result["working"]:
                    f.write(key["key"] + "\n")
    
    print(f"\n=== RESULTS ===")
    print(f"Total sources checked: {len(KEY_SOURCES)}")
    print(f"Total working keys: {len(all_working_keys)}")
    if all_working_keys:
        print(f"Best key: {all_working_keys[0]['host']}:{all_working_keys[0]['port']} ({all_working_keys[0]['latency_ms']} ms)")
    print(f"Results saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()

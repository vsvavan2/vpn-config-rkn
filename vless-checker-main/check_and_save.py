#!/usr/bin/env python3
import re
import requests
import socket
import time
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

BLACK_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS.txt"
BLACK_MOBILE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS_mobile.txt"
WHITE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt"

MAX_WORKERS = 20
TEST_TIMEOUT = 5
MAX_LATENCY_MS = 2000

COUNTRIES = {
    "baltics":     ["lithuania", "estonia", "latvia"],
    "finland":     ["finland"],
    "germany":     ["germany"],
    "sweden":      ["sweden"],
    "netherlands": ["netherlands"],
    "poland":      ["poland"],
}

COUNTRIES_ALL_KEYWORDS = [kw for kws in COUNTRIES.values() for kw in kws]

SKIP_COUNTRY_NAMES = {"anycast", "anycast-ip", "unknown"}



def parse_country_from_key(key):
    """Returns (country_name, flag_emoji) parsed from the key's URL fragment."""
    if '#' not in key:
        return None, None
    from urllib.parse import unquote
    fragment = unquote(key.split('#', 1)[1])
    match = re.search(
        r'([A-Z][A-Za-z\u00C0-\u017E](?:[A-Za-z\u00C0-\u017E\s\-]*[A-Za-z\u00C0-\u017E])?)(?:\s*[,|])',
        fragment
    )
    if not match:
        return None, None
    country = match.group(1).strip()
    flag = fragment[:match.start()].strip()
    return country, flag


def fetch_keys(url):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    lines = resp.text.strip().splitlines()
    return [line.strip() for line in lines if line.strip().startswith("vless://")]


def filter_keys(keys, mode):
    if mode in COUNTRIES:
        keywords = COUNTRIES[mode]
        return [k for k in keys if any(kw in k.lower() for kw in keywords)]
    if mode == "other":
        return [k for k in keys if not any(kw in k.lower() for kw in COUNTRIES_ALL_KEYWORDS) and "russia" not in k.lower()]
    if mode == "russia":
        return [k for k in keys if "russia" in k.lower()]
    if mode.startswith("w_"):
        country = mode[2:]
        if country in COUNTRIES:
            keywords = COUNTRIES[country]
            return [k for k in keys if any(kw in k.lower() for kw in keywords)]
        if country == "other":
            return [k for k in keys if not any(kw in k.lower() for kw in COUNTRIES_ALL_KEYWORDS) and "russia" not in k.lower()]
    return keys


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


def check_mode(keys, old_first_seen=None):
    if old_first_seen is None:
        old_first_seen = {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    working = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(test_key, key): key for key in keys}
        for future in as_completed(futures):
            result = future.result()
            if result:
                working.append(result)

    working.sort(key=lambda x: x["latency_ms"])

    for r in working:
        r["first_seen"] = old_first_seen.get(r["key"], now)

    return {
        "best": working[0]["key"] if working else None,
        "top10": working[:10],
        "total_working": len(working),
        "total": len(keys),
    }


def load_old_first_seen():
    try:
        with open("docs/keys.json", "r", encoding="utf-8") as f:
            old = json.load(f)
        seen = {}
        for mode_data in old.values():
            top_key = "top10" if "top10" in mode_data else "top5"
            if isinstance(mode_data, dict) and top_key in mode_data:
                for entry in mode_data[top_key]:
                    if "key" in entry and "first_seen" in entry:
                        seen[entry["key"]] = entry["first_seen"]
        return seen
    except Exception:
        return {}


def main():
    old_first_seen = load_old_first_seen()

    print("Загружаем BLACK ключи...")
    black_keys = fetch_keys(BLACK_URL)
    print(f"Загружено {len(black_keys)} BLACK ключей")

    print("Загружаем BLACK mobile ключи...")
    black_mobile_keys = fetch_keys(BLACK_MOBILE_URL)
    print(f"Загружено {len(black_mobile_keys)} BLACK mobile ключей")
    black_keys = list(dict.fromkeys(black_keys + black_mobile_keys))
    print(f"Итого уникальных BLACK ключей: {len(black_keys)}")

    print("Загружаем WHITE ключи...")
    white_keys = fetch_keys(WHITE_URL)
    print(f"Загружено {len(white_keys)} WHITE ключей")

    results = {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }

    for country in list(COUNTRIES.keys()):
        filtered = filter_keys(black_keys, country)
        print(f"[{country}] {len(filtered)} ключей, проверяем...")
        results[country] = check_mode(filtered, old_first_seen)
        print(f"[{country}] Рабочих: {results[country]['total_working']}/{results[country]['total']}")

    other_keys = filter_keys(black_keys, "other")
    print(f"[other] {len(other_keys)} ключей, группируем по странам...")
    country_groups = defaultdict(list)
    country_flags = {}
    for key in other_keys:
        name, flag = parse_country_from_key(key)
        if not name or name.lower() in SKIP_COUNTRY_NAMES:
            name = "Other"
            flag = "🌍"
        country_groups[name].append(key)
        if name not in country_flags:
            country_flags[name] = flag

    other_countries = {}
    for name, keys in country_groups.items():
        print(f"  [{name}] {len(keys)} ключей, проверяем...")
        checked = check_mode(keys, old_first_seen)
        print(f"  [{name}] Рабочих: {checked['total_working']}/{checked['total']}")
        checked["flag"] = country_flags[name]
        other_countries[name] = checked
    results["other_countries"] = other_countries

    for mode in ("w_baltics", "w_finland", "w_germany", "w_sweden", "w_netherlands", "w_poland", "w_other", "russia"):
        filtered = filter_keys(white_keys, mode)
        print(f"[{mode}] {len(filtered)} ключей, проверяем...")
        results[mode] = check_mode(filtered, old_first_seen)
        print(f"[{mode}] Рабочих: {results[mode]['total_working']}/{results[mode]['total']}")

    os.makedirs("docs", exist_ok=True)
    with open("docs/keys.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("Сохранено в docs/keys.json")


if __name__ == "__main__":
    main()

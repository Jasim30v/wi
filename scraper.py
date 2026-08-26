#!/usr/bin/env python3
import os
import requests
import zipfile
import subprocess
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "app/src/main/assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def scrape_wordlists():
    """جلب أحدث قوائم كلمات المرور من GitHub"""
    urls = {
        "rockyou.txt": "https://raw.githubusercontent.com/brannondorsey/naive-hashcat/master/rockyou.txt",
        "10m_passwords.txt": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt",
        "wpa_handshakes.txt": "https://raw.githubusercontent.com/OpenSecurityResearch/wordlists/main/wpa_handshake.txt"
    }
    for name, url in urls.items():
        try:
            print(f"[SCRAPER] جاري تحميل: {name}")
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                path = os.path.join(ASSETS_DIR, name)
                with open(path, "wb") as f:
                    f.write(resp.content)
                print(f"[+] تم حفظ: {path}")
            else:
                print(f"[-] فشل تحميل {name}")
        except Exception as e:
            print(f"[!] خطأ في {name}: {e}")

def scrape_tools():
    """جلب أدوات هجوم إضافية (ثنائيات ARM)"""
    tools = {
        "aircrack-ng": "https://github.com/aircrack-ng/aircrack-ng/releases/download/1.7/aircrack-ng-1.7-android-arm64.zip",
        "bettercap": "https://github.com/bettercap/bettercap/releases/latest/download/bettercap_android_arm64.tar.gz"
    }
    for name, url in tools.items():
        try:
            print(f"[SCRAPER] جاري جلب: {name}")
            resp = requests.get(url, timeout=60)
            if resp.status_code == 200:
                zip_path = os.path.join(ASSETS_DIR, f"{name}.zip")
                with open(zip_path, "wb") as f:
                    f.write(resp.content)
                # فك الضغط
                if zip_path.endswith(".zip"):
                    with zipfile.ZipFile(zip_path, 'r') as z:
                        z.extractall(ASSETS_DIR)
                elif zip_path.endswith(".tar.gz"):
                    subprocess.run(f"tar -xzf {zip_path} -C {ASSETS_DIR}", shell=True)
                os.remove(zip_path)
                print(f"[+] تم تثبيت {name}")
        except Exception as e:
            print(f"[!] خطأ في {name}: {e}")

def scrape_cves():
    """جلب أحدث ثغرات 0-day من NVD"""
    try:
        url = "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=wifi&resultsPerPage=10"
        resp = requests.get(url, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            cve_list = []
            for item in data.get("vulnerabilities", []):
                cve = item.get("cve", {})
                cve_list.append({
                    "id": cve.get("id"),
                    "description": cve.get("descriptions", [{}])[0].get("value"),
                    "score": cve.get("metrics", {}).get("cvssMetricV31", [{}])[0].get("cvssData", {}).get("baseScore")
                })
            with open(os.path.join(ASSETS_DIR, "latest_cves.json"), "w") as f:
                json.dump(cve_list, f, indent=2)
            print("[+] تم جلب آخر الثغرات")
    except Exception as e:
        print(f"[!] فشل جلب CVEs: {e}")

if __name__ == "__main__":
    print("[SCRAPER] بدء الجمع...")
    scrape_wordlists()
    scrape_tools()
    scrape_cves()
    print("[SCRAPER] انتهى الجمع.")

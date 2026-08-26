#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  📡 WiFi Network Scraper Pro - Advanced Scanner            ║
║     Real Network Discovery & Analysis Tool                 ║
║                                                            ║
║  🔍 Scan & Display Nearby WiFi Networks                   ║
║  📊 Signal Strength Analysis                              ║
║  🔐 Encryption Detection                                  ║
║  📍 Location-Based Scanning                               ║
║  📱 Export Results (JSON/CSV/TXT)                        ║
║  🎯 Target Selection & Password Testing                   ║
║                                                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import csv
import time
import platform
import subprocess
import argparse
import threading
import signal
import math
import re
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional, Tuple

# ============================================
# 🎨 ANSI Colors for Terminal
# ============================================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

# ============================================
# 📡 Network Data Structure
# ============================================
class WiFiNetwork:
    def __init__(self, ssid: str, bssid: str, signal: int, channel: int, 
                 encryption: str, frequency: float, capabilities: str = ""):
        self.ssid = ssid
        self.bssid = bssid
        self.signal = signal
        self.channel = channel
        self.encryption = encryption
        self.frequency = frequency
        self.capabilities = capabilities
        self.timestamp = datetime.now().isoformat()
        self.password_found = None
        
    def signal_strength_label(self) -> str:
        """Convert signal percentage to label"""
        if self.signal >= 80:
            return "Excellent"
        elif self.signal >= 60:
            return "Good"
        elif self.signal >= 40:
            return "Fair"
        elif self.signal >= 20:
            return "Weak"
        else:
            return "Very Weak"
    
    def security_level(self) -> str:
        """Get security level based on encryption"""
        if "WPA3" in self.encryption:
            return "🔒 Strong"
        elif "WPA2" in self.encryption:
            return "🔐 Good"
        elif "WPA" in self.encryption:
            return "🔓 Fair"
        elif "WEP" in self.encryption:
            return "⚠️ Weak"
        else:
            return "🔓 Open"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export"""
        return {
            "ssid": self.ssid,
            "bssid": self.bssid,
            "signal": self.signal,
            "signal_strength": self.signal_strength_label(),
            "channel": self.channel,
            "frequency": self.frequency,
            "encryption": self.encryption,
            "security_level": self.security_level(),
            "capabilities": self.capabilities,
            "password_found": self.password_found,
            "timestamp": self.timestamp
        }

# ============================================
# 🖥️ Display Functions
# ============================================
def print_banner():
    """Print beautiful banner"""
    banner = f"""
{Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   {Colors.BRIGHT_GREEN}📡 WiFi Network Scraper Pro{Colors.BRIGHT_CYAN}                          ║
║   {Colors.BRIGHT_MAGENTA}Advanced Network Discovery & Analysis{Colors.BRIGHT_CYAN}             ║
║                                                              ║
║   {Colors.BRIGHT_YELLOW}🔍 Real-Time Scanning{Colors.BRIGHT_CYAN}                                  ║
║   {Colors.BRIGHT_YELLOW}📊 Signal Analysis{Colors.BRIGHT_CYAN}                                    ║
║   {Colors.BRIGHT_YELLOW}🔐 Security Detection{Colors.BRIGHT_CYAN}                                 ║
║   {Colors.BRIGHT_YELLOW}💀 Password Testing{Colors.BRIGHT_CYAN}                                     ║
║   {Colors.BRIGHT_YELLOW}📱 Export Results{Colors.BRIGHT_CYAN}                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(banner)

def print_network_table(networks: List[WiFiNetwork]):
    """Print networks in a formatted table"""
    if not networks:
        print(f"\n{Colors.BRIGHT_RED}❌ No networks found!{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}💡 Try moving closer to WiFi sources or check permissions{Colors.RESET}")
        return
    
    print(f"\n{Colors.BRIGHT_GREEN}📡 Found {len(networks)} Networks:{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{'='*110}{Colors.RESET}")
    
    # Header
    header = f"{Colors.BOLD}{Colors.BRIGHT_WHITE}"
    header += f"{'#':<4} {'SSID':<28} {'BSSID':<20} {'Signal':<12} {'Channel':<10} {'Encryption':<15} {'Security':<12}"
    header += f"{Colors.RESET}"
    print(header)
    print(f"{Colors.BRIGHT_CYAN}{'-'*110}{Colors.RESET}")
    
    # Sort by signal strength
    sorted_networks = sorted(networks, key=lambda x: x.signal, reverse=True)
    
    for idx, net in enumerate(sorted_networks, 1):
        # Color code based on signal strength
        if net.signal >= 70:
            signal_color = Colors.BRIGHT_GREEN
        elif net.signal >= 40:
            signal_color = Colors.BRIGHT_YELLOW
        else:
            signal_color = Colors.BRIGHT_RED
        
        # Color code based on security
        if "WPA3" in net.encryption:
            security_color = Colors.BRIGHT_GREEN
        elif "WPA2" in net.encryption:
            security_color = Colors.GREEN
        elif "WPA" in net.encryption:
            security_color = Colors.YELLOW
        elif "WEP" in net.encryption:
            security_color = Colors.RED
        else:
            security_color = Colors.BRIGHT_RED
        
        # Signal bars
        bars = "▂▄▆█"[:min(4, math.ceil(net.signal / 25))]
        signal_display = f"{net.signal:>3}% {bars}"
        
        # Password indicator
        pwd_indicator = ""
        if net.password_found:
            pwd_indicator = f" {Colors.BRIGHT_GREEN}🔑{Colors.RESET}"
        
        print(f"{Colors.BRIGHT_WHITE}{idx:<4} {Colors.BRIGHT_CYAN}{net.ssid[:27]:<28} "
              f"{Colors.WHITE}{net.bssid:<20} "
              f"{signal_color}{signal_display:<12}{Colors.RESET} "
              f"{Colors.BRIGHT_BLUE}{net.channel:<10}{Colors.RESET} "
              f"{Colors.BRIGHT_MAGENTA}{net.encryption:<15}{Colors.RESET} "
              f"{security_color}{net.security_level():<12}{Colors.RESET}{pwd_indicator}")
    
    print(f"{Colors.BRIGHT_CYAN}{'='*110}{Colors.RESET}")

def print_statistics(networks: List[WiFiNetwork]):
    """Print network statistics"""
    if not networks:
        return
    
    print(f"\n{Colors.BRIGHT_CYAN}📊 Network Statistics:{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{'-'*50}{Colors.RESET}")
    
    # Total networks
    total = len(networks)
    
    # Average signal
    avg_signal = sum(n.signal for n in networks) / total
    
    # Encryption distribution
    enc_dist = defaultdict(int)
    for n in networks:
        enc_dist[n.encryption] += 1
    
    # Channel distribution
    channel_dist = defaultdict(int)
    for n in networks:
        channel_dist[n.channel] += 1
    
    # Strongest network
    strongest = max(networks, key=lambda x: x.signal)
    
    # Weakest network
    weakest = min(networks, key=lambda x: x.signal)
    
    print(f"{Colors.BRIGHT_WHITE}📡 Total Networks: {Colors.BRIGHT_GREEN}{total}{Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}📶 Average Signal: {Colors.BRIGHT_YELLOW}{avg_signal:.1f}%{Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}🔝 Strongest: {Colors.BRIGHT_GREEN}{strongest.ssid} ({strongest.signal}%){Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}🔻 Weakest: {Colors.BRIGHT_RED}{weakest.ssid} ({weakest.signal}%){Colors.RESET}")
    
    print(f"\n{Colors.BRIGHT_WHITE}🔐 Encryption Distribution:{Colors.RESET}")
    for enc, count in sorted(enc_dist.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {enc:<10} {count:>3} ({percentage:>5.1f}%) {Colors.BRIGHT_CYAN}{bar}{Colors.RESET}")
    
    print(f"\n{Colors.BRIGHT_WHITE}📡 Channel Distribution:{Colors.RESET}")
    for channel, count in sorted(channel_dist.items()):
        print(f"  Channel {channel}: {count} networks")

# ============================================
# 📡 Network Scanning Functions
# ============================================
def scan_windows() -> List[WiFiNetwork]:
    """Scan networks on Windows"""
    networks = []
    try:
        # Use netsh to get network list
        result = subprocess.run(
            ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        
        if result.returncode == 0:
            current_ssid = None
            current_bssid = None
            current_signal = 0
            current_channel = 0
            current_encryption = ""
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if line.startswith('SSID'):
                    current_ssid = line.split(':', 1)[1].strip()
                elif line.startswith('BSSID') and current_ssid:
                    current_bssid = line.split(':', 1)[1].strip()
                elif line.startswith('Signal') and current_ssid:
                    try:
                        signal_str = line.split(':', 1)[1].strip().replace('%', '')
                        current_signal = int(signal_str)
                    except:
                        current_signal = 0
                elif line.startswith('Channel') and current_ssid:
                    try:
                        channel_str = line.split(':', 1)[1].strip()
                        current_channel = int(channel_str)
                    except:
                        current_channel = 0
                elif line.startswith('Authentication') and current_ssid:
                    current_encryption = line.split(':', 1)[1].strip()
                elif line.startswith('Radio type') and current_ssid and current_bssid:
                    # We have all info for this network
                    freq = 2.4 if current_channel <= 14 else 5.0
                    
                    # Deduplicate by BSSID
                    if current_bssid and not any(n.bssid == current_bssid for n in networks):
                        networks.append(WiFiNetwork(
                            ssid=current_ssid if current_ssid else "<Hidden>",
                            bssid=current_bssid,
                            signal=current_signal,
                            channel=current_channel,
                            encryption=current_encryption if current_encryption else "Unknown",
                            frequency=freq
                        ))
                    current_ssid = None
                    current_bssid = None
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Error scanning Windows networks: {e}{Colors.RESET}")
    
    return networks

def scan_linux() -> List[WiFiNetwork]:
    """Scan networks on Linux"""
    networks = []
    try:
        # Try using iwlist first
        result = subprocess.run(
            ['sudo', 'iwlist', 'scan'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        
        if result.returncode == 0:
            current_ssid = None
            current_bssid = None
            current_signal = 0
            current_channel = 0
            current_encryption = ""
            current_freq = 0
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if 'Cell' in line and 'Address' in line:
                    # Save previous network if exists
                    if current_bssid and not any(n.bssid == current_bssid for n in networks):
                        networks.append(WiFiNetwork(
                            ssid=current_ssid or "<Hidden>",
                            bssid=current_bssid,
                            signal=current_signal,
                            channel=current_channel,
                            encryption=current_encryption or "Unknown",
                            frequency=current_freq or 2.4
                        ))
                    current_bssid = line.split('Address:')[1].strip()
                    current_ssid = None
                    current_signal = 0
                    current_channel = 0
                    current_encryption = ""
                    current_freq = 0
                elif 'ESSID' in line:
                    current_ssid = line.split('ESSID:')[1].strip().strip('"')
                elif 'Quality' in line and 'Signal level' in line:
                    try:
                        signal_str = line.split('Signal level=')[1].split()[0]
                        if '/' in signal_str:
                            num, den = signal_str.split('/')
                            current_signal = int((int(num) / int(den)) * 100)
                        elif 'dBm' in signal_str:
                            dbm = int(signal_str.replace('dBm', ''))
                            # Convert dBm to percentage (approximate)
                            current_signal = max(0, min(100, (dbm + 90) * 2))
                    except:
                        current_signal = 0
                elif 'Frequency' in line:
                    try:
                        freq_str = line.split(':')[1].strip().split()[0]
                        current_freq = float(freq_str)
                        current_channel = int(current_freq / 5) if current_freq > 4 else int(current_freq / 2.4)
                    except:
                        current_freq = 2.4
                        current_channel = 0
                elif 'Encryption key' in line:
                    current_encryption = line.split(':')[1].strip()
                elif 'Authentication' in line:
                    current_encryption = line.split(':')[1].strip()
            
            # Add last network
            if current_bssid and not any(n.bssid == current_bssid for n in networks):
                networks.append(WiFiNetwork(
                    ssid=current_ssid or "<Hidden>",
                    bssid=current_bssid,
                    signal=current_signal,
                    channel=current_channel,
                    encryption=current_encryption or "Unknown",
                    frequency=current_freq or 2.4
                ))
        else:
            # Try nmcli as alternative
            print(f"{Colors.BRIGHT_YELLOW}⚠️ iwlist failed, trying nmcli...{Colors.RESET}")
            result = subprocess.run(
                ['nmcli', '-f', 'SSID,BSSID,SIGNAL,CHAN,SECURITY', 'device', 'wifi', 'list'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        ssid = parts[0]
                        bssid = parts[1]
                        signal = int(parts[2]) if parts[2].isdigit() else 0
                        channel = int(parts[3]) if parts[3].isdigit() else 0
                        encryption = parts[4] if len(parts) > 4 else "Unknown"
                        
                        if bssid != "--" and not any(n.bssid == bssid for n in networks):
                            networks.append(WiFiNetwork(
                                ssid=ssid if ssid != "--" else "<Hidden>",
                                bssid=bssid,
                                signal=signal,
                                channel=channel,
                                encryption=encryption,
                                frequency=2.4 if channel <= 14 else 5.0
                            ))
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Error scanning Linux networks: {e}{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}💡 Try running with sudo or install wireless-tools{Colors.RESET}")
    
    return networks

def scan_macos() -> List[WiFiNetwork]:
    """Scan networks on macOS"""
    networks = []
    try:
        # Use airport command (may need to symlink first)
        airport_path = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport'
        
        # Check if airport command exists
        if not os.path.exists(airport_path):
            # Try to create symlink
            try:
                os.symlink(airport_path, '/usr/local/bin/airport')
                airport_path = '/usr/local/bin/airport'
            except:
                pass
        
        result = subprocess.run(
            [airport_path, '-s'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    ssid = parts[0]
                    bssid = parts[1] if len(parts) > 1 else "N/A"
                    
                    # Parse signal (RSSI)
                    rssi = int(parts[2]) if parts[2].lstrip('-').isdigit() else -50
                    signal = max(0, min(100, (rssi + 90) * 2))
                    
                    # Parse channel and encryption
                    channel = 0
                    encryption = "Unknown"
                    for part in parts[3:]:
                        if ',' in part:
                            try:
                                channel = int(part.split(',')[0])
                            except:
                                pass
                        if 'WPA' in part.upper() or 'WEP' in part.upper():
                            encryption = part.upper()
                        elif 'NONE' in part.upper():
                            encryption = "Open"
                    
                    if bssid != "N/A" and not any(n.bssid == bssid for n in networks):
                        networks.append(WiFiNetwork(
                            ssid=ssid,
                            bssid=bssid,
                            signal=signal,
                            channel=channel,
                            encryption=encryption,
                            frequency=2.4 if channel <= 14 else 5.0
                        ))
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}Error scanning macOS networks: {e}{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}Tip: Create symlink for airport command:{Colors.RESET}")
        print(f"{Colors.BRIGHT_CYAN}sudo ln -s /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport /usr/local/bin/airport{Colors.RESET}")
    
    return networks

def scan_networks() -> List[WiFiNetwork]:
    """Detect OS and scan networks accordingly"""
    system = platform.system().lower()
    
    print(f"{Colors.BRIGHT_CYAN}🔍 Detecting OS: {Colors.BRIGHT_WHITE}{platform.system()}{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}📡 Scanning for WiFi networks...{Colors.RESET}")
    
    if system == "windows":
        return scan_windows()
    elif system == "linux":
        return scan_linux()
    elif system == "darwin":
        return scan_macos()
    else:
        print(f"{Colors.BRIGHT_RED}❌ Unsupported OS: {system}{Colors.RESET}")
        return []

# ============================================
# 💀 Password Testing Functions
# ============================================
def load_password_file(filename: str) -> List[str]:
    """Load passwords from file"""
    passwords = []
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]
        print(f"{Colors.BRIGHT_GREEN}✅ Loaded {len(passwords)} passwords from {filename}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.BRIGHT_RED}❌ Error loading password file: {e}{Colors.RESET}")
    return passwords

def test_passwords(networks: List[WiFiNetwork], passwords: List[str]) -> Dict:
    """Test passwords against networks (simulation for demo)"""
    results = {}
    
    print(f"\n{Colors.BRIGHT_YELLOW}💀 Starting password testing...{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}Targets: {len(networks)} networks, {len(passwords)} passwords{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}{'='*50}{Colors.RESET}")
    
    total_attempts = len(networks) * len(passwords)
    current_attempt = 0
    
    for network in networks:
        print(f"\n{Colors.BRIGHT_CYAN}📡 Testing {network.ssid}...{Colors.RESET}")
        
        for password in passwords:
            current_attempt += 1
            progress = (current_attempt / total_attempts) * 100
            
            # Simulate testing (in real implementation, this would attempt connection)
            time.sleep(0.01)  # Small delay for demonstration
            
            # Show progress
            print(f"\r{Colors.BRIGHT_WHITE}Progress: {progress:.1f}% - Testing: {password[:20]}...{Colors.RESET}", end='')
            
            # Simulate finding password (for demo purposes)
            if network.ssid == "Home_5G" and password == "password123":
                network.password_found = password
                results[network.bssid] = {
                    "ssid": network.ssid,
                    "password": password,
                    "success": True
                }
                print(f"\n{Colors.BRIGHT_GREEN}✅ CRACKED! {network.ssid}: {password}{Colors.RESET}")
                break
            elif network.encryption == "Open" and current_attempt % 10 == 0:
                network.password_found = ""
                results[network.bssid] = {
                    "ssid": network.ssid,
                    "password": "",
                    "success": True
                }
                print(f"\n{Colors.BRIGHT_GREEN}✅ Open network! No password needed{Colors.RESET}")
                break
    
    print(f"\n{Colors.BRIGHT_YELLOW}{'='*50}{Colors.RESET}")
    
    # Summary
    successful = sum(1 for r in results.values() if r["success"])
    print(f"\n{Colors.BRIGHT_GREEN}📊 Results: {successful}/{len(networks)} networks cracked{Colors.RESET}")
    
    return results

# ============================================
# 📁 Export Functions
# ============================================
def export_json(networks: List[WiFiNetwork], filename: str = "wifi_networks.json"):
    """Export networks to JSON file"""
    data = {
        "scan_time": datetime.now().isoformat(),
        "total_networks": len(networks),
        "networks": [net.to_dict() for net in networks]
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"{Colors.BRIGHT_GREEN}✅ Exported to {filename}{Colors.RESET}")

def export_csv(networks: List[WiFiNetwork], filename: str = "wifi_networks.csv"):
    """Export networks to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['SSID', 'BSSID', 'Signal', 'Signal Strength', 'Channel', 'Frequency', 'Encryption', 'Security Level', 'Password Found', 'Timestamp'])
        
        for net in networks:
            writer.writerow([
                net.ssid, net.bssid, net.signal, net.signal_strength_label(),
                net.channel, net.frequency, net.encryption, net.security_level(), 
                net.password_found or '', net.timestamp
            ])
    
    print(f"{Colors.BRIGHT_GREEN}✅ Exported to {filename}{Colors.RESET}")

def export_txt(networks: List[WiFiNetwork], filename: str = "wifi_networks.txt"):
    """Export networks to TXT file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"WiFi Network Scan Results\n")
        f.write(f"Scan Time: {datetime.now().isoformat()}\n")
        f.write(f"Total Networks: {len(networks)}\n")
        f.write("="*60 + "\n\n")
        
        for idx, net in enumerate(networks, 1):
            f.write(f"Network #{idx}\n")
            f.write(f"  SSID: {net.ssid}\n")
            f.write(f"  BSSID: {net.bssid}\n")
            f.write(f"  Signal: {net.signal}% ({net.signal_strength_label()})\n")
            f.write(f"  Channel: {net.channel}\n")
            f.write(f"  Frequency: {net.frequency} GHz\n")
            f.write(f"  Encryption: {net.encryption}\n")
            f.write(f"  Security Level: {net.security_level()}\n")
            if net.password_found is not None:
                f.write(f"  Password Found: {net.password_found}\n")
            f.write("-"*40 + "\n")
    
    print(f"{Colors.BRIGHT_GREEN}✅ Exported to {filename}{Colors.RESET}")

# ============================================
# 🔄 Live Monitoring
# ============================================
def live_monitor(interval: int = 5, duration: int = 60):
    """Monitor networks in real-time"""
    print(f"{Colors.BRIGHT_CYAN}🔴 Live monitoring started...{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}Interval: {interval}s, Duration: {duration}s{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}Press Ctrl+C to stop early{Colors.RESET}")
    
    start_time = time.time()
    all_networks = []
    
    try:
        while time.time() - start_time < duration:
            print(f"\n{Colors.BRIGHT_YELLOW}📡 Scanning at {datetime.now().strftime('%H:%M:%S')}...{Colors.RESET}")
            
            networks = scan_networks()
            print_network_table(networks)
            
            # Track unique networks
            for net in networks:
                if net.bssid not in [n.bssid for n in all_networks]:
                    all_networks.append(net)
                    print(f"{Colors.BRIGHT_GREEN}🆕 New network detected: {net.ssid}{Colors.RESET}")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{Colors.BRIGHT_YELLOW}⚠️ Monitoring stopped by user{Colors.RESET}")
    
    print(f"\n{Colors.BRIGHT_GREEN}📊 Monitoring Summary:{Colors.RESET}")
    print(f"{Colors.BRIGHT_WHITE}Total unique networks found: {len(all_networks)}{Colors.RESET}")
    
    return all_networks

# ============================================
# 🎯 Interactive Mode
# ============================================
def interactive_mode():
    """Interactive menu for network selection"""
    networks = scan_networks()
    
    if not networks:
        return
    
    print_network_table(networks)
    print_statistics(networks)
    
    while True:
        print(f"\n{Colors.BRIGHT_CYAN}🎯 Options:{Colors.RESET}")
        print(f"  1. Rescan networks")
        print(f"  2. Export results")
        print(f"  3. Test passwords")
        print(f"  4. Show statistics")
        print(f"  5. Exit")
        
        choice = input(f"{Colors.BRIGHT_WHITE}Select option (1-5): {Colors.RESET}").strip()
        
        if choice == "1":
            networks = scan_networks()
            print_network_table(networks)
            print_statistics(networks)
        elif choice == "2":
            print(f"\n{Colors.BRIGHT_CYAN}Export format:{Colors.RESET}")
            print(f"  1. JSON")
            print(f"  2. CSV")
            print(f"  3. TXT")
            print(f"  4. All")
            fmt = input(f"{Colors.BRIGHT_WHITE}Select format (1-4): {Colors.RESET}").strip()
            
            if fmt == "1":
                export_json(networks)
            elif fmt == "2":
                export_csv(networks)
            elif fmt == "3":
                export_txt(networks)
            elif fmt == "4":
                export_json(networks)
                export_csv(networks)
                export_txt(networks)
        elif choice == "3":
            pwd_file = input(f"{Colors.BRIGHT_WHITE}Password file path: {Colors.RESET}").strip()
            if os.path.exists(pwd_file):
                passwords = load_password_file(pwd_file)
                results = test_passwords(networks, passwords)
                
                # Update networks with results
                for net in networks:
                    if net.bssid in results and results[net.bssid]["success"]:
                        net.password_found = results[net.bssid]["password"]
                
                print_network_table(networks)
            else:
                print(f"{Colors.BRIGHT_RED}❌ File not found!{Colors.RESET}")
        elif choice == "4":
            print_statistics(networks)
        elif choice == "5":
            print(f"{Colors.BRIGHT_GREEN}👋 Goodbye!{Colors.RESET}")
            break
        else:
            print(f"{Colors.BRIGHT_RED}❌ Invalid option!{Colors.RESET}")

# ============================================
# 🎯 Main Function
# ============================================
def main():
    parser = argparse.ArgumentParser(description='WiFi Network Scraper Pro')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('-l', '--live', action='store_true', help='Live monitoring mode')
    parser.add_argument('-t', '--interval', type=int, default=5, help='Scan interval in seconds (for live mode)')
    parser.add_argument('-d', '--duration', type=int, default=60, help='Duration in seconds (for live mode)')
    parser.add_argument('-e', '--export', choices=['json', 'csv', 'txt', 'all'], help='Export format')
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('-p', '--passwords', help='Password file for testing')
    parser.add_argument('-s', '--sort', choices=['signal', 'ssid', 'channel'], default='signal', help='Sort networks by')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print_banner()
    
    try:
        if args.interactive:
            interactive_mode()
        elif args.live:
            networks = live_monitor(args.interval, args.duration)
            if args.export and networks:
                if args.export == 'json' or args.export == 'all':
                    export_json(networks, args.output or 'wifi_networks.json')
                if args.export == 'csv' or args.export == 'all':
                    export_csv(networks, args.output or 'wifi_networks.csv')
                if args.export == 'txt' or args.export == 'all':
                    export_txt(networks, args.output or 'wifi_networks.txt')
        else:
            networks = scan_networks()
            
            # Sort if requested
            if args.sort == 'ssid':
                networks.sort(key=lambda x: x.ssid.lower())
            elif args.sort == 'channel':
                networks.sort(key=lambda x: x.channel)
            else:  # signal
                networks.sort(key=lambda x: x.signal, reverse=True)
            
            print_network_table(networks)
            print_statistics(networks)
            
            # Test passwords if provided
            if args.passwords and os.path.exists(args.passwords):
                passwords = load_password_file(args.passwords)
                results = test_passwords(networks, passwords)
                
                # Update networks with results
                for net in networks:
                    if net.bssid in results and results[net.bssid]["success"]:
                        net.password_found = results[net.bssid]["password"]
                
                print_network_table(networks)
            
            # Export if requested
            if args.export:
                if args.export == 'json' or args.export == 'all':
                    export_json(networks, args.output or 'wifi_networks.json')
                if args.export == 'csv' or args.export == 'all':
                    export_csv(networks, args.output or 'wifi_networks.csv')
                if args.export == 'txt' or args.export == 'all':
                    export_txt(networks, args.output or 'wifi_networks.txt')
            
            # Verbose output
            if args.verbose and networks:
                print(f"\n{Colors.BRIGHT_CYAN}🔍 Verbose Network Details:{Colors.RESET}")
                for net in networks:
                    print(f"\n{Colors.BRIGHT_WHITE}Network: {net.ssid}{Colors.RESET}")
                    print(f"  {Colors.DIM}BSSID: {net.bssid}{Colors.RESET}")
                    print(f"  {Colors.DIM}Capabilities: {net.capabilities}{Colors.RESET}")
                    print(f"  {Colors.DIM}Timestamp: {net.timestamp}{Colors.RESET}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.BRIGHT_YELLOW}⚠️ Scan interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.BRIGHT_RED}❌ Error: {e}{Colors.RESET}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

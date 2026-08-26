#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                                                            ║
║  📡  WiFi NETSCAN PRO - Network Scraper & Analyzer  📡    ║
║     Professional Network Scanner - Python Edition          ║
║                                                            ║
║  🌐  Real Network Discovery & Analysis                     ║
║  📊  Signal Strength Monitoring                           ║
║  🔍  Network Details Extraction                          ║
║  💾  Export to Multiple Formats                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import csv
import platform
import subprocess
import threading
import socket
import struct
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any
import argparse
from pathlib import Path

# Try to import optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  تثبيت rich للحصول على واجهة أفضل: pip install rich")

# Try to import WiFi scanning libraries
try:
    import pywifi
    from pywifi import const
    PYWIFI_AVAILABLE = True
except ImportError:
    PYWIFI_AVAILABLE = False

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False

try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False

# ═══════════════════════════════════════════════════════════
# 📡 CONFIGURATION & CONSTANTS
# ═══════════════════════════════════════════════════════════

class NetworkScannerConfig:
    """Configuration class for the network scanner"""
    
    # Scan settings
    DEFAULT_TIMEOUT = 5
    MAX_RETRIES = 3
    SCAN_INTERVAL = 2  # seconds between scans
    
    # Output settings
    OUTPUT_FORMATS = ['json', 'csv', 'txt', 'html']
    DEFAULT_OUTPUT = 'json'
    
    # Color codes for terminal
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m'
    }
    
    # Security types
    SECURITY_TYPES = {
        0: 'Open',
        1: 'WEP',
        2: 'WPA',
        3: 'WPA2',
        4: 'WPA3',
        5: 'WPA/WPA2',
        6: 'Enterprise',
        7: 'Unknown'
    }
    
    # Frequency bands
    FREQUENCY_BANDS = {
        '2.4 GHz': list(range(1, 15)),
        '5 GHz': [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165],
        '6 GHz': [1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 93, 97, 101, 105, 109, 113, 117, 121, 125, 129, 133, 137, 141, 145, 149, 153, 157, 161, 165, 169, 173, 177, 181, 185, 189, 193, 197, 201, 205, 209, 213, 217, 221, 225, 229, 233]
    }

# ═══════════════════════════════════════════════════════════
# 📡 NETWORK DATA MODELS
# ═══════════════════════════════════════════════════════════

class NetworkInfo:
    """Network information data class"""
    
    def __init__(self):
        self.ssid: str = ""
        self.bssid: str = ""
        self.signal: int = 0
        self.frequency: str = ""
        self.channel: int = 0
        self.security: str = "Unknown"
        self.encryption: str = ""
        self.max_speed: str = ""
        self.vendor: str = "Unknown"
        self.first_seen: str = ""
        self.last_seen: str = ""
        self.is_hidden: bool = False
        self.connected: bool = False
        self.ip_address: str = ""
        self.gateway: str = ""
        self.subnet: str = ""
        self.dns_servers: List[str] = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'ssid': self.ssid,
            'bssid': self.bssid,
            'signal': self.signal,
            'frequency': self.frequency,
            'channel': self.channel,
            'security': self.security,
            'encryption': self.encryption,
            'max_speed': self.max_speed,
            'vendor': self.vendor,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'is_hidden': self.is_hidden,
            'connected': self.connected,
            'ip_address': self.ip_address,
            'gateway': self.gateway,
            'subnet': self.subnet,
            'dns_servers': self.dns_servers
        }
    
    def __str__(self) -> str:
        """String representation"""
        security_icon = '🔓' if self.security == 'Open' else '🔒'
        signal_bars = '▂▄▆█'[:max(1, min(4, self.signal // 25))]
        return f"{security_icon} {self.ssid:<30} {signal_bars:<4} {self.signal}%  {self.frequency:<8} Ch:{self.channel:<3} {self.security}"

# ═══════════════════════════════════════════════════════════
# 📡 NETWORK SCANNER CORE
# ═══════════════════════════════════════════════════════════

class NetworkScanner:
    """Main network scanner class"""
    
    def __init__(self, config: Optional[NetworkScannerConfig] = None):
        self.config = config or NetworkScannerConfig()
        self.networks: Dict[str, NetworkInfo] = {}
        self.scan_history: List[Dict[str, Any]] = []
        self.is_scanning = False
        self.scan_thread = None
        self.current_network = self._get_current_network_info()
        
        # Initialize rich console if available
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
            
        # Detect platform
        self.platform = platform.system()
        self._detect_capabilities()
        
    def _detect_capabilities(self):
        """Detect available scanning capabilities"""
        self.capabilities = {
            'pywifi': PYWIFI_AVAILABLE,
            'nmap': NMAP_AVAILABLE,
            'netifaces': NETIFACES_AVAILABLE,
            'system_commands': self._check_system_commands(),
            'requests': REQUESTS_AVAILABLE
        }
        
    def _check_system_commands(self) -> Dict[str, bool]:
        """Check available system commands"""
        commands = {
            'iwlist': False,
            'iw': False,
            'netsh': False,
            'airport': False,
            'nmcli': False
        }
        
        for cmd in commands:
            try:
                result = subprocess.run(['which', cmd] if self.platform != 'Windows' else ['where', cmd],
                                      capture_output=True, text=True, timeout=2)
                commands[cmd] = result.returncode == 0
            except:
                pass
                
        return commands
    
    def _get_current_network_info(self) -> NetworkInfo:
        """Get current network information"""
        info = NetworkInfo()
        
        try:
            # Try to get current WiFi connection
            if PYWIFI_AVAILABLE:
                wifi = pywifi.PyWiFi()
                iface = wifi.interfaces()[0]
                if iface.status() == const.IFACE_CONNECTED:
                    profile = iface.network_profiles()[0]
                    info.ssid = profile.ssid
                    info.connected = True
                    
            # Get IP configuration
            if NETIFACES_AVAILABLE:
                for iface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(iface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            if 'addr' in addr and not addr['addr'].startswith('127.'):
                                info.ip_address = addr['addr']
                                if 'netmask' in addr:
                                    info.subnet = addr['netmask']
                            
                    if netifaces.AF_LINK in addrs:
                        for addr in addrs[netifaces.AF_LINK]:
                            if 'addr' in addr:
                                info.bssid = addr['addr']
                                
            # Get gateway
            if self.platform == 'Linux':
                try:
                    result = subprocess.run(['ip', 'route', 'show', 'default'],
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        parts = result.stdout.split()
                        if len(parts) > 2:
                            info.gateway = parts[2]
                except:
                    pass
                    
            # Get DNS servers
            try:
                with open('/etc/resolv.conf', 'r') as f:
                    for line in f:
                        if line.startswith('nameserver'):
                            info.dns_servers.append(line.split()[1])
            except:
                pass
                
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]⚠️  خطأ في الحصول على معلومات الشبكة: {e}[/yellow]")
                
        return info
    
    def scan_networks(self, interface: Optional[str] = None) -> List[NetworkInfo]:
        """Scan for available networks"""
        self.is_scanning = True
        networks = []
        
        try:
            # Try pywifi first
            if PYWIFI_AVAILABLE:
                networks.extend(self._scan_with_pywifi())
            
            # Try system commands
            if not networks or len(networks) < 3:
                networks.extend(self._scan_with_system_commands(interface))
            
            # Try nmap for network mapping
            if NMAP_AVAILABLE:
                networks.extend(self._scan_with_nmap())
                
            # Deduplicate networks
            networks = self._deduplicate_networks(networks)
            
            # Update network database
            current_time = datetime.now().isoformat()
            for net in networks:
                if net.bssid in self.networks:
                    # Update existing network
                    self.networks[net.bssid].signal = net.signal
                    self.networks[net.bssid].last_seen = current_time
                    self.networks[net.bssid].security = net.security
                else:
                    # New network
                    net.first_seen = current_time
                    net.last_seen = current_time
                    self.networks[net.bssid] = net
                    
            # Add to history
            self.scan_history.append({
                'timestamp': current_time,
                'count': len(networks),
                'networks': [n.to_dict() for n in networks]
            })
            
        finally:
            self.is_scanning = False
            
        return networks
    
    def _scan_with_pywifi(self) -> List[NetworkInfo]:
        """Scan using pywifi library"""
        networks = []
        
        try:
            wifi = pywifi.PyWiFi()
            iface = wifi.interfaces()[0]
            iface.scan()
            time.sleep(3)  # Wait for scan results
            
            results = iface.scan_results()
            for result in results:
                net = NetworkInfo()
                net.ssid = result.ssid or "<Hidden Network>"
                net.bssid = result.bssid
                net.signal = result.signal
                net.frequency = f"{result.freq / 1000:.1f} GHz"
                net.channel = self._freq_to_channel(result.freq)
                net.security = self._parse_security(result)
                net.is_hidden = result.ssid == ""
                
                networks.append(net)
                
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]⚠️  pywifi scan failed: {e}[/yellow]")
                
        return networks
    
    def _scan_with_system_commands(self, interface: Optional[str] = None) -> List[NetworkInfo]:
        """Scan using system commands"""
        networks = []
        
        try:
            if self.platform == 'Linux':
                # Try iwlist
                if self.config.capabilities['system_commands'].get('iwlist', False):
                    cmd = ['iwlist', 'scan']
                    if interface:
                        cmd = ['iwlist', interface, 'scan']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config.DEFAULT_TIMEOUT)
                    networks.extend(self._parse_iwlist_output(result.stdout))
                
                # Try iw
                if self.config.capabilities['system_commands'].get('iw', False):
                    cmd = ['iw', 'dev', 'scan']
                    if interface:
                        cmd = ['iw', 'dev', interface, 'scan']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.config.DEFAULT_TIMEOUT)
                    networks.extend(self._parse_iw_output(result.stdout))
                
                # Try nmcli
                if self.config.capabilities['system_commands'].get('nmcli', False):
                    result = subprocess.run(['nmcli', '-t', '-f', 'SSID,BSSID,SIGNAL,FREQ,SECURITY', 'dev', 'wifi', 'list'],
                                          capture_output=True, text=True, timeout=self.config.DEFAULT_TIMEOUT)
                    networks.extend(self._parse_nmcli_output(result.stdout))
                    
            elif self.platform == 'Windows':
                # Use netsh
                if self.config.capabilities['system_commands'].get('netsh', False):
                    result = subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                                          capture_output=True, text=True, timeout=self.config.DEFAULT_TIMEOUT)
                    networks.extend(self._parse_netsh_output(result.stdout))
                    
            elif self.platform == 'Darwin':  # macOS
                # Use airport
                if self.config.capabilities['system_commands'].get('airport', False):
                    result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                                          capture_output=True, text=True, timeout=self.config.DEFAULT_TIMEOUT)
                    networks.extend(self._parse_airport_output(result.stdout))
                    
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]⚠️  System command scan failed: {e}[/yellow]")
                
        return networks
    
    def _scan_with_nmap(self) -> List[NetworkInfo]:
        """Scan using nmap for network mapping"""
        networks = []
        
        try:
            nm = nmap.PortScanner()
            # Get local network range
            if self.current_network.ip_address and self.current_network.subnet:
                network_range = self._get_network_range(
                    self.current_network.ip_address,
                    self.current_network.subnet
                )
                if network_range:
                    nm.scan(hosts=network_range, arguments='-sn -T4')
                    
                    for host in nm.all_hosts():
                        net = NetworkInfo()
                        net.bssid = nm[host].get('addresses', {}).get('mac', 'Unknown')
                        net.ip_address = host
                        net.vendor = nm[host].get('vendor', {}).get(net.bssid, 'Unknown')
                        net.connected = True
                        networks.append(net)
                        
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]⚠️  nmap scan failed: {e}[/yellow]")
                
        return networks
    
    def _deduplicate_networks(self, networks: List[NetworkInfo]) -> List[NetworkInfo]:
        """Remove duplicate networks"""
        seen = {}
        unique = []
        
        for net in networks:
            key = net.bssid or net.ssid
            if key not in seen:
                seen[key] = net
                unique.append(net)
            else:
                # Update with better signal
                if net.signal > seen[key].signal:
                    seen[key].signal = net.signal
                    
        return list(seen.values())
    
    def _freq_to_channel(self, freq: int) -> int:
        """Convert frequency to channel number"""
        if 2400 <= freq <= 2500:
            return (freq - 2407) // 5
        elif 5000 <= freq <= 5900:
            return (freq - 5000) // 5
        return 0
    
    def _parse_security(self, result) -> str:
        """Parse security type from scan result"""
        try:
            if hasattr(result, 'akm'):
                akm = result.akm
                if const.AKM_TYPE_WPA2PSK in akm:
                    return 'WPA2'
                elif const.AKM_TYPE_WPAPSK in akm:
                    return 'WPA'
                elif const.AKM_TYPE_WPA2ENT in akm:
                    return 'WPA2-Enterprise'
                elif const.AKM_TYPE_WPA3 in akm:
                    return 'WPA3'
                elif len(akm) == 0:
                    return 'Open'
            return 'Unknown'
        except:
            return 'Unknown'
    
    def _parse_iwlist_output(self, output: str) -> List[NetworkInfo]:
        """Parse iwlist scan output"""
        networks = []
        current = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if 'Cell' in line and 'Address' in line:
                if current:
                    networks.append(current)
                current = NetworkInfo()
                current.bssid = line.split('Address:')[1].strip()
                
            elif current and 'ESSID' in line:
                essid = line.split('ESSID:')[1].strip().strip('"')
                current.ssid = essid if essid else '<Hidden Network>'
                current.is_hidden = essid == ''
                
            elif current and 'Signal level' in line:
                try:
                    signal_str = line.split('Signal level=')[1].split()[0]
                    if 'dBm' in line:
                        dbm = int(signal_str)
                        current.signal = self._dbm_to_percent(dbm)
                    else:
                        current.signal = int(signal_str.split('/')[0])
                except:
                    pass
                    
            elif current and 'Frequency' in line:
                try:
                    freq = float(line.split(':')[1].split()[0])
                    current.frequency = f"{freq} GHz"
                    current.channel = int(line.split('Channel')[1].split(')')[0])
                except:
                    pass
                    
            elif current and 'Encryption key' in line:
                current.security = 'Open' if 'off' in line else 'Secured'
                
        if current:
            networks.append(current)
            
        return networks
    
    def _parse_iw_output(self, output: str) -> List[NetworkInfo]:
        """Parse iw scan output"""
        networks = []
        current = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith('BSS'):
                if current:
                    networks.append(current)
                current = NetworkInfo()
                current.bssid = line.split()[1].split('(')[0]
                
            elif current and line.startswith('SSID:'):
                current.ssid = line.split('SSID:')[1].strip() or '<Hidden Network>'
                current.is_hidden = current.ssid == '<Hidden Network>'
                
            elif current and line.startswith('signal:'):
                try:
                    dbm = float(line.split(':')[1].split()[0])
                    current.signal = self._dbm_to_percent(dbm)
                except:
                    pass
                    
            elif current and line.startswith('freq:'):
                try:
                    freq = float(line.split(':')[1])
                    current.frequency = f"{freq/1000:.1f} GHz"
                except:
                    pass
                    
            elif current and 'RSN:' in line:
                current.security = 'WPA2'
            elif current and 'WPA:' in line:
                current.security = 'WPA'
                
        if current:
            networks.append(current)
            
        return networks
    
    def _parse_nmcli_output(self, output: str) -> List[NetworkInfo]:
        """Parse nmcli output"""
        networks = []
        
        for line in output.split('\n'):
            if not line.strip():
                continue
                
            parts = line.split(':')
            if len(parts) >= 5:
                net = NetworkInfo()
                net.ssid = parts[0] or '<Hidden Network>'
                net.bssid = parts[1]
                try:
                    net.signal = int(parts[2])
                except:
                    net.signal = 0
                try:
                    freq = float(parts[3])
                    net.frequency = f"{freq/1000:.1f} GHz"
                except:
                    pass
                net.security = parts[4] if parts[4] else 'Open'
                networks.append(net)
                
        return networks
    
    def _parse_netsh_output(self, output: str) -> List[NetworkInfo]:
        """Parse netsh output"""
        networks = []
        current = None
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith('SSID'):
                if current:
                    networks.append(current)
                current = NetworkInfo()
                current.ssid = line.split(':')[1].strip()
                current.is_hidden = current.ssid == ''
                
            elif current and line.startswith('BSSID'):
                current.bssid = line.split(':')[1].strip()
                
            elif current and line.startswith('Signal'):
                try:
                    signal_str = line.split(':')[1].strip().replace('%', '')
                    current.signal = int(signal_str)
                except:
                    pass
                    
            elif current and line.startswith('Authentication'):
                auth = line.split(':')[1].strip()
                current.security = auth if auth != 'Open' else 'Open'
                
            elif current and line.startswith('Channel'):
                try:
                    current.channel = int(line.split(':')[1].strip())
                    current.frequency = '2.4 GHz' if current.channel <= 14 else '5 GHz'
                except:
                    pass
                    
        if current:
            networks.append(current)
            
        return networks
    
    def _parse_airport_output(self, output: str) -> List[NetworkInfo]:
        """Parse airport output"""
        networks = []
        lines = output.split('\n')[1:]  # Skip header
        
        for line in lines:
            if not line.strip():
                continue
                
            parts = line.split()
            if len(parts) >= 3:
                net = NetworkInfo()
                net.ssid = parts[0]
                net.bssid = parts[1]
                try:
                    net.signal = int(parts[2])
                except:
                    net.signal = 0
                if len(parts) > 3:
                    net.channel = int(parts[3])
                    net.frequency = '2.4 GHz' if net.channel <= 14 else '5 GHz'
                if len(parts) > 4:
                    net.security = parts[4]
                networks.append(net)
                
        return networks
    
    def _dbm_to_percent(self, dbm: int) -> int:
        """Convert dBm to percentage"""
        if dbm <= -100:
            return 0
        elif dbm >= -50:
            return 100
        else:
            return int((dbm + 100) * 2)
    
    def _get_network_range(self, ip: str, subnet: str) -> Optional[str]:
        """Get network range from IP and subnet"""
        try:
            ip_parts = list(map(int, ip.split('.')))
            subnet_parts = list(map(int, subnet.split('.')))
            
            network = [ip_parts[i] & subnet_parts[i] for i in range(4)]
            broadcast = [network[i] | (255 - subnet_parts[i]) for i in range(4)]
            
            return f"{'.'.join(map(str, network))}/{sum(bin(x).count('1') for x in subnet_parts)}"
        except:
            return None

# ═══════════════════════════════════════════════════════════
# 📡 EXPORT MANAGER
# ═══════════════════════════════════════════════════════════

class ExportManager:
    """Export scan results to different formats"""
    
    def __init__(self, scanner: NetworkScanner):
        self.scanner = scanner
        
    def export_json(self, filename: str):
        """Export to JSON"""
        data = {
            'scan_time': datetime.now().isoformat(),
            'total_networks': len(self.scanner.networks),
            'networks': [net.to_dict() for net in self.scanner.networks.values()]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def export_csv(self, filename: str):
        """Export to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['SSID', 'BSSID', 'Signal', 'Frequency', 'Channel', 'Security', 'Vendor'])
            for net in self.scanner.networks.values():
                writer.writerow([net.ssid, net.bssid, net.signal, net.frequency, net.channel, net.security, net.vendor])
                
    def export_txt(self, filename: str):
        """Export to text"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("  WiFi NETSCAN PRO - Network Scan Results\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Networks: {len(self.scanner.networks)}\n\n")
            
            for net in self.scanner.networks.values():
                f.write(f"Network: {net.ssid}\n")
                f.write(f"  BSSID: {net.bssid}\n")
                f.write(f"  Signal: {net.signal}%\n")
                f.write(f"  Frequency: {net.frequency}\n")
                f.write(f"  Channel: {net.channel}\n")
                f.write(f"  Security: {net.security}\n")
                f.write(f"  Vendor: {net.vendor}\n")
                f.write("-" * 40 + "\n")
                
    def export_html(self, filename: str):
        """Export to HTML"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WiFi NETSCAN PRO - Results</title>
            <style>
                body { font-family: Arial, sans-serif; background: #1a1a2e; color: #e0e0e0; padding: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { padding: 12px; text-align: right; border-bottom: 1px solid #333; }
                th { background: #16213e; color: #00ffcc; }
                tr:hover { background: #16213e; }
                .signal-high { color: #00ff00; }
                .signal-medium { color: #ffff00; }
                .signal-low { color: #ff0000; }
            </style>
        </head>
        <body>
            <h1>📡 WiFi NETSCAN PRO - Scan Results</h1>
            <p>Scan Time: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p>Total Networks: """ + str(len(self.scanner.networks)) + """</p>
            <table>
                <tr>
                    <th>SSID</th>
                    <th>BSSID</th>
                    <th>Signal</th>
                    <th>Frequency</th>
                    <th>Channel</th>
                    <th>Security</th>
                </tr>
        """
        
        for net in self.scanner.networks.values():
            signal_class = 'signal-high' if net.signal >= 70 else 'signal-medium' if net.signal >= 40 else 'signal-low'
            html += f"""
                <tr>
                    <td>{net.ssid}</td>
                    <td>{net.bssid}</td>
                    <td class="{signal_class}">{net.signal}%</td>
                    <td>{net.frequency}</td>
                    <td>{net.channel}</td>
                    <td>{net.security}</td>
                </tr>
            """
            
        html += """
            </table>
        </body>
        </html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def export_all(self, prefix: str = "scan_results"):
        """Export to all formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exports = {
            'json': f"{prefix}_{timestamp}.json",
            'csv': f"{prefix}_{timestamp}.csv",
            'txt': f"{prefix}_{timestamp}.txt",
            'html': f"{prefix}_{timestamp}.html"
        }
        
        self.export_json(exports['json'])
        self.export_csv(exports['csv'])
        self.export_txt(exports['txt'])
        self.export_html(exports['html'])
        
        return exports

# ═══════════════════════════════════════════════════════════
# 📡 DISPLAY MANAGER
# ═══════════════════════════════════════════════════════════

class DisplayManager:
    """Display scan results"""
    
    def __init__(self, scanner: NetworkScanner):
        self.scanner = scanner
        self.console = scanner.console if RICH_AVAILABLE else None
        
    def display_results(self, networks: List[NetworkInfo]):
        """Display scan results"""
        if self.console:
            self._display_rich(networks)
        else:
            self._display_plain(networks)
            
    def _display_rich(self, networks: List[NetworkInfo]):
        """Display using rich library"""
        table = Table(
            title="📡 WiFi NETSCAN PRO - Network Results",
            box=box.ROUNDED,
            header_style="bold cyan",
            border_style="bright_blue"
        )
        
        table.add_column("SSID", style="bold white", no_wrap=True)
        table.add_column("BSSID", style="dim")
        table.add_column("Signal", justify="center")
        table.add_column("Frequency", justify="center")
        table.add_column("Channel", justify="center")
        table.add_column("Security", justify="center")
        table.add_column("Status", justify="center")
        
        for net in networks:
            signal_style = "green" if net.signal >= 70 else "yellow" if net.signal >= 40 else "red"
            security_style = "green" if net.security == "Open" else "yellow" if "WPA" in net.security else "red"
            status = "🔗" if net.connected else ""
            
            table.add_row(
                net.ssid,
                net.bssid,
                f"[{signal_style}]{net.signal}%[/{signal_style}]",
                net.frequency,
                str(net.channel),
                f"[{security_style}]{net.security}[/{security_style}]",
                status
            )
            
        self.console.print(table)
        
    def _display_plain(self, networks: List[NetworkInfo]):
        """Display without rich library"""
        print("\n" + "=" * 70)
        print("  📡 WiFi NETSCAN PRO - Network Results")
        print("=" * 70)
        print(f"  {'SSID':<30} {'Signal':<8} {'Frequency':<10} {'Channel':<8} {'Security'}")
        print("-" * 70)
        
        for net in networks:
            signal_color = self.scanner.config.COLORS['green'] if net.signal >= 70 else \
                          self.scanner.config.COLORS['yellow'] if net.signal >= 40 else \
                          self.scanner.config.COLORS['red']
            
            print(f"  {net.ssid:<30} {signal_color}{net.signal}%{self.scanner.config.COLORS['reset']:<8} "
                  f"{net.frequency:<10} {net.channel:<8} {net.security}")
            
        print("=" * 70)

# ═══════════════════════════════════════════════════════════
# 📡 MAIN APPLICATION
# ═══════════════════════════════════════════════════════════

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="WiFi NETSCAN PRO - Professional Network Scanner")
    parser.add_argument('-i', '--interface', help='Network interface to scan')
    parser.add_argument('-o', '--output', choices=['json', 'csv', 'txt', 'html', 'all'], 
                       default='json', help='Output format')
    parser.add_argument('-f', '--filename', help='Output filename')
    parser.add_argument('-c', '--continuous', action='store_true', help='Continuous scanning mode')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Scan timeout in seconds')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--export-dir', default='scan_results', help='Export directory')
    
    args = parser.parse_args()
    
    # Initialize scanner
    config = NetworkScannerConfig()
    config.DEFAULT_TIMEOUT = args.timeout
    
    scanner = NetworkScanner(config)
    exporter = ExportManager(scanner)
    display = DisplayManager(scanner)
    
    # Print header
    if RICH_AVAILABLE:
        console = Console()
        console.print(Panel.fit(
            "[bold cyan]📡 WiFi NETSCAN PRO[/bold cyan]\n"
            "[dim]Professional Network Scanner - Python Edition[/dim]",
            border_style="cyan",
            box=box.DOUBLE
        ))
    else:
        print("""
╔══════════════════════════════════════════════════════════╗
║  📡 WiFi NETSCAN PRO - Professional Network Scanner  📡  ║
║     Python Edition - Works Offline                      ║
╚══════════════════════════════════════════════════════════╝
        """)
    
    # Check capabilities
    if args.verbose:
        print("\n📋 Available Capabilities:")
        for cap, available in scanner.capabilities.items():
            status = "✅" if available else "❌"
            print(f"  {status} {cap}")
    
    # Create export directory
    if args.output != 'all' and not args.filename:
        os.makedirs(args.export_dir, exist_ok=True)
    
    try:
        if args.continuous:
            # Continuous scanning mode
            print("\n🔄 Continuous scanning mode - Press Ctrl+C to stop\n")
            scan_count = 0
            
            while True:
                scan_count += 1
                print(f"\n📡 Scan #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                networks = scanner.scan_networks(args.interface)
                display.display_results(networks)
                
                print(f"\n✅ Found {len(networks)} networks")
                
                # Auto-export on each scan
                if args.output != 'all':
                    filename = args.filename or f"{args.export_dir}/scan_{scan_count}.{args.output}"
                    if args.output == 'json':
                        exporter.export_json(filename)
                    elif args.output == 'csv':
                        exporter.export_csv(filename)
                    elif args.output == 'txt':
                        exporter.export_txt(filename)
                    elif args.output == 'html':
                        exporter.export_html(filename)
                    
                    if args.verbose:
                        print(f"💾 Exported to: {filename}")
                
                time.sleep(config.SCAN_INTERVAL)
                
        else:
            # Single scan mode
            print("\n🔍 Scanning for networks...\n")
            
            networks = scanner.scan_networks(args.interface)
            display.display_results(networks)
            
            print(f"\n✅ Found {len(networks)} networks")
            
            # Export results
            if args.output == 'all':
                exports = exporter.export_all(args.filename or "scan_results")
                print("\n💾 Exported to:")
                for fmt, filename in exports.items():
                    print(f"  • {fmt.upper()}: {filename}")
            else:
                filename = args.filename or f"{args.export_dir}/scan_results.{args.output}"
                
                if args.output == 'json':
                    exporter.export_json(filename)
                elif args.output == 'csv':
                    exporter.export_csv(filename)
                elif args.output == 'txt':
                    exporter.export_txt(filename)
                elif args.output == 'html':
                    exporter.export_html(filename)
                    
                print(f"\n💾 Exported to: {filename}")
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Scan interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
            
    finally:
        print("\n" + "=" * 70)
        print("  ✅ Scan complete - WiFi NETSCAN PRO")
        print("=" * 70)

if __name__ == "__main__":
    main()

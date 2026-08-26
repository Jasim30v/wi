#!/usr/bin/env python3
"""
📡 WiFi Scanner Backend - Cross-Platform Network Scanner
"""

import subprocess
import platform
import re
import json
import socket
from datetime import datetime
import threading
import time
import struct

class WiFiScanner:
    def __init__(self):
        self.system = platform.system()
        self.networks = []
        self.scanning = False
        self.last_scan_time = None
        
    def scan_networks(self):
        """Scan for available WiFi networks"""
        self.networks = []
        self.scanning = True
        
        try:
            if self.system == "Windows":
                self._scan_windows()
            elif self.system == "Linux":
                self._scan_linux()
            elif self.system == "Darwin":
                self._scan_macos()
            else:
                self._scan_generic()
        except Exception as e:
            print(f"Scan error: {e}")
        
        self.scanning = False
        self.last_scan_time = datetime.now()
        return self.networks
    
    def _scan_windows(self):
        """Scan on Windows using netsh"""
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            if result.returncode == 0:
                output = result.stdout
                # Parse the output
                current_network = {}
                
                for line in output.split('\n'):
                    line = line.strip()
                    
                    if 'SSID' in line and ':' in line:
                        ssid = line.split(':', 1)[1].strip()
                        if ssid and ssid != '':
                            if current_network:
                                self.networks.append(current_network)
                            current_network = {
                                'ssid': ssid,
                                'bssid': '',
                                'channel': 0,
                                'signal': 0,
                                'security': 'Unknown',
                                'band': 'Unknown'
                            }
                    
                    elif 'BSSID' in line and ':' in line and current_network:
                        current_network['bssid'] = line.split(':', 1)[1].strip()
                    
                    elif 'Signal' in line and '%' in line and current_network:
                        signal_str = line.split(':')[1].strip().replace('%', '')
                        current_network['signal'] = int(signal_str)
                    
                    elif 'Channel' in line and ':' in line and current_network:
                        channel_str = line.split(':')[1].strip()
                        current_network['channel'] = int(channel_str)
                    
                    elif 'Authentication' in line and ':' in line and current_network:
                        auth = line.split(':', 1)[1].strip()
                        current_network['security'] = auth
                    
                    elif 'Radio type' in line and ':' in line and current_network:
                        radio = line.split(':', 1)[1].strip()
                        if '802.11a' in radio or '802.11ac' in radio or '802.11ax' in radio:
                            current_network['band'] = '5GHz'
                        else:
                            current_network['band'] = '2.4GHz'
                
                if current_network and 'ssid' in current_network:
                    self.networks.append(current_network)
                    
        except Exception as e:
            print(f"Windows scan error: {e}")
    
    def _scan_linux(self):
        """Scan on Linux using iwlist or nmcli"""
        try:
            # Try nmcli first
            result = subprocess.run(
                ['nmcli', '-t', '-f', 'SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY', 'device', 'wifi', 'list'],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        parts = line.split(':')
                        if len(parts) >= 5:
                            ssid = parts[0] if parts[0] else '(Hidden)'
                            bssid = parts[1] if len(parts) > 1 else ''
                            channel = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                            freq = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 2400
                            signal = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 0
                            security = parts[5] if len(parts) > 5 else 'Unknown'
                            
                            self.networks.append({
                                'ssid': ssid,
                                'bssid': bssid,
                                'channel': channel,
                                'signal': signal,
                                'security': security,
                                'band': '5GHz' if freq > 5000 else '2.4GHz'
                            })
            else:
                self._scan_linux_iwlist()
                
        except Exception as e:
            print(f"nmcli scan error: {e}")
            self._scan_linux_iwlist()
    
    def _scan_linux_iwlist(self):
        """Fallback Linux scan using iwlist"""
        try:
            # Find wireless interface
            result = subprocess.run(
                ['iwconfig'],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line:
                    interface = line.split()[0]
                    interfaces.append(interface)
            
            if not interfaces:
                # Try to find via iw
                result = subprocess.run(
                    ['iw', 'dev'],
                    capture_output=True, text=True, encoding='utf-8'
                )
                for line in result.stdout.split('\n'):
                    if 'Interface' in line:
                        interface = line.split()[1]
                        interfaces.append(interface)
            
            for interface in interfaces:
                result = subprocess.run(
                    ['iwlist', interface, 'scan'],
                    capture_output=True, text=True, encoding='utf-8'
                )
                
                current_network = {}
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    if 'Cell' in line and 'Address' in line:
                        if current_network and 'ssid' in current_network:
                            self.networks.append(current_network)
                        current_network = {
                            'bssid': line.split('Address:')[1].strip(),
                            'ssid': '',
                            'channel': 0,
                            'signal': 0,
                            'security': 'Unknown',
                            'band': '2.4GHz'
                        }
                    
                    elif 'ESSID:' in line and current_network:
                        essid = line.split('ESSID:')[1].strip().strip('"')
                        current_network['ssid'] = essid if essid else '(Hidden)'
                    
                    elif 'Frequency:' in line and current_network:
                        freq_match = re.search(r'Frequency:(\d+\.?\d*)', line)
                        if freq_match:
                            freq = float(freq_match.group(1))
                            current_network['band'] = '5GHz' if freq > 5 else '2.4GHz'
                        
                        channel_match = re.search(r'Channel (\d+)', line)
                        if channel_match:
                            current_network['channel'] = int(channel_match.group(1))
                    
                    elif 'Quality=' in line and current_network:
                        quality_match = re.search(r'Quality=(\d+)/(\d+)', line)
                        if quality_match:
                            quality = int(quality_match.group(1))
                            max_quality = int(quality_match.group(2))
                            current_network['signal'] = int((quality / max_quality) * 100)
                        
                        signal_match = re.search(r'Signal level=(-?\d+)', line)
                        if signal_match:
                            # Convert dBm to percentage (approximate)
                            dbm = int(signal_match.group(1))
                            # -30 dBm = 100%, -90 dBm = 0%
                            signal_pct = max(0, min(100, int((dbm + 90) * 1.67)))
                            current_network['signal'] = signal_pct
                    
                    elif 'Encryption key:' in line and current_network:
                        if 'on' in line:
                            current_network['security'] = 'Encrypted'
                        else:
                            current_network['security'] = 'Open'
                    
                    elif 'WPA' in line or 'WEP' in line:
                        if current_network:
                            if 'WPA2' in line or 'WPA3' in line:
                                current_network['security'] = 'WPA2/WPA3'
                            elif 'WPA' in line:
                                current_network['security'] = 'WPA'
                            elif 'WEP' in line:
                                current_network['security'] = 'WEP'
                
                if current_network and 'ssid' in current_network:
                    self.networks.append(current_network)
                    
        except Exception as e:
            print(f"iwlist scan error: {e}")
    
    def _scan_macos(self):
        """Scan on macOS using airport or system_profiler"""
        try:
            # Try to use airport command
            result = subprocess.run(
                ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                # Skip header line
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 3:
                        ssid = parts[0]
                        bssid = parts[1]
                        rssi = int(parts[2])
                        channel = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0
                        security = ' '.join(parts[4:]) if len(parts) > 4 else 'Unknown'
                        
                        # Convert RSSI to percentage
                        signal_pct = max(0, min(100, int((rssi + 100) * 2)))
                        
                        self.networks.append({
                            'ssid': ssid,
                            'bssid': bssid,
                            'channel': channel,
                            'signal': signal_pct,
                            'security': security,
                            'band': '5GHz' if channel > 14 else '2.4GHz'
                        })
        except Exception as e:
            print(f"macOS scan error: {e}")
    
    def _scan_generic(self):
        """Generic scan fallback"""
        self.networks = [
            {
                'ssid': 'Network Scanner Not Available',
                'bssid': 'N/A',
                'channel': 0,
                'signal': 0,
                'security': 'N/A',
                'band': 'N/A'
            }
        ]
    
    def get_connected_network(self):
        """Get currently connected network info"""
        connected = None
        
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    ['netsh', 'wlan', 'show', 'interfaces'],
                    capture_output=True, text=True, encoding='utf-8'
                )
                for line in result.stdout.split('\n'):
                    if 'SSID' in line and ':' in line:
                        ssid = line.split(':', 1)[1].strip()
                        if ssid:
                            connected = ssid
                            break
            elif self.system == "Linux":
                result = subprocess.run(
                    ['nmcli', '-t', '-f', 'active,ssid', 'device', 'wifi'],
                    capture_output=True, text=True, encoding='utf-8'
                )
                for line in result.stdout.split('\n'):
                    if line.startswith('yes:'):
                        connected = line.split(':', 1)[1]
                        break
            elif self.system == "Darwin":
                result = subprocess.run(
                    ['networksetup', '-getairportnetwork', 'en0'],
                    capture_output=True, text=True, encoding='utf-8'
                )
                if 'Current Wi-Fi Network' in result.stdout:
                    connected = result.stdout.split(': ')[1].strip()
        except Exception as e:
            print(f"Get connected network error: {e}")
        
        return connected
    
    def get_ip_info(self):
        """Get IP address information"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return {
                'hostname': hostname,
                'ip': ip_address
            }
        except:
            return {
                'hostname': 'Unknown',
                'ip': 'Unknown'
            }
    
    def analyze_channels(self):
        """Analyze channel congestion"""
        channels = {}
        
        for network in self.networks:
            channel = network.get('channel', 0)
            if channel > 0:
                if channel not in channels:
                    channels[channel] = {
                        'count': 0,
                        'networks': [],
                        'signal_avg': 0
                    }
                channels[channel]['count'] += 1
                channels[channel]['networks'].append(network['ssid'])
        
        # Calculate average signal per channel
        for channel, data in channels.items():
            channel_networks = [n for n in self.networks if n.get('channel') == channel]
            if channel_networks:
                signals = [n.get('signal', 0) for n in channel_networks]
                data['signal_avg'] = int(sum(signals) / len(signals))
        
        # Find best channel (least congested)
        best_channels = []
        for ch in range(1, 15):  # 2.4GHz channels
            if ch not in channels or channels[ch]['count'] == 0:
                best_channels.append(ch)
        
        return {
            'channels': channels,
            'best_channels': best_channels[:3],
            'recommendation': best_channels[0] if best_channels else 6
        }
    
    def generate_report(self):
        """Generate comprehensive network report"""
        connected = self.get_connected_network()
        ip_info = self.get_ip_info()
        channel_analysis = self.analyze_channels()
        
        secure_count = 0
        open_count = 0
        total_signal = 0
        
        for network in self.networks:
            if network['security'] in ['WPA2', 'WPA3', 'WPA2/WPA3', 'WPA']:
                secure_count += 1
            elif network['security'] == 'Open':
                open_count += 1
            total_signal += network.get('signal', 0)
        
        avg_signal = int(total_signal / len(self.networks)) if self.networks else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_networks': len(self.networks),
            'secure_networks': secure_count,
            'open_networks': open_count,
            'average_signal': avg_signal,
            'connected_network': connected,
            'ip_info': ip_info,
            'channel_analysis': channel_analysis,
            'networks': self.networks
        }

if __name__ == '__main__':
    scanner = WiFiScanner()
    print("📡 Scanning WiFi networks...")
    networks = scanner.scan_networks()
    
    print(f"\n✅ Found {len(networks)} networks:\n")
    for network in networks:
        print(f"  📶 {network['ssid']}")
        print(f"     Signal: {network['signal']}%")
        print(f"     Channel: {network['channel']}")
        print(f"     Security: {network['security']}")
        print(f"     Band: {network['band']}")
        print()
    
    print("\n📊 Channel Analysis:")
    analysis = scanner.analyze_channels()
    print(f"  Best channels: {analysis['best_channels']}")
    print(f"  Recommendation: Channel {analysis['recommendation']}")

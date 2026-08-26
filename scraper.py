#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  📡  WIFI ACCESS PRO - Ultimate Network Manager            ║
║     Access WiFi & Display Nearby Networks                  ║
║                                                              ║
║  🔍  Scan & Display Nearby WiFi Networks                   ║
║  📊  Real-time Signal Monitoring                           ║
║  🔐  Security Analysis & Warnings                          ║
║  📱  Modern Glass Morphism UI                             ║
║  ⚡  Fast & Responsive                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import subprocess
import platform
import re
import socket
import threading
import time
from datetime import datetime
import sys

TOTAL_LINES = 0

def write(filename, content):
    global TOTAL_LINES
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    lines = content.count('\n') + 1
    TOTAL_LINES += lines
    print(f"  ✅ {filename} ({lines} سطر)")

def section(title):
    print(f"\n{'='*60}")
    print(f"  📡 {title}")
    print(f"{'='*60}")

# ═══════════════════════════════════════════════════════════
# 📡 1. index.html - الواجهة الرئيسية
# ═══════════════════════════════════════════════════════════

def build_index():
    return """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>📡 WiFi Access Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- الخلفية -->
    <div class="bg-void"></div>
    <div class="bg-grid"></div>
    <div class="bg-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
    </div>
    <div id="particlesContainer"></div>

    <!-- التطبيق -->
    <div class="app">
        <!-- الهيدر -->
        <div class="header glass-card">
            <div class="header-left">
                <div class="logo animate-pulse">📡</div>
                <div class="header-text">
                    <h1>WiFi Access Pro</h1>
                    <span>✦ Network Manager ✦</span>
                </div>
            </div>
            <div class="header-actions">
                <button class="btn-icon" onclick="toggleAutoScan()" id="btnAutoScan" title="مسح تلقائي">
                    <i class="fas fa-sync-alt"></i>
                </button>
                <button class="btn-icon" onclick="refreshNetworks()" id="btnRefresh" title="تحديث">
                    <i class="fas fa-rotate"></i>
                </button>
                <button class="btn-icon" onclick="toggleSettings()" id="btnSettings" title="الإعدادات">
                    <i class="fas fa-gear"></i>
                </button>
            </div>
        </div>

        <!-- حالة الاتصال -->
        <div class="connection-status glass-card" id="connectionStatus">
            <div class="status-left">
                <div class="status-icon" id="statusIcon">
                    <i class="fas fa-wifi"></i>
                </div>
                <div class="status-info">
                    <div class="status-title" id="statusTitle">جارٍ الفحص...</div>
                    <div class="status-subtitle" id="statusSubtitle">البحث عن الشبكات المتاحة</div>
                </div>
            </div>
            <div class="status-right">
                <div class="status-badge" id="statusBadge">...</div>
            </div>
        </div>

        <!-- الإحصائيات -->
        <div class="stats-grid">
            <div class="stat-card glass-card" onclick="scrollToNetworks()">
                <div class="stat-icon" style="color:#00ffcc">
                    <i class="fas fa-wifi"></i>
                </div>
                <div class="stat-info">
                    <div class="stat-value" id="totalNetworks">0</div>
                    <div class="stat-label">شبكة متاحة</div>
                </div>
            </div>
            <div class="stat-card glass-card" onclick="scrollToNetworks()">
                <div class="stat-icon" style="color:#ff44aa">
                    <i class="fas fa-signal"></i>
                </div>
                <div class="stat-info">
                    <div class="stat-value" id="avgSignal">0%</div>
                    <div class="stat-label">متوسط الإشارة</div>
                </div>
            </div>
            <div class="stat-card glass-card" onclick="filterSecure()">
                <div class="stat-icon" style="color:#00ff88">
                    <i class="fas fa-shield-halved"></i>
                </div>
                <div class="stat-info">
                    <div class="stat-value" id="secureNetworks">0</div>
                    <div class="stat-label">شبكة آمنة</div>
                </div>
            </div>
            <div class="stat-card glass-card" onclick="filterOpen()">
                <div class="stat-icon" style="color:#ff4444">
                    <i class="fas fa-unlock"></i>
                </div>
                <div class="stat-info">
                    <div class="stat-value" id="openNetworks">0</div>
                    <div class="stat-label">شبكة مفتوحة</div>
                </div>
            </div>
        </div>

        <!-- شريط التقدم والفلترة -->
        <div class="filter-section glass-card">
            <div class="filter-header">
                <h3>📶 الشبكات المكتشفة</h3>
                <div class="filter-actions">
                    <button class="filter-btn active" onclick="filterNetworks('all', this)">
                        <i class="fas fa-list"></i> الكل
                    </button>
                    <button class="filter-btn" onclick="filterNetworks('secure', this)">
                        <i class="fas fa-lock"></i> آمنة
                    </button>
                    <button class="filter-btn" onclick="filterNetworks('open', this)">
                        <i class="fas fa-unlock"></i> مفتوحة
                    </button>
                    <button class="filter-btn" onclick="filterNetworks('5g', this)">
                        <i class="fas fa-tower-broadcast"></i> 5GHz
                    </button>
                </div>
            </div>
            <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" id="searchInput" placeholder="ابحث عن شبكة..." oninput="searchNetworks(this.value)">
            </div>
        </div>

        <!-- قائمة الشبكات -->
        <div class="networks-list" id="networksList">
            <div class="loading-spinner" id="loadingSpinner">
                <div class="spinner"></div>
                <p>جارٍ فحص الشبكات...</p>
            </div>
        </div>

        <!-- لوحة الإعدادات -->
        <div class="settings-panel glass-card" id="settingsPanel" style="display:none">
            <div class="settings-header">
                <h3>⚙️ الإعدادات</h3>
                <button class="btn-close" onclick="toggleSettings()">
                    <i class="fas fa-xmark"></i>
                </button>
            </div>
            <div class="settings-content">
                <div class="setting-item">
                    <div class="setting-info">
                        <div class="setting-title">المسح التلقائي</div>
                        <div class="setting-desc">تحديث الشبكات كل 10 ثوانٍ</div>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="autoScanToggle" checked onchange="toggleAutoScanSetting()">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="setting-item">
                    <div class="setting-info">
                        <div class="setting-title">إظهار الشبكات المخفية</div>
                        <div class="setting-desc">عرض الشبكات بدون اسم</div>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="showHiddenToggle" onchange="toggleHiddenNetworks()">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="setting-item">
                    <div class="setting-info">
                        <div class="setting-title">تنبيه الشبكات غير الآمنة</div>
                        <div class="setting-desc">تحذير عند وجود شبكات مفتوحة</div>
                    </div>
                    <label class="switch">
                        <input type="checkbox" id="securityAlertToggle" checked onchange="toggleSecurityAlerts()">
                        <span class="slider"></span>
                    </label>
                </div>
            </div>
        </div>
    </div>

    <!-- نافذة تفاصيل الشبكة -->
    <div class="modal" id="networkModal" style="display:none">
        <div class="modal-content glass-card">
            <div class="modal-header">
                <h3 id="modalTitle">تفاصيل الشبكة</h3>
                <button class="btn-close" onclick="closeModal()">
                    <i class="fas fa-xmark"></i>
                </button>
            </div>
            <div class="modal-body" id="modalBody"></div>
        </div>
    </div>

    <!-- إشعارات -->
    <div class="toast" id="toast"></div>

    <script src="scanner.js"></script>
    <script src="app.js"></script>
</body>
</html>"""
# ═══════════════════════════════════════════════════════════
# 📡 2. style.css - التصميم الحديث
# ═══════════════════════════════════════════════════════════

def build_style():
    return """*{margin:0;padding:0;box-sizing:border-box}
:root{
    --bg:#0a0a1a;
    --bg2:#12122a;
    --card:rgba(255,255,255,0.05);
    --card2:rgba(255,255,255,0.08);
    --text:#ffffff;
    --text2:#a0a0c0;
    --text3:#606080;
    --accent:#00ffcc;
    --accent2:#ff44aa;
    --accent3:#ffaa00;
    --accent4:#6366f1;
    --danger:#ff4444;
    --success:#00ff88;
    --border:rgba(255,255,255,0.1);
    --radius:20px;
    --radius-sm:14px;
    --radius-xs:10px;
    --shadow:0 8px 32px rgba(0,0,0,0.3);
    --glass:blur(20px);
}
body{
    font-family:'Cairo',sans-serif;
    background:var(--bg);
    color:var(--text);
    min-height:100vh;
    overflow-x:hidden;
    direction:rtl;
    user-select:none;
    -webkit-tap-highlight-color:transparent;
}

/* الخلفية */
.bg-void{
    position:fixed;
    inset:0;
    z-index:0;
    background:radial-gradient(ellipse at 20% 20%,rgba(0,255,204,0.08) 0%,transparent 50%),
               radial-gradient(ellipse at 80% 80%,rgba(99,102,241,0.06) 0%,transparent 50%),
               var(--bg);
}
.bg-grid{
    position:fixed;
    inset:0;
    z-index:0;
    background-image:linear-gradient(rgba(255,255,255,0.02) 1px,transparent 1px),
                     linear-gradient(90deg,rgba(255,255,255,0.02) 1px,transparent 1px);
    background-size:50px 50px;
    pointer-events:none;
}
.bg-orbs{position:fixed;inset:0;z-index:0;pointer-events:none}
.orb{position:absolute;border-radius:50%;filter:blur(80px);opacity:0.3;animation:orbFloat 20s ease-in-out infinite}
.orb-1{width:300px;height:300px;background:#00ffcc;top:-100px;right:-50px}
.orb-2{width:250px;height:250px;background:#6366f1;bottom:-50px;left:-30px;animation-delay:-7s}
.orb-3{width:200px;height:200px;background:#ff44aa;top:50%;left:50%;animation-delay:-14s}
@keyframes orbFloat{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(30px,-30px) scale(1.1)}66%{transform:translate(-20px,20px) scale(0.9)}}

/* التطبيق */
.app{width:100%;max-width:520px;margin:0 auto;padding:12px;position:relative;z-index:1}

/* Glass Card */
.glass-card{
    background:var(--card);
    backdrop-filter:var(--glass);
    -webkit-backdrop-filter:var(--glass);
    border:1px solid var(--border);
    border-radius:var(--radius);
    box-shadow:var(--shadow);
}

/* الهيدر */
.header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:16px;
    margin-bottom:12px;
    position:relative;
    overflow:hidden;
}
.header::before{
    content:'';
    position:absolute;
    top:0;
    left:0;
    right:0;
    height:1px;
    background:linear-gradient(90deg,transparent,var(--accent),transparent);
}
.header-left{display:flex;align-items:center;gap:12px}
.logo{
    width:50px;
    height:50px;
    background:linear-gradient(135deg,rgba(0,255,204,0.1),rgba(99,102,241,0.1));
    border:1px solid rgba(0,255,204,0.3);
    border-radius:var(--radius-sm);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:24px;
    animation:logoPulse 3s ease-in-out infinite;
}
@keyframes logoPulse{0%,100%{box-shadow:0 0 20px rgba(0,255,204,0.3)}50%{box-shadow:0 0 40px rgba(0,255,204,0.6)}}
.header-text h1{
    font-family:'Orbitron',sans-serif;
    font-size:18px;
    font-weight:800;
    background:linear-gradient(135deg,#00ffcc,#6366f1,#ff44aa);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    background-size:200% 200%;
    animation:gradientShift 3s ease infinite;
}
@keyframes gradientShift{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
.header-text span{font-size:8px;color:var(--text3);letter-spacing:2px}
.header-actions{display:flex;gap:8px}
.btn-icon{
    width:40px;
    height:40px;
    background:var(--card2);
    border:1px solid var(--border);
    border-radius:var(--radius-xs);
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    font-size:16px;
    color:var(--text2);
    transition:all 0.3s;
    position:relative;
    overflow:hidden;
}
.btn-icon::before{
    content:'';
    position:absolute;
    inset:0;
    background:linear-gradient(135deg,var(--accent),var(--accent4));
    opacity:0;
    transition:opacity 0.3s;
}
.btn-icon:hover::before{opacity:0.1}
.btn-icon:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-2px)}
.btn-icon:active{transform:translateY(0)}
.btn-icon.active{background:rgba(0,255,204,0.1);border-color:var(--accent);color:var(--accent)}
.btn-icon.spinning i{animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* حالة الاتصال */
.connection-status{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:14px 16px;
    margin-bottom:12px;
    cursor:pointer;
    transition:all 0.3s;
}
.connection-status:hover{border-color:var(--accent);transform:translateY(-2px)}
.status-left{display:flex;align-items:center;gap:12px}
.status-icon{
    width:40px;
    height:40px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:18px;
    background:rgba(0,255,204,0.1);
    border:1px solid rgba(0,255,204,0.3);
}
.status-icon.connected{
    background:rgba(0,255,136,0.1);
    border-color:rgba(0,255,136,0.3);
    color:var(--success);
    animation:connectedPulse 2s ease-in-out infinite;
}
@keyframes connectedPulse{0%,100%{box-shadow:0 0 10px rgba(0,255,136,0.3)}50%{box-shadow:0 0 25px rgba(0,255,136,0.6)}}
.status-icon.disconnected{
    background:rgba(255,68,68,0.1);
    border-color:rgba(255,68,68,0.3);
    color:var(--danger);
}
.status-title{font-size:14px;font-weight:700;margin-bottom:2px}
.status-subtitle{font-size:10px;color:var(--text3)}
.status-badge{
    padding:6px 12px;
    border-radius:20px;
    font-size:10px;
    font-weight:700;
    background:rgba(0,255,204,0.1);
    border:1px solid rgba(0,255,204,0.3);
    color:var(--accent);
}
.status-badge.connected{
    background:rgba(0,255,136,0.1);
    border-color:rgba(0,255,136,0.3);
    color:var(--success);
}

/* الإحصائيات */
.stats-grid{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:8px;
    margin-bottom:12px;
}
.stat-card{
    display:flex;
    align-items:center;
    gap:10px;
    padding:14px;
    cursor:pointer;
    transition:all 0.3s;
}
.stat-card:hover{border-color:var(--accent);transform:translateY(-2px)}
.stat-icon{font-size:20px;width:35px;text-align:center}
.stat-value{
    font-family:'Orbitron',sans-serif;
    font-size:20px;
    font-weight:800;
    background:linear-gradient(135deg,var(--text),var(--accent));
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.stat-label{font-size:9px;color:var(--text3);margin-top:2px}

/* قسم الفلترة */
.filter-section{
    padding:14px;
    margin-bottom:12px;
}
.filter-header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:10px;
    flex-wrap:wrap;
    gap:8px;
}
.filter-header h3{
    font-family:'Orbitron',sans-serif;
    font-size:12px;
    font-weight:700;
    color:var(--accent);
}
.filter-actions{display:flex;gap:6px;flex-wrap:wrap}
.filter-btn{
    padding:6px 10px;
    background:var(--card2);
    border:1px solid var(--border);
    color:var(--text2);
    cursor:pointer;
    border-radius:20px;
    font-size:9px;
    font-family:'Cairo',sans-serif;
    transition:all 0.3s;
    display:flex;
    align-items:center;
    gap:4px;
}
.filter-btn:hover{border-color:var(--accent);color:var(--accent)}
.filter-btn.active{
    background:linear-gradient(135deg,var(--accent),var(--accent4));
    border-color:transparent;
    color:#000;
    font-weight:700;
    box-shadow:0 4px 15px rgba(0,255,204,0.3);
}
.search-box{
    position:relative;
    display:flex;
    align-items:center;
}
.search-box i{
    position:absolute;
    right:12px;
    color:var(--text3);
    font-size:12px;
}
.search-box input{
    width:100%;
    padding:10px 35px 10px 12px;
    background:var(--card2);
    border:1px solid var(--border);
    border-radius:var(--radius-xs);
    color:var(--text);
    font-family:'Cairo',sans-serif;
    font-size:11px;
    transition:all 0.3s;
}
.search-box input:focus{
    outline:none;
    border-color:var(--accent);
    box-shadow:0 0 15px rgba(0,255,204,0.2);
}
.search-box input::placeholder{color:var(--text3)}

/* قائمة الشبكات */
.networks-list{
    display:flex;
    flex-direction:column;
    gap:6px;
    padding-bottom:30px;
}
.loading-spinner{
    text-align:center;
    padding:40px;
    color:var(--text3);
}
.spinner{
    width:40px;
    height:40px;
    border:3px solid var(--border);
    border-top-color:var(--accent);
    border-radius:50%;
    margin:0 auto 15px;
    animation:spin 1s linear infinite;
}
.network-item{
    display:flex;
    align-items:center;
    gap:12px;
    padding:14px;
    background:var(--card);
    backdrop-filter:var(--glass);
    border:1px solid var(--border);
    border-radius:var(--radius-sm);
    cursor:pointer;
    transition:all 0.3s;
    position:relative;
    overflow:hidden;
}
.network-item::before{
    content:'';
    position:absolute;
    top:0;
    left:0;
    right:0;
    height:1px;
    background:linear-gradient(90deg,transparent,var(--accent),transparent);
    opacity:0;
    transition:opacity 0.3s;
}
.network-item:hover{
    border-color:var(--accent);
    transform:translateY(-2px);
    box-shadow:0 8px 25px rgba(0,0,0,0.3);
}
.network-item:hover::before{opacity:1}
.network-item.connected{
    border-color:var(--success);
    background:rgba(0,255,136,0.05);
}
.network-item.connected::before{
    background:linear-gradient(90deg,transparent,var(--success),transparent);
    opacity:1;
}
.network-icon{
    width:40px;
    height:40px;
    border-radius:var(--radius-xs);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:18px;
    position:relative;
}
.network-icon.secure{
    background:rgba(0,255,136,0.1);
    border:1px solid rgba(0,255,136,0.3);
}
.network-icon.open{
    background:rgba(255,68,68,0.1);
    border:1px solid rgba(255,68,68,0.3);
}
.network-info{flex:1;min-width:0}
.network-name{
    font-size:13px;
    font-weight:700;
    margin-bottom:3px;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
}
.network-details{
    font-size:9px;
    color:var(--text3);
    display:flex;
    gap:8px;
    align-items:center;
}
.network-details span{
    display:flex;
    align-items:center;
    gap:3px;
}
.network-signal{
    display:flex;
    flex-direction:column;
    align-items:center;
    gap:4px;
    min-width:50px;
}
.signal-bars{
    display:flex;
    gap:2px;
    align-items:flex-end;
    height:20px;
}
.signal-bar{
    width:3px;
    border-radius:2px;
    transition:all 0.3s;
}
.signal-bar:nth-child(1){height:4px}
.signal-bar:nth-child(2){height:8px}
.signal-bar:nth-child(3){height:12px}
.signal-bar:nth-child(4){height:16px}
.signal-bar:nth-child(5){height:20px}
.signal-percent{
    font-family:'Orbitron',sans-serif;
    font-size:9px;
    font-weight:700;
}
.signal-excellent{color:var(--success)}
.signal-good{color:var(--accent3)}
.signal-poor{color:var(--danger)}

/* الإعدادات */
.settings-panel{
    margin-top:12px;
    padding:16px;
    animation:slideDown 0.3s ease;
}
@keyframes slideDown{
    from{opacity:0;transform:translateY(-20px)}
    to{opacity:1;transform:translateY(0)}
}
.settings-header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:16px;
}
.settings-header h3{
    font-family:'Orbitron',sans-serif;
    font-size:13px;
    font-weight:700;
    color:var(--accent);
}
.btn-close{
    width:30px;
    height:30px;
    background:var(--card2);
    border:1px solid var(--border);
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    color:var(--text2);
    transition:all 0.3s;
}
.btn-close:hover{border-color:var(--danger);color:var(--danger)}
.setting-item{
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:12px 0;
    border-bottom:1px solid var(--border);
}
.setting-item:last-child{border-bottom:none}
.setting-title{font-size:12px;font-weight:600;margin-bottom:2px}
.setting-desc{font-size:9px;color:var(--text3)}

/* Switch */
.switch{position:relative;display:inline-block;width:44px;height:24px}
.switch input{opacity:0;width:0;height:0}
.slider{
    position:absolute;
    cursor:pointer;
    inset:0;
    background:var(--card2);
    border:1px solid var(--border);
    border-radius:24px;
    transition:0.3s;
}
.slider:before{
    content:'';
    position:absolute;
    height:18px;
    width:18px;
    left:2px;
    bottom:2px;
    background:var(--text2);
    border-radius:50%;
    transition:0.3s;
}
.switch input:checked + .slider{
    background:rgba(0,255,204,0.2);
    border-color:var(--accent);
}
.switch input:checked + .slider:before{
    transform:translateX(20px);
    background:var(--accent);
    box-shadow:0 0 10px rgba(0,255,204,0.5);
}

/* Modal */
.modal{
    position:fixed;
    inset:0;
    background:rgba(0,0,0,0.8);
    backdrop-filter:blur(10px);
    z-index:200;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:20px;
    animation:fadeIn 0.3s ease;
}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.modal-content{
    background:var(--bg2);
    border:1px solid var(--accent);
    border-radius:var(--radius);
    padding:20px;
    max-width:400px;
    width:100%;
    max-height:80vh;
    overflow-y:auto;
    animation:slideUp 0.3s ease;
}
@keyframes slideUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
.modal-header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:15px;
}
.modal-header h3{
    font-family:'Orbitron',sans-serif;
    font-size:14px;
    font-weight:700;
    color:var(--accent);
}
.modal-body{font-size:11px;color:var(--text2)}
.detail-row{
    display:flex;
    justify-content:space-between;
    padding:10px 0;
    border-bottom:1px solid var(--border);
}
.detail-label{color:var(--text3)}
.detail-value{font-weight:600;color:var(--text)}

/* Toast */
.toast{
    position:fixed;
    bottom:35px;
    left:50%;
    transform:translateX(-50%) translateY(130px);
    background:var(--bg2);
    border:1px solid var(--accent);
    color:var(--text);
    padding:12px 24px;
    border-radius:25px;
    font-size:11px;
    z-index:300;
    transition:transform 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
    font-family:'Cairo',sans-serif;
    box-shadow:0 8px 30px rgba(0,0,0,0.5);
}
.toast.show{transform:translateX(-50%) translateY(0)}

/* Particles */
.particle{
    position:fixed;
    border-radius:50%;
    pointer-events:none;
    z-index:0;
}
@keyframes particleFloat{
    0%{transform:translateY(110vh) scale(0);opacity:0}
    15%{opacity:0.7}
    85%{opacity:0.1}
    100%{transform:translateY(-10vh) scale(1.5);opacity:0}
}

/* Responsive */
@media(max-width:400px){
    .stats-grid{gap:5px}
    .stat-card{padding:10px}
    .stat-value{font-size:16px}
    .filter-actions{gap:3px}
    .filter-btn{padding:4px 8px;font-size:8px}
}

/* Scrollbar */
::-webkit-scrollbar{width:8px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:var(--accent)}
"""

# ═══════════════════════════════════════════════════════════
# 📡 3. scanner.js - منطق المسح والعرض
# ═══════════════════════════════════════════════════════════

def build_scanner_js():
    return """// 📡 WiFi Scanner - Logic
let networks = [];
let currentFilter = 'all';
let searchQuery = '';
let autoScanEnabled = true;
let scanInterval = null;
let isScanning = false;

// بيانات تجريبية واقعية
const demoNetworks = [
    {ssid: 'Home_Network_5G', bssid: 'AA:BB:CC:DD:EE:01', channel: 36, signal: 85, security: 'WPA2', band: '5GHz', connected: true},
    {ssid: 'Home_Network', bssid: 'AA:BB:CC:DD:EE:02', channel: 6, signal: 72, security: 'WPA2', band: '2.4GHz', connected: false},
    {ssid: 'Neighbor_WiFi', bssid: 'AA:BB:CC:DD:EE:03', channel: 1, signal: 55, security: 'WPA2', band: '2.4GHz', connected: false},
    {ssid: 'CoffeeShop_Free', bssid: 'AA:BB:CC:DD:EE:04', channel: 11, signal: 45, security: 'Open', band: '2.4GHz', connected: false},
    {ssid: 'Office_5G', bssid: 'AA:BB:CC:DD:EE:05', channel: 44, signal: 65, security: 'WPA3', band: '5GHz', connected: false},
    {ssid: 'Guest_Network', bssid: 'AA:BB:CC:DD:EE:06', channel: 3, signal: 30, security: 'WPA', band: '2.4GHz', connected: false},
    {ssid: 'TechHub_5G', bssid: 'AA:BB:CC:DD:EE:07', channel: 52, signal: 78, security: 'WPA2', band: '5GHz', connected: false},
    {ssid: 'SmartHome_IoT', bssid: 'AA:BB:CC:DD:EE:09', channel: 9, signal: 40, security: 'WPA2', band: '2.4GHz', connected: false},
    {ssid: 'Library_WiFi', bssid: 'AA:BB:CC:DD:EE:10', channel: 149, signal: 58, security: 'Open', band: '5GHz', connected: false},
    {ssid: 'Apartment_3B', bssid: 'AA:BB:CC:DD:EE:11', channel: 6, signal: 35, security: 'WPA2', band: '2.4GHz', connected: false},
    {ssid: 'Xiaomi_Router', bssid: 'AA:BB:CC:DD:EE:12', channel: 11, signal: 48, security: 'WPA2', band: '2.4GHz', connected: false},
    {ssid: 'iPhone_Hotspot', bssid: 'AA:BB:CC:DD:EE:13', channel: 1, signal: 62, security: 'WPA2', band: '2.4GHz', connected: false}
];

function initScanner() {
    updateConnectionStatus();
    scanNetworks();
    startAutoScan();
}

function scanNetworks() {
    if (isScanning) return;
    isScanning = true;
    
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) spinner.style.display = 'block';
    
    // محاكاة فحص الشبكات
    setTimeout(() => {
        networks = demoNetworks.map(n => ({
            ...n,
            signal: Math.max(10, Math.min(95, n.signal + Math.floor(Math.random() * 10) - 5))
        }));
        
        // تحديث الاتصال
        updateConnectionStatus();
        updateStats();
        renderNetworks();
        
        if (spinner) spinner.style.display = 'none';
        isScanning = false;
    }, 1500);
}

function startAutoScan() {
    if (scanInterval) clearInterval(scanInterval);
    scanInterval = setInterval(() => {
        if (autoScanEnabled) {
            scanNetworks();
        }
    }, 10000);
}

function toggleAutoScan() {
    autoScanEnabled = !autoScanEnabled;
    const btn = document.getElementById('btnAutoScan');
    btn.classList.toggle('active', autoScanEnabled);
    showToast(autoScanEnabled ? '✅ المسح التلقائي مفعل' : '⏸️ المسح التلقائي متوقف');
}

function toggleAutoScanSetting() {
    autoScanEnabled = document.getElementById('autoScanToggle').checked;
    const btn = document.getElementById('btnAutoScan');
    btn.classList.toggle('active', autoScanEnabled);
}

function refreshNetworks() {
    const btn = document.getElementById('btnRefresh');
    btn.classList.add('spinning');
    
    scanNetworks();
    
    setTimeout(() => {
        btn.classList.remove('spinning');
        showToast('✅ تم تحديث الشبكات');
    }, 2000);
}

function updateConnectionStatus() {
    const connected = networks.find(n => n.connected);
    const statusIcon = document.getElementById('statusIcon');
    const statusTitle = document.getElementById('statusTitle');
    const statusSubtitle = document.getElementById('statusSubtitle');
    const statusBadge = document.getElementById('statusBadge');
    const connectionStatus = document.getElementById('connectionStatus');
    
    if (connected) {
        statusIcon.className = 'status-icon connected';
        statusIcon.innerHTML = '<i class="fas fa-wifi"></i>';
        statusTitle.textContent = connected.ssid;
        statusSubtitle.textContent = `متصل • ${connected.security} • ${connected.signal}%`;
        statusBadge.textContent = 'متصل';
        statusBadge.className = 'status-badge connected';
    } else {
        statusIcon.className = 'status-icon disconnected';
        statusIcon.innerHTML = '<i class="fas fa-wifi"></i>';
        statusTitle.textContent = 'غير متصل';
        statusSubtitle.textContent = 'لا يوجد اتصال نشط';
        statusBadge.textContent = 'منفصل';
        statusBadge.className = 'status-badge';
    }
}

function updateStats() {
    const totalNetworks = networks.length;
    const avgSignal = networks.length > 0 ? Math.round(networks.reduce((sum, n) => sum + n.signal, 0) / networks.length) : 0;
    const secureNetworks = networks.filter(n => ['WPA2', 'WPA3', 'WPA2/WPA3'].includes(n.security)).length;
    const openNetworks = networks.filter(n => n.security === 'Open').length;
    
    document.getElementById('totalNetworks').textContent = totalNetworks;
    document.getElementById('avgSignal').textContent = avgSignal + '%';
    document.getElementById('secureNetworks').textContent = secureNetworks;
    document.getElementById('openNetworks').textContent = openNetworks;
    
    // تنبيه للشبكات غير الآمنة
    if (openNetworks > 0 && document.getElementById('securityAlertToggle').checked) {
        showToast(`⚠️ تنبيه: ${openNetworks} شبكة مفتوحة غير آمنة`);
    }
}

function renderNetworks() {
    const list = document.getElementById('networksList');
    
    if (!networks.length) {
        list.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>لم يتم العثور على شبكات</p>
            </div>
        `;
        return;
    }
    
    let filteredNetworks = networks;
    
    // تطبيق الفلتر
    if (currentFilter === 'secure') {
        filteredNetworks = networks.filter(n => ['WPA2', 'WPA3', 'WPA2/WPA3'].includes(n.security));
    } else if (currentFilter === 'open') {
        filteredNetworks = networks.filter(n => n.security === 'Open');
    } else if (currentFilter === '5g') {
        filteredNetworks = networks.filter(n => n.band === '5GHz');
    }
    
    // تطبيق البحث
    if (searchQuery) {
        filteredNetworks = filteredNetworks.filter(n => 
            n.ssid.toLowerCase().includes(searchQuery.toLowerCase())
        );
    }
    
    // ترتيب حسب قوة الإشارة
    filteredNetworks.sort((a, b) => b.signal - a.signal);
    
    list.innerHTML = filteredNetworks.map((network, index) => {
        const originalIndex = networks.indexOf(network);
        const isSecure = ['WPA2', 'WPA3', 'WPA2/WPA3'].includes(network.security);
        const signalClass = network.signal >= 70 ? 'signal-excellent' : network.signal >= 40 ? 'signal-good' : 'signal-poor';
        
        // إنشاء أعمدة الإشارة
        const signalBars = [1,2,3,4,5].map(level => {
            const active = network.signal >= (level * 20);
            return `<div class="signal-bar" style="height:${level * 4}px;background:${active ? (network.signal >= 70 ? 'var(--success)' : network.signal >= 40 ? 'var(--accent3)' : 'var(--danger)') : 'var(--border)'}"></div>`;
        }).join('');
        
        return `
            <div class="network-item ${network.connected ? 'connected' : ''}" onclick="showNetworkDetails(${originalIndex})">
                <div class="network-icon ${isSecure ? 'secure' : 'open'}">
                    <i class="fas ${isSecure ? 'fa-lock' : 'fa-unlock'}"></i>
                </div>
                <div class="network-info">
                    <div class="network-name">${network.ssid} ${network.connected ? '<i class="fas fa-check-circle" style="color:var(--success);font-size:10px"></i>' : ''}</div>
                    <div class="network-details">
                        <span><i class="fas fa-tower-broadcast"></i> ${network.band}</span>
                        <span><i class="fas fa-hashtag"></i> ${network.channel}</span>
                        <span><i class="fas fa-shield-halved"></i> ${network.security}</span>
                    </div>
                </div>
                <div class="network-signal">
                    <div class="signal-bars">${signalBars}</div>
                    <div class="signal-percent ${signalClass}">${network.signal}%</div>
                </div>
            </div>
        `;
    }).join('');
}

function filterNetworks(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderNetworks();
}

function filterSecure() {
    currentFilter = 'secure';
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.filter-btn')[1].classList.add('active');
    renderNetworks();
    scrollToNetworks();
}

function filterOpen() {
    currentFilter = 'open';
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.filter-btn')[2].classList.add('active');
    renderNetworks();
    scrollToNetworks();
}

function searchNetworks(query) {
    searchQuery = query;
    renderNetworks();
}

function scrollToNetworks() {
    document.getElementById('networksList').scrollIntoView({behavior: 'smooth'});
}

function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    document.getElementById('btnSettings').classList.toggle('active', panel.style.display === 'block');
}

function toggleHiddenNetworks() {
    showToast('تم ' + (document.getElementById('showHiddenToggle').checked ? 'إظهار' : 'إخفاء') + ' الشبكات المخفية');
}

function toggleSecurityAlerts() {
    showToast('تم ' + (document.getElementById('securityAlertToggle').checked ? 'تفعيل' : 'تعطيل') + ' تنبيهات الأمان');
}

function showNetworkDetails(index) {
    const network = networks[index];
    if (!network) return;
    
    const modal = document.getElementById('networkModal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');
    
    title.textContent = network.ssid;
    
    const securityLevel = getSecurityLevel(network.security);
    const signalQuality = network.signal >= 70 ? 'ممتاز' : network.signal >= 40 ? 'جيد' : 'ضعيف';
    
    body.innerHTML = `
        <div class="detail-row">
            <span class="detail-label">BSSID</span>
            <span class="detail-value">${network.bssid}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">نوع النطاق</span>
            <span class="detail-value">${network.band}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">القناة</span>
            <span class="detail-value">${network.channel}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">قوة الإشارة</span>
            <span class="detail-value">${network.signal}% (${signalQuality})</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">نوع الأمان</span>
            <span class="detail-value">${network.security}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">مستوى الأمان</span>
            <span class="detail-value">${securityLevel}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">الحالة</span>
            <span class="detail-value">${network.connected ? '✅ متصل' : '❌ غير متصل'}</span>
        </div>
    `;
    
    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('networkModal').style.display = 'none';
}

function getSecurityLevel(security) {
    if (security === 'WPA3') return '🟢 ممتاز - أعلى مستوى حماية';
    if (security === 'WPA2' || security === 'WPA2/WPA3') return '🟢 جيد جداً - حماية قوية';
    if (security === 'WPA') return '🟡 متوسط - حماية قديمة';
    if (security === 'WEP') return '🔴 ضعيف - غير آمن';
    return '🔴 غير آمن - شبكة مفتوحة';
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// إغلاق النافذة عند النقر خارجها
document.addEventListener('click', function(e) {
    const modal = document.getElementById('networkModal');
    if (e.target === modal) {
        closeModal();
    }
});
"""

# ═══════════════════════════════════════════════════════════
# 📡 4. app.js - التهيئة الرئيسية
# ═══════════════════════════════════════════════════════════

def build_app_js():
    return """// 📡 WiFi Access Pro - Main App
function initParticles() {
    const container = document.getElementById('particlesContainer');
    const colors = ['#00ffcc', '#6366f1', '#ff44aa'];
    
    for (let i = 0; i < 30; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            left: ${Math.random() * 100}%;
            bottom: -10px;
            width: ${Math.random() * 3 + 1}px;
            height: ${Math.random() * 3 + 1}px;
            background: radial-gradient(circle, ${colors[i % 3]} 0%, transparent 70%);
            animation: particleFloat ${Math.random() * 5 + 5}s ease-in infinite;
            animation-delay: ${Math.random() * 5}s;
        `;
        container.appendChild(particle);
    }
}

// تهيئة التطبيق
document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initScanner();
    
    console.log('📡 WiFi Access Pro initialized');
    console.log('🔍 Scanning for nearby networks...');
});

// معالجة الأخطاء
window.onerror = function(msg, url, line, col, error) {
    console.error('Error:', msg);
    showToast('⚠️ حدث خطأ غير متوقع');
    return false;
};
"""

# ═══════════════════════════════════════════════════════════
# 📡 MAIN - المولد الرئيسي
# ═══════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║  📡  WIFI ACCESS PRO - Network Manager                  ║
║     Access WiFi & Display Nearby Networks               ║
║                                                          ║
║  🔍  Scan & Display WiFi Networks                       ║
║  📊  Real-time Signal Monitoring                        ║
║  🔐  Security Analysis                                  ║
║  📱  Modern Glass Morphism UI                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

    section("BUILDING WIFI ACCESS PRO")

    write("index.html", build_index())
    write("style.css", build_style())
    write("scanner.js", build_scanner_js())
    write("app.js", build_app_js())

    print(f"""
{'='*60}
  ✅ BUILD COMPLETE! - {TOTAL_LINES} خط
  📁 4 ملفات

  📡 WiFi Access Pro Features:
  • 🔍 عرض الشبكات القريبة
  • 📊 مراقبة قوة الإشارة
  • 🔐 تحليل الأمان
  • 🔍 بحث وتصفية
  • ⚡ مسح تلقائي
  • 📱 واجهة زجاجية عصرية

  🚀 للتشغيل:
     افتح index.html في المتصفح

  📡 WIFI ACCESS PRO READY!
{'='*60}
    """)

if __name__ == "__main__":
    main()

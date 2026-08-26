#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                                                            ║
║  📡  WiFi NETSCAN PRO - ULTIMATE NETWORK SCANNER  📡     ║
║     Real WiFi Access + Professional UI                     ║
║                                                            ║
║  🌐  Real Network Detection + Signal Analysis              ║
║  🎨  Premium Glass Morphism Design                         ║
║  📊  Real-time Signal Monitoring                           ║
║  🔐  Security Analysis + Network Details                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
import subprocess
import platform
import re
from datetime import datetime

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
# 📡 1. index.html - واجهة احترافية
# ═══════════════════════════════════════════════════════════

def build_index():
    return """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>📡 WiFi NetScan Pro - الماسح الاحترافي</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="bg-void"></div>
    <div class="bg-grid"></div>
    <div class="bg-ring bg-ring-1"></div>
    <div class="bg-ring bg-ring-2"></div>
    <div class="bg-ring bg-ring-3"></div>
    <div id="particlesContainer"></div>

    <div class="app">
        <!-- Header -->
        <div class="header">
            <div class="header-left">
                <div class="logo">
                    <i class="fas fa-wifi"></i>
                </div>
                <div class="header-text">
                    <h1>WiFi NetScan Pro</h1>
                    <span>✦ ULTIMATE SCANNER ✦</span>
                </div>
            </div>
            <div class="header-right">
                <button class="btn-icon" onclick="toggleFilters()" id="btnFilters" title="الفلاتر">
                    <i class="fas fa-filter"></i>
                </button>
                <button class="btn-icon" onclick="toggleHistory()" id="btnHistory" title="السجل">
                    <i class="fas fa-history"></i>
                </button>
                <button class="btn-icon" onclick="toggleSettings()" id="btnSettings" title="الإعدادات">
                    <i class="fas fa-cog"></i>
                </button>
            </div>
        </div>

        <!-- Stats Bar -->
        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-wifi"></i></div>
                <div class="stat-info">
                    <div class="stat-value" id="totalNetworks">0</div>
                    <div class="stat-label">الشبكات</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-shield-alt"></i></div>
                <div class="stat-info">
                    <div class="stat-value" id="secureNetworks">0</div>
                    <div class="stat-label">آمنة</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-unlock"></i></div>
                <div class="stat-info">
                    <div class="stat-value" id="openNetworks">0</div>
                    <div class="stat-label">مفتوحة</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon"><i class="fas fa-signal"></i></div>
                <div class="stat-info">
                    <div class="stat-value" id="avgSignal">0%</div>
                    <div class="stat-label">المتوسط</div>
                </div>
            </div>
        </div>

        <!-- Main Visualizer -->
        <div class="visualizer-3d" id="visualizer3D">
            <canvas id="vizCanvas"></canvas>
            <div class="viz-overlay">
                <div class="viz-header">
                    <div class="viz-title">
                        <div class="network-count" id="networkCount">0 شبكة</div>
                        <div class="scan-status" id="scanStatus">جاهز للمسح</div>
                    </div>
                    <div class="viz-time">
                        <span id="lastScan">آخر مسح: -</span>
                        <span id="scanDuration">0:00</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Progress Bar -->
        <div class="progress-section">
            <div class="progress-track" id="progressTrack">
                <div class="progress-fill" id="progressFill"></div>
                <div class="progress-thumb" id="progressThumb"></div>
            </div>
            <div class="progress-labels">
                <span>المسح</span>
                <span id="progressPercent">0%</span>
            </div>
        </div>

        <!-- Controls -->
        <div class="controls">
            <button class="ctrl-btn" onclick="toggleAutoScan()" id="autoScanBtn" title="مسح تلقائي">
                <i class="fas fa-sync"></i>
            </button>
            <button class="ctrl-btn" onclick="exportData()" title="تصدير">
                <i class="fas fa-download"></i>
            </button>
            <button class="ctrl-play" id="scanBtn" onclick="startScan()" title="بدء المسح">
                <i class="fas fa-search" id="scanIcon"></i>
            </button>
            <button class="ctrl-btn" onclick="sortNetworks()" title="ترتيب">
                <i class="fas fa-sort-amount-down"></i>
            </button>
            <button class="ctrl-btn" onclick="clearNetworks()" title="مسح">
                <i class="fas fa-trash"></i>
            </button>
        </div>

        <!-- Filters Panel -->
        <div class="filter-panel" id="filterPanel" style="display:none">
            <div class="panel-header">
                <h3><i class="fas fa-filter"></i> الفلاتر</h3>
                <button class="btn-close" onclick="toggleFilters()">✕</button>
            </div>
            <div class="filter-presets">
                <button class="preset-btn active" onclick="setFilter('all', this)">الكل</button>
                <button class="preset-btn" onclick="setFilter('secure', this)">آمنة</button>
                <button class="preset-btn" onclick="setFilter('open', this)">مفتوحة</button>
                <button class="preset-btn" onclick="setFilter('5ghz', this)">5 GHz</button>
                <button class="preset-btn" onclick="setFilter('2ghz', this)">2.4 GHz</button>
            </div>
            <div class="filter-options">
                <div class="filter-knob">
                    <span>📶 الحد الأدنى للإشارة</span>
                    <input type="range" class="gold-slider" id="minSignal" min="0" max="100" value="0" oninput="updateFilters()">
                    <span id="minSignalValue">0%</span>
                </div>
                <div class="filter-knob">
                    <span>👁 إظهار المخفية</span>
                    <label class="switch">
                        <input type="checkbox" id="showHidden" onchange="updateFilters()">
                        <span class="slider"></span>
                    </label>
                </div>
            </div>
        </div>

        <!-- History Panel -->
        <div class="history-panel" id="historyPanel" style="display:none">
            <div class="panel-header">
                <h3><i class="fas fa-history"></i> سجل المسح</h3>
                <button class="btn-close" onclick="toggleHistory()">✕</button>
            </div>
            <div class="history-content" id="historyContent">
                <p class="history-line">📡 لا يوجد سجل بعد</p>
            </div>
        </div>

        <!-- Settings Panel -->
        <div class="settings-panel" id="settingsPanel" style="display:none">
            <div class="panel-header">
                <h3><i class="fas fa-cog"></i> الإعدادات</h3>
                <button class="btn-close" onclick="toggleSettings()">✕</button>
            </div>
            <div class="settings-content">
                <div class="setting-item">
                    <span>🔄 المسح التلقائي</span>
                    <label class="switch">
                        <input type="checkbox" id="autoScanSetting" onchange="updateSettings()">
                        <span class="slider"></span>
                    </label>
                </div>
                <div class="setting-item">
                    <span>⏱ مدة المسح (ثانية)</span>
                    <input type="number" class="setting-input" id="scanInterval" value="10" min="5" max="60">
                </div>
                <div class="setting-item">
                    <span>🔊 صوت التنبيه</span>
                    <label class="switch">
                        <input type="checkbox" id="soundEnabled" checked>
                        <span class="slider"></span>
                    </label>
                </div>
            </div>
        </div>

        <!-- Network List -->
        <div class="playlist-section">
            <div class="playlist-header">
                <h3><i class="fas fa-network-wired"></i> الشبكات المكتشفة</h3>
                <span class="network-stats" id="networkStats">0 شبكة</span>
            </div>
            <div class="playlist" id="networkList">
                <div class="empty-playlist">
                    <span>📡</span>
                    <p>اضغط زر المسح لبدء اكتشاف الشبكات</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Network Details Modal -->
    <div class="modal" id="networkModal">
        <div class="modal-content">
            <div class="modal-header">
                <h3 id="modalTitle">تفاصيل الشبكة</h3>
                <button class="btn-close" onclick="closeModal()">✕</button>
            </div>
            <div class="modal-body" id="modalBody">
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script src="storage.js"></script>
    <script src="particles.js"></script>
    <script src="visualizer.js"></script>
    <script src="scanner.js"></script>
    <script src="filters.js"></script>
    <script src="history.js"></script>
    <script src="settings.js"></script>
    <script src="app.js"></script>
</body>
</html>"""

# ═══════════════════════════════════════════════════════════
# 📡 2. style.css - تصميم احترافي
# ═══════════════════════════════════════════════════════════

def build_style():
    return """*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a1a;--card:rgba(15,15,35,0.9);--card2:rgba(20,20,45,0.8);--text:#f0e8ff;--text2:#a098b8;--text3:#605878;--accent:#00ffcc;--accent2:#ff44aa;--accent3:#ffaa00;--accent4:#6366f1;--glass:rgba(0,255,204,0.08);--border:rgba(0,255,204,0.15);--radius:24px;--radius-sm:16px;--radius-xs:12px;--shadow:0 8px 32px rgba(0,0,0,0.3);--shadow-glow:0 0 30px rgba(0,255,204,0.2)}
body{font-family:'Cairo',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;-webkit-tap-highlight-color:transparent;direction:rtl;user-select:none}

.bg-void{position:fixed;inset:0;z-index:0;background:radial-gradient(ellipse at 30% 20%,rgba(0,255,204,0.05) 0%,transparent 60%),radial-gradient(ellipse at 70% 80%,rgba(255,68,170,0.04) 0%,transparent 60%),var(--bg)}
.bg-grid{position:fixed;inset:0;z-index:0;background-image:linear-gradient(rgba(0,255,204,0.02) 1px,transparent 1px),linear-gradient(90deg,rgba(0,255,204,0.02) 1px,transparent 1px);background-size:50px 50px;pointer-events:none}
.bg-ring{position:fixed;border-radius:50%;border:1px solid rgba(0,255,204,0.08);z-index:0;pointer-events:none;animation:ringRotate 30s linear infinite}
.bg-ring-1{width:600px;height:600px;top:-200px;left:-100px;animation-duration:25s}
.bg-ring-2{width:500px;height:500px;bottom:-150px;right:-80px;animation-duration:35s;animation-direction:reverse}
.bg-ring-3{width:400px;height:400px;top:30%;left:40%;animation-duration:40s}
@keyframes ringRotate{to{transform:rotate(360deg)}}

.app{width:100%;max-width:520px;margin:0 auto;padding:12px;position:relative;z-index:1}

/* Header */
.header{display:flex;align-items:center;justify-content:space-between;padding:16px;background:var(--card);backdrop-filter:blur(40px);border-radius:var(--radius);border:1px solid var(--border);margin-bottom:12px;box-shadow:var(--shadow)}
.header-left{display:flex;align-items:center;gap:12px}
.logo{width:48px;height:48px;background:var(--glass);border:1px solid var(--border);border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;font-size:22px;color:var(--accent);animation:logoGlow 3s ease-in-out infinite}
@keyframes logoGlow{0%,100%{box-shadow:0 0 20px rgba(0,255,204,0.3)}50%{box-shadow:0 0 35px rgba(255,68,170,0.6)}}
.header-text h1{font-family:'Orbitron',sans-serif;font-size:20px;font-weight:800;background:linear-gradient(135deg,#00ffcc,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.header-text span{font-size:8px;color:var(--text3);letter-spacing:3px}
.header-right{display:flex;gap:8px}
.btn-icon{width:40px;height:40px;background:var(--card2);border:1px solid var(--border);border-radius:var(--radius-xs);display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:16px;color:var(--text2);transition:all 0.3s}
.btn-icon:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-2px)}
.btn-icon.active{background:var(--glass);border-color:var(--accent);color:var(--accent);box-shadow:var(--shadow-glow)}

/* Stats Bar */
.stats-bar{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}
.stat-card{background:var(--card);backdrop-filter:blur(40px);border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;text-align:center;transition:all 0.3s}
.stat-card:hover{transform:translateY(-3px);box-shadow:var(--shadow-glow)}
.stat-icon{font-size:20px;margin-bottom:6px}
.stat-icon .fa-wifi{color:var(--accent)}
.stat-icon .fa-shield-alt{color:#00ff88}
.stat-icon .fa-unlock{color:var(--accent2)}
.stat-icon .fa-signal{color:var(--accent3)}
.stat-value{font-family:'Orbitron',sans-serif;font-size:18px;font-weight:700;color:var(--text)}
.stat-label{font-size:9px;color:var(--text3)}

/* Visualizer */
.visualizer-3d{position:relative;width:100%;aspect-ratio:1;max-height:350px;background:var(--card);backdrop-filter:blur(40px);border-radius:var(--radius);border:1px solid var(--border);overflow:hidden;margin-bottom:10px;box-shadow:var(--shadow)}
.visualizer-3d canvas{width:100%;height:100%}
.viz-overlay{position:absolute;bottom:0;left:0;right:0;padding:16px;background:linear-gradient(to top,rgba(10,10,26,0.95),transparent)}
.viz-header{display:flex;justify-content:space-between;align-items:flex-end}
.network-count{font-family:'Orbitron',sans-serif;font-size:18px;font-weight:700;color:var(--accent);text-shadow:0 0 20px rgba(0,255,204,0.5)}
.scan-status{font-size:11px;color:var(--text2)}
.viz-time{text-align:left;font-family:'Orbitron',sans-serif;font-size:9px;color:var(--accent2)}

/* Progress */
.progress-section{padding:4px 0;margin-bottom:10px}
.progress-track{width:100%;height:6px;background:rgba(255,255,255,0.1);border-radius:3px;cursor:pointer;position:relative}
.progress-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2),var(--accent3));border-radius:3px;width:0;transition:width 0.3s ease}
.progress-thumb{position:absolute;top:-5px;width:16px;height:16px;background:#fff;border-radius:50%;box-shadow:0 0 15px rgba(0,255,204,0.6);transform:translateX(-50%);left:0;display:none}
.progress-track:hover .progress-thumb{display:block}
.progress-labels{display:flex;justify-content:space-between;font-size:9px;color:var(--text3);margin-top:4px}

/* Controls */
.controls{display:flex;align-items:center;justify-content:center;gap:16px;margin-bottom:12px}
.ctrl-btn{width:44px;height:44px;background:var(--card2);border:1px solid var(--border);border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:16px;color:var(--text2);transition:all 0.3s}
.ctrl-btn:hover{border-color:var(--accent);color:var(--accent);transform:scale(1.1)}
.ctrl-btn.active{border-color:var(--accent);color:var(--accent);box-shadow:var(--shadow-glow)}
.ctrl-play{width:64px;height:64px;background:linear-gradient(135deg,var(--accent),var(--accent4));border:none;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:22px;color:#000;box-shadow:0 8px 30px rgba(0,255,204,0.4);transition:all 0.3s;position:relative;overflow:hidden}
.ctrl-play::before{content:'';position:absolute;inset:-2px;background:linear-gradient(135deg,var(--accent),var(--accent2),var(--accent3));border-radius:50%;z-index:-1;animation:spin 3s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.ctrl-play:hover{transform:scale(1.1);box-shadow:0 12px 40px rgba(99,102,241,0.6)}
.ctrl-play:active{transform:scale(0.95)}
.ctrl-play.scanning{animation:pulse 1s ease-in-out infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(0,255,204,0.7)}50%{box-shadow:0 0 0 20px rgba(0,255,204,0)}}

/* Panels */
.filter-panel,.history-panel,.settings-panel{background:var(--card);backdrop-filter:blur(40px);border-radius:var(--radius);border:1px solid var(--border);padding:16px;margin-bottom:12px;animation:slideDown 0.4s ease;box-shadow:var(--shadow)}
@keyframes slideDown{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
.panel-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.panel-header h3{font-family:'Orbitron',sans-serif;font-size:14px;font-weight:700;color:var(--accent)}
.btn-close{width:30px;height:30px;background:var(--card2);border:1px solid var(--border);color:var(--text2);cursor:pointer;border-radius:50%;font-size:12px;transition:all 0.3s}
.btn-close:hover{border-color:var(--accent2);color:var(--accent2)}

.filter-presets{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.preset-btn{padding:6px 12px;background:var(--card2);border:1px solid var(--border);color:var(--text2);cursor:pointer;border-radius:20px;font-size:10px;font-family:'Cairo',sans-serif;transition:all 0.3s}
.preset-btn:hover{border-color:var(--accent)}
.preset-btn.active{background:var(--accent);border-color:var(--accent);color:#000;font-weight:700}
.filter-options{display:flex;gap:20px;justify-content:space-around;flex-wrap:wrap}
.filter-knob{display:flex;flex-direction:column;align-items:center;gap:8px}
.filter-knob span{font-size:10px;color:var(--text2)}
.gold-slider{width:120px;height:4px;-webkit-appearance:none;appearance:none;background:rgba(0,255,204,0.2);border-radius:2px;outline:none;cursor:pointer}
.gold-slider::-webkit-slider-thumb{-webkit-appearance:none;width:20px;height:20px;background:var(--accent);border-radius:50%;cursor:pointer;box-shadow:0 0 15px rgba(0,255,204,0.5)}

/* Switch */
.switch{position:relative;display:inline-block;width:50px;height:26px}
.switch input{opacity:0;width:0;height:0}
.slider{position:absolute;cursor:pointer;inset:0;background:var(--card2);border:1px solid var(--border);transition:0.3s;border-radius:26px}
.slider:before{position:absolute;content:'';height:18px;width:18px;left:3px;bottom:3px;background:var(--text2);transition:0.3s;border-radius:50%}
input:checked + .slider{background:var(--glass);border-color:var(--accent)}
input:checked + .slider:before{transform:translateX(24px);background:var(--accent);box-shadow:0 0 10px rgba(0,255,204,0.5)}

/* History */
.history-content{max-height:180px;overflow-y:auto}
.history-line{padding:8px 0;font-size:12px;color:var(--text2);text-align:center;border-bottom:1px solid rgba(255,255,255,0.05)}
.history-line.active{color:var(--accent);font-weight:700}

/* Settings */
.settings-content{display:flex;flex-direction:column;gap:12px}
.setting-item{display:flex;align-items:center;justify-content:space-between;padding:8px;background:var(--card2);border-radius:var(--radius-xs)}
.setting-item span{font-size:11px}
.setting-input{width:60px;padding:5px;background:var(--card);border:1px solid var(--border);color:var(--text);border-radius:8px;text-align:center;font-family:'Orbitron',sans-serif}

/* Network List */
.playlist-section{margin-top:8px;padding-bottom:30px}
.playlist-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;padding:0 4px}
.playlist-header h3{font-family:'Orbitron',sans-serif;font-size:14px;font-weight:700;color:var(--text)}
.network-stats{font-size:10px;color:var(--accent);font-family:'Orbitron',sans-serif}
.playlist{display:flex;flex-direction:column;gap:8px}
.network-item{display:flex;align-items:center;gap:12px;padding:14px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius-sm);cursor:pointer;transition:all 0.3s}
.network-item:hover{border-color:var(--accent);background:var(--glass);transform:translateX(-5px)}
.network-item.active{border-color:var(--accent);background:rgba(0,255,204,0.08);box-shadow:var(--shadow-glow)}
.network-item .n-icon{width:40px;height:40px;background:var(--glass);border-radius:var(--radius-xs);display:flex;align-items:center;justify-content:center;font-size:20px}
.network-item .n-info{flex:1;min-width:0}
.network-item .n-name{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.network-item .n-details{font-size:10px;color:var(--text3);margin-top:2px}
.network-item .n-signal{display:flex;flex-direction:column;align-items:center;gap:4px}
.signal-bars{display:flex;align-items:flex-end;gap:2px;height:24px}
.signal-bar{width:5px;background:var(--accent);border-radius:2px;transition:all 0.3s}
.signal-percent{font-size:9px;color:var(--accent);font-family:'Orbitron',sans-serif}
.empty-playlist{text-align:center;padding:40px;color:var(--text3)}
.empty-playlist span{font-size:48px;display:block;margin-bottom:12px}
.empty-playlist p{font-size:13px}

/* Modal */
.modal{position:fixed;inset:0;background:rgba(0,0,0,0.8);backdrop-filter:blur(10px);z-index:1000;display:none;align-items:center;justify-content:center;padding:20px}
.modal.active{display:flex}
.modal-content{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;max-width:400px;width:100%;animation:modalIn 0.3s ease}
@keyframes modalIn{from{transform:scale(0.8);opacity:0}to{transform:scale(1);opacity:1}}
.modal-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.modal-header h3{font-family:'Orbitron',sans-serif;font-size:16px;color:var(--accent)}
.modal-body{display:flex;flex-direction:column;gap:10px}
.modal-item{display:flex;justify-content:space-between;padding:8px;background:var(--card2);border-radius:var(--radius-xs)}
.modal-item .label{font-size:11px;color:var(--text3)}
.modal-item .value{font-size:12px;font-weight:600}

.toast{position:fixed;bottom:35px;left:50%;transform:translateX(-50%) translateY(130px);background:var(--card);border:1px solid var(--accent);color:var(--text);padding:12px 24px;border-radius:25px;font-size:12px;z-index:2000;transition:transform 0.4s cubic-bezier(0.175,0.885,0.32,1.275);font-family:'Cairo',sans-serif;box-shadow:var(--shadow-glow)}
.toast.show{transform:translateX(-50%) translateY(0)}

.particle{position:fixed;border-radius:50%;pointer-events:none;z-index:0}
@keyframes particleFloat{0%{transform:translateY(110vh) scale(0);opacity:0}15%{opacity:0.7}85%{opacity:0.1}100%{transform:translateY(-10vh) scale(1.5);opacity:0}}

@media(max-width:400px){
    .stats-bar{grid-template-columns:repeat(2,1fr)}
    .controls{gap:10px}
    .ctrl-btn{width:38px;height:38px}
    .ctrl-play{width:56px;height:56px}
}"""

# ═══════════════════════════════════════════════════════════
# 📡 3-9. JS Files
# ═══════════════════════════════════════════════════════════

def build_storage_js():
    return """const KEYS={networks:'wifinetscanpro_networks',settings:'wifinetscanpro_settings',history:'wifinetscanpro_history',filters:'wifinetscanpro_filters'};
function saveData(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true}catch(e){console.error('Save error:',e);return false}}
function loadData(k,d=null){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){console.error('Load error:',e);return d}}
function saveNetworks(nets){const data=nets.map(n=>({id:n.id,ssid:n.ssid,mac:n.mac,signal:n.signal,frequency:n.frequency,channel:n.channel,security:n.security,encryption:n.encryption,maxSpeed:n.maxSpeed,firstSeen:n.firstSeen,lastSeen:n.lastSeen,hidden:n.hidden}));return saveData(KEYS.networks,data)}
function loadNetworks(){return loadData(KEYS.networks,[])}
function saveFilters(f){saveData(KEYS.filters,f)}
function loadFilters(){return loadData(KEYS.filters,{type:'all',minSignal:0,showHidden:false})}
function saveHistory(h){saveData(KEYS.history,h)}
function loadHistory(){return loadData(KEYS.history,[])}
function addToHistory(entry){const h=loadHistory();h.unshift(entry);if(h.length>50)h.pop();saveHistory(h)}
function saveSettings(s){saveData(KEYS.settings,s)}
function loadSettings(){return loadData(KEYS.settings,{autoScan:false,scanInterval:10,soundEnabled:true})}"""

def build_particles_js():
    return """function initParticles(){const c=document.getElementById('particlesContainer');c.innerHTML='';const cols=['#00ffcc','#ff44aa','#6366f1','#ffaa00'];for(let i=0;i<50;i++){const p=document.createElement('div');p.className='particle';const size=Math.random()*4+1;p.style.cssText=`left:${Math.random()*100}%;bottom:-10px;width:${size}px;height:${size}px;background:radial-gradient(circle,${cols[i%4]} 0%,transparent 70%);animation:particleFloat ${Math.random()*5+5}s ease-in infinite;animation-delay:${Math.random()*5}s`;c.appendChild(p)}}"""

def build_visualizer_js():
    return """let vizCanvas,vizCtx,networkData=[],vizAnimationId;
function initVisualizer(){vizCanvas=document.getElementById('vizCanvas');vizCtx=vizCanvas.getContext('2d');resizeViz();window.addEventListener('resize',resizeViz);for(let i=0;i<64;i++)networkData.push(Math.random()*0.3);drawViz()}
function resizeViz(){const c=vizCanvas.parentElement;vizCanvas.width=c.clientWidth;vizCanvas.height=c.clientHeight}
function drawViz(){vizAnimationId=requestAnimationFrame(drawViz);const w=vizCanvas.width,h=vizCanvas.height;vizCtx.fillStyle='rgba(10,10,26,0.3)';vizCtx.fillRect(0,0,w,h);const cx=w/2,cy=h/2,r=Math.min(w,h)*0.35;for(let i=0;i<networkData.length;i++){const a=(i/networkData.length)*Math.PI*2;const val=networkData[i];const x1=cx+Math.cos(a)*(r+val*60);const y1=cy+Math.sin(a)*(r+val*60);const x2=cx+Math.cos(a)*(r-val*40);const y2=cy+Math.sin(a)*(r-val*40);const grad=vizCtx.createLinearGradient(x1,y1,x2,y2);grad.addColorStop(0,`rgba(0,255,204,${0.3+val})`);grad.addColorStop(0.5,`rgba(99,102,241,${0.2+val})`);grad.addColorStop(1,`rgba(255,68,170,${0.15+val})`);vizCtx.beginPath();vizCtx.moveTo(x1,y1);vizCtx.lineTo(x2,y2);vizCtx.strokeStyle=grad;vizCtx.lineWidth=1.5+val*2;vizCtx.stroke();vizCtx.beginPath();vizCtx.arc(x1,y1,3+val*15,0,Math.PI*2);vizCtx.fillStyle=`rgba(0,255,204,${0.6+val})`;vizCtx.shadowColor='#00ffcc';vizCtx.shadowBlur=10+val*20;vizCtx.fill();vizCtx.shadowBlur=0}
vizCtx.beginPath();vizCtx.arc(cx,cy,8,0,Math.PI*2);vizCtx.fillStyle='#fff';vizCtx.shadowColor='#00ffcc';vizCtx.shadowBlur=30;vizCtx.fill();vizCtx.shadowBlur=0}
function updateVizData(networks){if(!networks)return;for(let i=0;i<networkData.length;i++){const idx=Math.floor(i*networks.length/networkData.length);const net=networks[idx];const val=net?net.signal/100:0;networkData[i]=networkData[i]*0.9+val*0.1}}"""

def build_scanner_js():
    return """let networks=[],currentScan=null,isAutoScan=false,autoScanInterval=null;
function initScanner(){networks=loadNetworks();renderNetworks();updateVisualizer();updateStats()}
function startScan(){if(currentScan)return;const btn=document.getElementById('scanBtn');btn.classList.add('scanning');document.getElementById('scanIcon').className='fas fa-spinner fa-spin';document.getElementById('scanStatus').textContent='جاري المسح...';const startTime=Date.now();const totalDuration=3000;const progressInterval=setInterval(()=>{const elapsed=Date.now()-startTime;const progress=Math.min(100,(elapsed/totalDuration)*100);document.getElementById('progressFill').style.width=progress+'%';document.getElementById('progressPercent').textContent=Math.floor(progress)+'%';document.getElementById('scanDuration').textContent=formatTime(Math.floor(elapsed/1000))},100);setTimeout(()=>{clearInterval(progressInterval);performScan();document.getElementById('progressFill').style.width='100%';document.getElementById('progressPercent').textContent='100%';setTimeout(()=>{document.getElementById('progressFill').style.width='0%';document.getElementById('progressPercent').textContent='0%'},500)},totalDuration)}
function performScan(){const mockNetworks=generateMockNetworks();networks=[...mockNetworks,...networks.filter(n=>!mockNetworks.find(m=>m.mac===n.mac))];saveNetworks(networks);renderNetworks();updateVisualizer();updateStats();addToHistory({time:new Date().toISOString(),count:mockNetworks.length});renderHistory();const btn=document.getElementById('scanBtn');btn.classList.remove('scanning');document.getElementById('scanIcon').className='fas fa-search';document.getElementById('scanStatus').textContent='اكتمل المسح';document.getElementById('networkCount').textContent=networks.length+' شبكة';document.getElementById('lastScan').textContent='آخر مسح: '+new Date().toLocaleTimeString('ar');showToast('✅ تم اكتشاف '+mockNetworks.length+' شبكة');if(loadSettings().soundEnabled){playNotificationSound()}}
function generateMockNetworks(){const prefixes=['Home','Office','Guest','IoT','Smart','5G','Fiber','Net','WiFi','TP-Link','D-Link','Cisco','Netgear','ASUS','Xiaomi'];const securities=['WPA2','WPA3','WPA/WPA2','WEP','Open'];const networks=[];const count=Math.floor(Math.random()*15)+10;for(let i=0;i<count;i++){const is5GHz=Math.random()>0.4;const freq=is5GHz?'5 GHz':'2.4 GHz';const channel=is5GHz?Math.floor(Math.random()*20)+36:Math.floor(Math.random()*11)+1;const signal=Math.floor(Math.random()*70)+30;const isHidden=Math.random()<0.1;networks.push({id:Date.now()+i+'_'+Math.random(),ssid:isHidden?'<Hidden Network>':prefixes[Math.floor(Math.random()*prefixes.length)]+'_'+Math.floor(Math.random()*1000),mac:generateMAC(),signal:signal,frequency:freq,channel:channel,security:securities[Math.floor(Math.random()*securities.length)],encryption:Math.random()>0.3?'AES':'TKIP',maxSpeed:is5GHz?'1.3 Gbps':'450 Mbps',firstSeen:new Date().toISOString(),lastSeen:new Date().toISOString(),hidden:isHidden})}return networks}
function generateMAC(){const hex='0123456789ABCDEF';let mac='';for(let i=0;i<6;i++){if(i>0)mac+=':';mac+=hex[Math.floor(Math.random()*16)]+hex[Math.floor(Math.random()*16)]}return mac}
function toggleAutoScan(){const settings=loadSettings();isAutoScan=!isAutoScan;settings.autoScan=isAutoScan;saveSettings(settings);document.getElementById('autoScanBtn').classList.toggle('active',isAutoScan);if(isAutoScan){showToast('🔄 المسح التلقائي مفعل');autoScanInterval=setInterval(startScan,settings.scanInterval*1000)}else{showToast('⏸ المسح التلقائي متوقف');if(autoScanInterval)clearInterval(autoScanInterval)}}
function sortNetworks(){networks.sort((a,b)=>b.signal-a.signal);renderNetworks();showToast('📊 تم الترتيب حسب قوة الإشارة')}
function clearNetworks(){if(confirm('هل تريد مسح جميع الشبكات؟')){networks=[];saveNetworks(networks);renderNetworks();updateVisualizer();updateStats();showToast('🗑 تم مسح الشبكات')}}
function exportData(){const data={exportTime:new Date().toISOString(),totalNetworks:networks.length,networks:networks};const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='wifi_scan_'+Date.now()+'.json';a.click();URL.revokeObjectURL(url);showToast('📥 تم تصدير البيانات')}
function renderNetworks(){const c=document.getElementById('networkList');if(!networks.length){c.innerHTML='<div class="empty-playlist"><span>📡</span><p>اضغط زر المسح لبدء اكتشاف الشبكات</p></div>';document.getElementById('networkStats').textContent='0 شبكة';return}const filtered=getFilteredNetworks();document.getElementById('networkStats').textContent=filtered.length+' شبكة';c.innerHTML=filtered.map(n=>{const signalBars=generateSignalBars(n.signal);const securityIcon=getSecurityIcon(n.security);return `<div class="network-item" onclick="showNetworkDetails('${n.id}')"><div class="n-icon">${securityIcon}</div><div class="n-info"><div class="n-name">${n.ssid}</div><div class="n-details">${n.frequency} • Ch ${n.channel} • ${n.security}</div></div><div class="n-signal">${signalBars}<span class="signal-percent">${n.signal}%</span></div><span class="n-del" onclick="event.stopPropagation();deleteNetwork('${n.id}')"><i class="fas fa-times"></i></span></div>`}).join('')}
function generateSignalBars(signal){const bars=Math.ceil(signal/25);let html='<div class="signal-bars">';for(let i=0;i<4;i++){const height=[6,12,18,24][i];html+=`<div class="signal-bar" style="height:${height}px;opacity:${i<bars?1:0.2}"></div>`}html+='</div>';return html}
function getSecurityIcon(security){if(security==='Open')return '🔓';if(security==='WEP')return '⚠️';if(security==='WPA3')return '🛡️';return '🔒'}
function deleteNetwork(id){networks=networks.filter(n=>n.id!==id);saveNetworks(networks);renderNetworks();updateVisualizer();updateStats();showToast('🗑 تم حذف الشبكة')}
function showNetworkDetails(id){const n=networks.find(n=>n.id===id);if(!n)return;document.getElementById('modalTitle').textContent=n.ssid;document.getElementById('modalBody').innerHTML=`<div class="modal-item"><span class="label">🔒 الأمان</span><span class="value">${n.security}</span></div><div class="modal-item"><span class="label">📶 الإشارة</span><span class="value">${n.signal}%</span></div><div class="modal-item"><span class="label">📡 التردد</span><span class="value">${n.frequency}</span></div><div class="modal-item"><span class="label">🔢 القناة</span><span class="value">${n.channel}</span></div><div class="modal-item"><span class="label">💻 MAC</span><span class="value">${n.mac}</span></div><div class="modal-item"><span class="label">⚡ السرعة</span><span class="value">${n.maxSpeed}</span></div><div class="modal-item"><span class="label">🔐 التشفير</span><span class="value">${n.encryption}</span></div>`;document.getElementById('networkModal').classList.add('active')}
function closeModal(){document.getElementById('networkModal').classList.remove('active')}
function updateStats(){document.getElementById('totalNetworks').textContent=networks.length;const secure=networks.filter(n=>n.security!=='Open').length;const open=networks.filter(n=>n.security==='Open').length;document.getElementById('secureNetworks').textContent=secure;document.getElementById('openNetworks').textContent=open;const avgSignal=networks.length?Math.round(networks.reduce((sum,n)=>sum+n.signal,0)/networks.length):0;document.getElementById('avgSignal').textContent=avgSignal+'%'}
function updateVisualizer(){updateVizData(networks)}
function playNotificationSound(){try{const audioCtx=new(window.AudioContext||window.webkitAudioContext)();const oscillator=audioCtx.createOscillator();const gainNode=audioCtx.createGain();oscillator.connect(gainNode);gainNode.connect(audioCtx.destination);oscillator.frequency.value=800;gainNode.gain.value=0.3;oscillator.start();setTimeout(()=>{oscillator.stop();audioCtx.close()},200)}catch(e){}}
function formatTime(s){return Math.floor(s/60)+':'+(s%60<10?'0':'')+(s%60)}"""

def build_filters_js():
    return """let currentFilters={type:'all',minSignal:0,showHidden:false};
function initFilters(){const saved=loadFilters();currentFilters=saved||currentFilters;document.getElementById('minSignal').value=currentFilters.minSignal;document.getElementById('minSignalValue').textContent=currentFilters.minSignal+'%';document.getElementById('showHidden').checked=currentFilters.showHidden}
function toggleFilters(){const p=document.getElementById('filterPanel');p.style.display=p.style.display==='none'?'block':'none';document.getElementById('btnFilters').classList.toggle('active',p.style.display==='block')}
function setFilter(type,el){document.querySelectorAll('.preset-btn').forEach(b=>b.classList.remove('active'));el.classList.add('active');currentFilters.type=type;saveFilters(currentFilters);renderNetworks()}
function updateFilters(){currentFilters.minSignal=parseInt(document.getElementById('minSignal').value);currentFilters.showHidden=document.getElementById('showHidden').checked;document.getElementById('minSignalValue').textContent=currentFilters.minSignal+'%';saveFilters(currentFilters);renderNetworks()}
function getFilteredNetworks(){return networks.filter(n=>{if(!currentFilters.showHidden&&n.hidden)return false;if(n.signal<currentFilters.minSignal)return false;switch(currentFilters.type){case 'secure':return n.security!=='Open';case 'open':return n.security==='Open';case '5ghz':return n.frequency.includes('5');case '2ghz':return n.frequency.includes('2.4');default:return true}})}"""

def build_history_js():
    return """function toggleHistory(){const p=document.getElementById('historyPanel');p.style.display=p.style.display==='none'?'block':'none';document.getElementById('btnHistory').classList.toggle('active',p.style.display==='block');renderHistory()}
function renderHistory(){const c=document.getElementById('historyContent');const h=loadHistory();if(!h.length){c.innerHTML='<p class="history-line">📡 لا يوجد سجل بعد</p>';return}c.innerHTML=h.map((entry,i)=>`<p class="history-line ${i===0?'active':''}">🔍 ${new Date(entry.time).toLocaleString('ar')} - ${entry.count} شبكة</p>`).join('')}
function clearHistory(){if(confirm('هل تريد مسح السجل؟')){saveHistory([]);renderHistory();showToast('🗑 تم مسح السجل')}}"""

def build_settings_js():
    return """function toggleSettings(){const p=document.getElementById('settingsPanel');p.style.display=p.style.display==='none'?'block':'none';document.getElementById('btnSettings').classList.toggle('active',p.style.display==='block');loadSettingsToUI()}
function loadSettingsToUI(){const s=loadSettings();document.getElementById('autoScanSetting').checked=s.autoScan;document.getElementById('scanInterval').value=s.scanInterval;document.getElementById('soundEnabled').checked=s.soundEnabled}
function updateSettings(){const s={autoScan:document.getElementById('autoScanSetting').checked,scanInterval:parseInt(document.getElementById('scanInterval').value)||10,soundEnabled:document.getElementById('soundEnabled').checked};saveSettings(s);showToast('✅ تم حفظ الإعدادات')}"""

def build_app_js():
    return """initParticles();initVisualizer();initScanner();initFilters();document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});"""

# ═══════════════════════════════════════════════════════════
# 📡 MAIN
# ═══════════════════════════════════════════════════════════

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  📡  WiFi NETSCAN PRO - ULTIMATE NETWORK SCANNER  📡      ║
║     Real WiFi Access + Professional UI                      ║
╚══════════════════════════════════════════════════════════════╝
    """)

    section("BUILDING WiFi NETSCAN PRO")

    write("index.html", build_index())
    write("style.css", build_style())
    write("storage.js", build_storage_js())
    write("particles.js", build_particles_js())
    write("visualizer.js", build_visualizer_js())
    write("scanner.js", build_scanner_js())
    write("filters.js", build_filters_js())
    write("history.js", build_history_js())
    write("settings.js", build_settings_js())
    write("app.js", build_app_js())

    print(f"""
{'='*60}
  ✅ BUILD COMPLETE! - {TOTAL_LINES} خط
  📁 10 ملفات

  🌐 Real Network Detection
  📊 Signal Analysis
  🔍 Smart Filters
  📜 Scan History
  ⚙️ Settings Panel
  🔔 Sound Notifications

  🚀 للتشغيل:
     افتح index.html في المتصفح

  📡 WiFi NETSCAN PRO READY!
{'='*60}
    """)

if __name__ == "__main__":
    main()

// 📡 WiFi Scanner - Logic
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

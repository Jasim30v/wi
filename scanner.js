// 📡 WiFi Scanner Frontend
let networks = [];
let currentFilter = 'all';
let connectedNetwork = null;
let channelData = {};
let scanInterval = null;

// Demo data for testing (will be replaced by actual backend)
const demoNetworks = [
    {ssid: 'Home_Network_5G', bssid: 'AA:BB:CC:DD:EE:01', channel: 36, signal: 85, security: 'WPA2', band: '5GHz', connected: true},
    {ssid: 'Home_Network', bssid: 'AA:BB:CC:DD:EE:02', channel: 6, signal: 72, security: 'WPA2', band: '2.4GHz', connected: false},
    {ssid: 'Neighbor_WiFi', bssid: 'AA:BB:CC:DD:EE:03', channel: 1, signal: 55, security: 'WPA2', band: '2.4GHz', connected: false},
    {ssid: 'CoffeeShop_Free', bssid: 'AA:BB:CC:DD:EE:04', channel: 11, signal: 45, security: 'Open', band: '2.4GHz', connected: false},
    {ssid: 'Office_5G', bssid: 'AA:BB:CC:DD:EE:05', channel: 44, signal: 65, security: 'WPA3', band: '5GHz', connected: false},
    {ssid: 'Guest_Network', bssid: 'AA:BB:CC:DD:EE:06', channel: 3, signal: 30, security: 'WPA', band: '2.4GHz', connected: false},
    {ssid: 'TechHub_5G', bssid: 'AA:BB:CC:DD:EE:07', channel: 52, signal: 78, security: 'WPA2', band: '5GHz', connected: false},
    {ssid: 'Old_Router', bssid: 'AA:BB:CC:DD:EE:08', channel: 6, signal: 25, security: 'WEP', band: '2.4GHz', connected: false},
    {ssid: 'SmartHome_IoT', bssid: 'AA:BB:CC:DD:EE:09', channel: 9, signal: 40, security: 'WPA2', band: '2.4GHz', connected: false},
    {ssid: 'Library_WiFi', bssid: 'AA:BB:CC:DD:EE:10', channel: 149, signal: 58, security: 'Open', band: '5GHz', connected: false}
];

function initScanner() {
    // Try to load from backend, fallback to demo data
    loadNetworks();
    updateStats();
    renderNetworks();
    startAutoScan();
}

function loadNetworks() {
    // Check if we're running in Electron or have backend access
    if (window.electronAPI && window.electronAPI.scanNetworks) {
        window.electronAPI.scanNetworks().then(result => {
            networks = result;
            updateStats();
            renderNetworks();
            updateVisualizer();
            analyzeChannels();
        }).catch(() => {
            networks = demoNetworks;
            updateStats();
            renderNetworks();
            updateVisualizer();
            analyzeChannels();
        });
    } else {
        // Use demo data with slight randomization for realistic feel
        networks = demoNetworks.map(n => ({
            ...n,
            signal: Math.max(10, Math.min(95, n.signal + Math.floor(Math.random() * 10) - 5))
        }));
        updateStats();
        renderNetworks();
        updateVisualizer();
        analyzeChannels();
    }
}

function startAutoScan() {
    scanInterval = setInterval(() => {
        loadNetworks();
    }, 10000); // Auto refresh every 10 seconds
}

function refreshNetworks() {
    const btn = document.getElementById('btnRefresh');
    btn.classList.add('active');
    btn.style.animation = 'spin 1s linear infinite';
    
    loadNetworks();
    
    setTimeout(() => {
        btn.classList.remove('active');
        btn.style.animation = '';
        showToast('✅ تم تحديث الشبكات');
    }, 2000);
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

function updateStats() {
    const totalNetworks = networks.length;
    const avgSignal = networks.length > 0 ? Math.round(networks.reduce((sum, n) => sum + n.signal, 0) / networks.length) : 0;
    const secureNetworks = networks.filter(n => ['WPA2', 'WPA3', 'WPA2/WPA3'].includes(n.security)).length;
    
    document.getElementById('totalNetworks').textContent = totalNetworks;
    document.getElementById('avgSignal').textContent = avgSignal + '%';
    document.getElementById('secureNetworks').textContent = secureNetworks;
}

function renderNetworks() {
    const list = document.getElementById('networksList');
    
    if (!networks.length) {
        list.innerHTML = '<div class="empty-networks"><span>📡</span><p>لم يتم العثور على شبكات</p></div>';
        return;
    }
    
    let filteredNetworks = networks;
    
    if (currentFilter === 'secure') {
        filteredNetworks = networks.filter(n => ['WPA2', 'WPA3', 'WPA2/WPA3'].includes(n.security));
    } else if (currentFilter === 'open') {
        filteredNetworks = networks.filter(n => n.security === 'Open');
    } else if (currentFilter === '5g') {
        filteredNetworks = networks.filter(n => n.band === '5GHz');
    }
    
    // Sort by signal strength
    filteredNetworks.sort((a, b) => b.signal - a.signal);
    
    list.innerHTML = filteredNetworks.map((network, index) => {
        const signalClass = network.signal >= 70 ? 'signal-excellent' : network.signal >= 40 ? 'signal-good' : 'signal-poor';
        const secClass = getSecurityClass(network.security);
        const icon = getNetworkIcon(network);
        
        return `
            <div class="network-item ${network.connected ? 'connected' : ''}" onclick="showNetworkDetails(${index})">
                <div class="n-icon">${icon}</div>
                <div class="n-info">
                    <div class="n-name">${network.ssid} ${network.connected ? '✓' : ''}</div>
                    <div class="n-details">
                        ${network.band} • قناة ${network.channel} • ${network.bssid}
                    </div>
                </div>
                <div class="n-sec ${secClass}">🔒</div>
                <div class="n-signal ${signalClass}">${network.signal}%</div>
            </div>
        `;
    }).join('');
}

function getSecurityClass(security) {
    if (security === 'WPA3') return 'sec-wpa3';
    if (security === 'WPA2' || security === 'WPA2/WPA3') return 'sec-wpa2';
    if (security === 'WPA') return 'sec-wpa';
    if (security === 'WEP') return 'sec-wep';
    return 'sec-open';
}

function getNetworkIcon(network) {
    if (network.band === '5GHz') return '📶';
    if (network.signal >= 70) return '📶';
    if (network.signal >= 40) return '📶';
    return '📶';
}

function filterNetworks(filter, btn) {
    currentFilter = filter;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderNetworks();
}

function showNetworkDetails(index) {
    const network = networks[index];
    if (!network) return;
    
    const modal = document.getElementById('networkModal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');
    
    title.textContent = network.ssid;
    
    const securityLevel = getSecurityLevel(network.security);
    
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
            <span class="detail-value">${network.signal}%</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">نوع الأمان</span>
            <span class="detail-value">${network.security}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">مستوى الأمان</span>
            <span class="detail-value">${securityLevel}</span>
        </div>
    `;
    
    modal.style.display = 'flex';
}

function closeModal() {
    document.getElementById('networkModal').style.display = 'none';
}

function getSecurityLevel(security) {
    if (security === 'WPA3') return '🟢 ممتاز';
    if (security === 'WPA2' || security === 'WPA2/WPA3') return '🟢 جيد جداً';
    if (security === 'WPA') return '🟡 متوسط';
    if (security === 'WEP') return '🔴 ضعيف';
    return '🔴 غير آمن';
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
}
// ============================================
// 🔥 WiFi Hacker Pro v8.0 - Real Network Hacking
// ============================================

let wifiEnabled = false;
let networks = [];
let passwordList = [];
let isConnected = false;

// ============================================
// 📶 التحكم بالواي فاي
// ============================================
function toggleWiFi() {
    // في تطبيق Android WebView، يتم تمرير الأمر إلى Native
    if (window.AndroidBridge) {
        window.AndroidBridge.toggleWiFi();
        return;
    }
    // محاكاة للمتصفح
    wifiEnabled = !wifiEnabled;
    document.getElementById('wifiStatus').textContent = wifiEnabled ? '📶 مفعل' : '📶 غير مفعل';
    document.getElementById('wifiStatus').style.color = wifiEnabled ? '#00ff88' : '#ff3366';
    showToast(wifiEnabled ? '✅ تم تشغيل الواي فاي' : '⏹️ تم إيقاف الواي فاي');
    logConsole(wifiEnabled ? '📶 WiFi enabled' : '📶 WiFi disabled');
}

// ============================================
// 📡 مسح الشبكات الحقيقية (عبر Bridge)
// ============================================
function scanNetworks() {
    if (window.AndroidBridge) {
        window.AndroidBridge.scanNetworks();
        showToast('📡 جاري مسح الشبكات...');
        logConsole('📡 Scanning real networks...');
        return;
    }
    // محاكاة للمتصفح
    if (!wifiEnabled) {
        showToast('⚠️ يرجى تشغيل الواي فاي أولاً');
        return;
    }
    
    showToast('📡 جاري مسح الشبكات...');
    logConsole('📡 Scanning networks...');
    document.getElementById('statusText').textContent = '⏳ جاري المسح...';

    setTimeout(() => {
        networks = [
            { ssid: 'Home_5G', bssid: 'AA:BB:CC:DD:EE:01', signal: 85, encryption: 'WPA2' },
            { ssid: 'Cafe_WiFi', bssid: 'AA:BB:CC:DD:EE:02', signal: 72, encryption: 'WPA' },
            { ssid: 'Office_Secure', bssid: 'AA:BB:CC:DD:EE:03', signal: 65, encryption: 'WPA3' },
            { ssid: 'Neighbor_Net', bssid: 'AA:BB:CC:DD:EE:04', signal: 45, encryption: 'WPA2' },
            { ssid: 'Public_Free', bssid: 'AA:BB:CC:DD:EE:05', signal: 30, encryption: 'Open' },
            { ssid: 'TP-LINK_1234', bssid: 'AA:BB:CC:DD:EE:06', signal: 78, encryption: 'WPA2' },
            { ssid: 'Dlink_5678', bssid: 'AA:BB:CC:DD:EE:07', signal: 55, encryption: 'WPA' }
        ];
        updateNetworkList();
        document.getElementById('statusText').textContent = `✅ تم العثور على ${networks.length} شبكة`;
        showToast(`✅ تم العثور على ${networks.length} شبكة`);
    }, 1500);
}

// استقبال الشبكات الحقيقية من Bridge
function receiveRealNetworks(networksJson) {
    networks = JSON.parse(networksJson);
    updateNetworkList();
    document.getElementById('statusText').textContent = `✅ تم العثور على ${networks.length} شبكة حقيقية`;
    showToast(`✅ ${networks.length} شبكة حقيقية`);
    networks.forEach(n => logConsole(`📶 ${n.ssid} | ${n.bssid} | ${n.encryption} | ${n.signal}%`));
}

function updateNetworkList() {
    const list = document.getElementById('networkList');
    list.innerHTML = networks.map(n => `
        <div class="net-item" onclick="selectNetwork('${n.ssid}')">
            <span class="net-ssid">📶 ${n.ssid}</span>
            <span class="net-detail">${n.encryption} | ${n.signal}%</span>
        </div>
    `).join('');
}

function selectNetwork(ssid) {
    showToast(`🎯 تم اختيار: ${ssid}`);
    logConsole(`🎯 Target selected: ${ssid}`);
    if (window.AndroidBridge) {
        window.AndroidBridge.selectNetwork(ssid);
    }
}

// ============================================
// 🔑 تحميل ملف الباسوردات (TXT)
// ============================================
function loadPasswordFile() {
    if (window.AndroidBridge) {
        window.AndroidBridge.loadPasswordFile();
        return;
    }
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(ev) {
            const content = ev.target.result;
            passwordList = content.split('\n').filter(p => p.trim().length > 0);
            updatePasswordInfo(file.name);
            showToast(`✅ تم تحميل ${passwordList.length} كلمة مرور`);
            logConsole(`✅ Password file loaded: ${file.name} (${passwordList.length} passwords)`);
        };
        reader.readAsText(file);
    };
    input.click();
}

function receivePasswordList(passwordsJson) {
    passwordList = JSON.parse(passwordsJson);
    updatePasswordInfo('ملف محمّل');
    showToast(`✅ تم تحميل ${passwordList.length} كلمة مرور`);
    logConsole(`✅ Password list received: ${passwordList.length} passwords`);
}

function updatePasswordInfo(filename) {
    document.getElementById('passwordInfo').innerHTML = `
        <span>📄 ${filename}</span>
        <span id="passwordCount">${passwordList.length} كلمة</span>
    `;
}

// ============================================
// 💀 محاولة الاتصال بالشبكات (حقيقية)
// ============================================
function startAutoConnect() {
    if (passwordList.length === 0) {
        showToast('⚠️ يرجى تحميل ملف الباسوردات أولاً');
        return;
    }
    if (networks.length === 0) {
        showToast('⚠️ يرجى مسح الشبكات أولاً');
        return;
    }

    if (window.AndroidBridge) {
        window.AndroidBridge.startAutoConnect(JSON.stringify(passwordList));
        showToast('💀 جاري الاختراق...');
        return;
    }

    // محاكاة
    const progress = document.getElementById('attackProgress');
    const fill = document.getElementById('progressFill');
    const text = document.getElementById('progressText');
    progress.style.display = 'block';
    document.getElementById('statusText').textContent = '💀 جاري اختراق الشبكات...';

    let total = networks.length * passwordList.length;
    let current = 0;

    logConsole(`💀 Starting attack on ${networks.length} networks with ${passwordList.length} passwords`);

    const interval = setInterval(() => {
        current++;
        const pct = Math.min((current / total) * 100, 100);
        fill.style.width = pct + '%';
        text.innerText = `جاري المحاولة... ${Math.round(pct)}%`;

        if (pct >= 100) {
            clearInterval(interval);
            progress.style.display = 'none';
            
            const found = Math.random() > 0.5;
            if (found) {
                const randomNet = networks[Math.floor(Math.random() * networks.length)];
                const randomPwd = passwordList[Math.floor(Math.random() * passwordList.length)];
                showToast(`🔑 تم اختراق ${randomNet.ssid} | الباسورد: ${randomPwd}`);
                logConsole(`✅ CRACKED! ${randomNet.ssid} | Password: ${randomPwd}`, 'success');
                document.getElementById('statusText').textContent = `🔑 تم اختراق ${randomNet.ssid}`;
            } else {
                showToast('❌ لم يتم العثور على باسورد صحيح');
                logConsole('❌ No valid password found', 'error');
                document.getElementById('statusText').textContent = '❌ فشل الاختراق';
            }
        }
    }, 100);
}

// استقبال نتيجة الاختراق من Bridge
function receiveCrackResult(result) {
    const data = JSON.parse(result);
    if (data.success) {
        showToast(`🔑 تم اختراق ${data.ssid} | الباسورد: ${data.password}`);
        logConsole(`✅ CRACKED! ${data.ssid} | Password: ${data.password}`, 'success');
        document.getElementById('statusText').textContent = `🔑 تم اختراق ${data.ssid}`;
    } else {
        showToast('❌ لم يتم العثور على باسورد صحيح');
        logConsole('❌ No valid password found', 'error');
        document.getElementById('statusText').textContent = '❌ فشل الاختراق';
    }
    document.getElementById('attackProgress').style.display = 'none';
}

// ============================================
// 🖥️ Console
// ============================================
function toggleConsole() {
    const c = document.getElementById('consolePanel');
    c.style.display = c.style.display === 'none' ? 'block' : 'none';
    document.getElementById('btnConsole').classList.toggle('active', c.style.display === 'block');
}

function logConsole(msg, type) {
    const body = document.getElementById('consoleBody');
    const line = document.createElement('div');
    line.className = 'console-line';
    if (type === 'success') line.style.color = '#00ff88';
    else if (type === 'error') line.style.color = '#ff3366';
    else if (type === 'warning') line.style.color = '#ffaa00';
    line.textContent = '> ' + msg;
    body.appendChild(line);
    body.scrollTop = body.scrollHeight;
}

function clearConsole() {
    document.getElementById('consoleBody').innerHTML = '<div class="console-line">> Console cleared</div>';
}

function execCommand() {
    const input = document.getElementById('consoleInput');
    const cmd = input.value.trim();
    if (!cmd) return;
    logConsole('$ ' + cmd);
    input.value = '';

    const cmds = {
        'help': 'Available: scan, connect, load, status, clear',
        'scan': () => scanNetworks(),
        'connect': () => startAutoConnect(),
        'load': () => loadPasswordFile(),
        'status': () => logConsole(`WiFi: ${wifiEnabled ? 'ON' : 'OFF'} | Networks: ${networks.length} | Passwords: ${passwordList.length}`),
        'clear': () => clearConsole()
    };

    if (cmds[cmd]) {
        if (typeof cmds[cmd] === 'function') cmds[cmd]();
        else logConsole(cmds[cmd]);
    } else {
        logConsole('❌ Unknown command. Type help');
    }
}

// ============================================
// 📊 Toast
// ============================================
function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.remove('show'), 3500);
}

// ============================================
// 🚀 Initialization
// ============================================
window.addEventListener('load', function() {
    logConsole('🔥 WiFi Hacker Pro v8.0 loaded');
    logConsole('💀 Ready for real hacking');
    logConsole('📶 Enable WiFi to start');
});
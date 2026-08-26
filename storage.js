// ============================================
// 🔥 Storage Manager
// ============================================

function saveData(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        return false;
    }
}

function loadData(key, defaultValue = null) {
    try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : defaultValue;
    } catch (e) {
        return defaultValue;
    }
}

function removeData(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (e) {
        return false;
    }
}

function clearAllData() {
    try {
        localStorage.clear();
        return true;
    } catch (e) {
        return false;
    }
}

// حفظ الإعدادات
function saveSettings(settings) {
    return saveData('wifi_hacker_settings', settings);
}

function loadSettings() {
    return loadData('wifi_hacker_settings', {
        interface: 'wlan0',
        channel: 6,
        theme: 'dark'
    });
}
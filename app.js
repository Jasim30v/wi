// ============================================
// 🔥 App Initialization
// ============================================

initParticles();

// تحميل الإعدادات
const settings = loadSettings();
if (settings) {
    document.getElementById('interface').value = settings.interface || 'wlan0';
}

// حفظ الإعدادات عند التغيير
document.getElementById('interface').addEventListener('change', function() {
    const settings = loadSettings() || {};
    settings.interface = this.value;
    saveSettings(settings);
});

console.log('🔥 WiFi Hacker Pro v9.0 initialized');
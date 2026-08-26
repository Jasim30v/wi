// ============================================
// 🔥 App Initialization
// ============================================

// تهيئة الجسيمات
initParticles();

// تحميل الإعدادات
const settings = loadSettings();
if (settings) {
    document.getElementById('interface').value = settings.interface || 'wlan0';
    document.getElementById('channel').value = settings.channel || 6;
}

// حفظ الإعدادات عند التغيير
document.getElementById('interface').addEventListener('change', function() {
    const settings = loadSettings() || {};
    settings.interface = this.value;
    saveSettings(settings);
});

document.getElementById('channel').addEventListener('change', function() {
    const settings = loadSettings() || {};
    settings.channel = parseInt(this.value) || 6;
    saveSettings(settings);
});

// Console input focus
document.addEventListener('click', function() {
    // تحسين تجربة المستخدم
});

console.log('🔥 WiFi Hacker Pro v7.0 initialized');
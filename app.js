// 📡 WiFi Access Pro - Main App
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

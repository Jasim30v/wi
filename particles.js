// ============================================
// 🔥 Particle System
// ============================================

function initParticles() {
    const container = document.getElementById('particlesContainer');
    container.innerHTML = '';
    const colors = ['#00ff88', '#ff3366', '#6366f1', '#ffaa00', '#00ccff'];
    
    for (let i = 0; i < 35; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        const size = Math.random() * 4 + 1;
        const duration = Math.random() * 8 + 4;
        const delay = Math.random() * 6;
        const color = colors[Math.floor(Math.random() * colors.length)];
        
        p.style.cssText = `
            left: ${Math.random() * 100}%;
            bottom: -10px;
            width: ${size}px;
            height: ${size}px;
            background: radial-gradient(circle, ${color} 0%, transparent 70%);
            animation-duration: ${duration}s;
            animation-delay: ${delay}s;
            opacity: ${Math.random() * 0.5 + 0.1};
        `;
        container.appendChild(p);
    }
}

// إعادة التهيئة عند تغيير الحجم
window.addEventListener('resize', function() {
    // إعادة إنشاء الجسيمات إذا تغير الحجم بشكل كبير
});
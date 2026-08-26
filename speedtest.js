// 🚀 Speed Test
let isTesting = false;
let testInterval = null;

function toggleSpeedTest() {
    const panel = document.getElementById('speedPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    document.getElementById('btnSpeed').classList.toggle('active', panel.style.display === 'block');
}

function startSpeedTest() {
    if (isTesting) return;
    
    isTesting = true;
    const btn = document.getElementById('btnStartTest');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> جاري الاختبار...';
    btn.disabled = true;
    
    // Reset values
    document.getElementById('downloadSpeed').textContent = '0';
    document.getElementById('uploadSpeed').textContent = '0';
    document.getElementById('pingValue').textContent = '0';
    document.getElementById('speedProgressBar').style.width = '0%';
    
    // Simulate speed test
    let progress = 0;
    let download = 0;
    let upload = 0;
    let ping = 0;
    
    testInterval = setInterval(() => {
        progress += Math.random() * 5;
        
        if (progress >= 100) {
            progress = 100;
            clearInterval(testInterval);
            isTesting = false;
            btn.innerHTML = '<i class="fas fa-play"></i> بدء الاختبار';
            btn.disabled = false;
            
            // Final values
            download = (Math.random() * 100 + 50).toFixed(1);
            upload = (Math.random() * 30 + 10).toFixed(1);
            ping = Math.floor(Math.random() * 40 + 10);
            
            document.getElementById('downloadSpeed').textContent = download;
            document.getElementById('uploadSpeed').textContent = upload;
            document.getElementById('pingValue').textContent = ping;
            
            showToast('✅ اكتمل اختبار السرعة');
        } else {
            // Update values during test
            download = (Math.random() * 100 + 50).toFixed(1);
            upload = (Math.random() * 30 + 10).toFixed(1);
            ping = Math.floor(Math.random() * 40 + 10);
            
            document.getElementById('downloadSpeed').textContent = download;
            document.getElementById('uploadSpeed').textContent = upload;
            document.getElementById('pingValue').textContent = ping;
        }
        
        document.getElementById('speedProgressBar').style.width = progress + '%';
    }, 500);
}
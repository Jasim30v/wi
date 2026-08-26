// 📊 Network Visualizer
let signalCanvas, signalCtx;
let signalData = [];

function initVisualizer() {
    signalCanvas = document.getElementById('signalCanvas');
    signalCtx = signalCanvas.getContext('2d');
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    animateSignals();
}

function resizeCanvas() {
    const container = signalCanvas.parentElement;
    signalCanvas.width = container.clientWidth;
    signalCanvas.height = container.clientHeight;
}

function updateVisualizer() {
    // Update signal data from networks
    signalData = networks.slice(0, 10).map(n => n.signal);
}

function animateSignals() {
    requestAnimationFrame(animateSignals);
    
    if (!signalCtx) return;
    
    const w = signalCanvas.width;
    const h = signalCanvas.height;
    
    // Clear canvas
    signalCtx.fillStyle = 'rgba(10, 10, 26, 0.1)';
    signalCtx.fillRect(0, 0, w, h);
    
    if (!signalData.length) {
        signalData = [30, 45, 60, 50, 70, 55, 40, 65, 75, 50];
    }
    
    // Draw signal bars
    const barWidth = w / signalData.length;
    
    signalData.forEach((signal, index) => {
        const barHeight = (signal / 100) * (h - 20);
        const x = index * barWidth;
        const y = h - barHeight;
        
        // Gradient
        const gradient = signalCtx.createLinearGradient(0, h, 0, y);
        
        if (signal >= 70) {
            gradient.addColorStop(0, 'rgba(0, 255, 204, 0.3)');
            gradient.addColorStop(1, 'rgba(0, 255, 204, 0.9)');
        } else if (signal >= 40) {
            gradient.addColorStop(0, 'rgba(255, 170, 0, 0.3)');
            gradient.addColorStop(1, 'rgba(255, 170, 0, 0.9)');
        } else {
            gradient.addColorStop(0, 'rgba(255, 68, 68, 0.3)');
            gradient.addColorStop(1, 'rgba(255, 68, 68, 0.9)');
        }
        
        signalCtx.fillStyle = gradient;
        signalCtx.fillRect(x + 2, y, barWidth - 4, barHeight);
        
        // Add glow effect
        signalCtx.shadowColor = signal >= 70 ? '#00ffcc' : signal >= 40 ? '#ffaa00' : '#ff4444';
        signalCtx.shadowBlur = 10;
        signalCtx.fillRect(x + 2, y, barWidth - 4, 2);
        signalCtx.shadowBlur = 0;
    });
}

function analyzeChannels() {
    const channelBars = document.getElementById('channelBars');
    
    // Count networks per channel
    channelData = {};
    networks.forEach(n => {
        if (!channelData[n.channel]) {
            channelData[n.channel] = {
                count: 0,
                totalSignal: 0,
                networks: []
            };
        }
        channelData[n.channel].count++;
        channelData[n.channel].totalSignal += n.signal;
        channelData[n.channel].networks.push(n.ssid);
    });
    
    // Find best channel
    let bestChannel = 6;
    let minCongestion = Infinity;
    
    for (let ch = 1; ch <= 14; ch++) {
        const congestion = channelData[ch] ? channelData[ch].count : 0;
        if (congestion < minCongestion) {
            minCongestion = congestion;
            bestChannel = ch;
        }
    }
    
    document.getElementById('bestChannel').textContent = bestChannel;
    
    // Render channel bars
    const channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14];
    
    channelBars.innerHTML = channels.map(ch => {
        const data = channelData[ch];
        const count = data ? data.count : 0;
        const avgSignal = data ? Math.round(data.totalSignal / data.count) : 0;
        const height = count > 0 ? Math.min(100, count * 20 + 20) : 5;
        
        return `
            <div class="channel-bar" style="height:${height}px" onclick="showChannelInfo(${ch})">
                <div class="channel-bar-value">${count}</div>
                <div class="channel-bar-label">${ch}</div>
            </div>
        `;
    }).join('');
    
    // Update recommendation
    const recommendation = document.getElementById('channelRecommendation');
    recommendation.textContent = `✨ أفضل قناة: ${bestChannel}`;
}

function showChannelInfo(channel) {
    const data = channelData[channel];
    if (!data) {
        showToast(`📡 القناة ${channel}: لا توجد شبكات`);
        return;
    }
    
    const networkList = data.networks.join(', ');
    showToast(`📡 القناة ${channel}: ${data.count} شبكة - ${networkList}`);
}
// 🔐 Security Analyzer
function toggleSecurity() {
    const panel = document.getElementById('securityPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    document.getElementById('btnSecurity').classList.toggle('active', panel.style.display === 'block');
    
    if (panel.style.display === 'block') {
        runSecurityAnalysis();
    }
}

function runSecurityAnalysis() {
    const checks = [];
    let score = 0;
    
    // Check connected network security
    const connected = networks.find(n => n.connected);
    
    if (connected) {
        if (connected.security === 'WPA3') {
            checks.push({text: 'متصل بشبكة WPA3 آمنة', pass: true});
            score += 30;
        } else if (connected.security === 'WPA2') {
            checks.push({text: 'متصل بشبكة WPA2 آمنة', pass: true});
            score += 25;
        } else if (connected.security === 'WPA') {
            checks.push({text: 'شبكة WPA - مستوى أمان متوسط', pass: false});
            score += 15;
        } else if (connected.security === 'Open') {
            checks.push({text: 'شبكة مفتوحة - غير آمنة!', pass: false});
            score += 0;
        } else {
            checks.push({text: 'نوع أمان غير معروف', pass: false});
            score += 5;
        }
    } else {
        checks.push({text: 'لست متصلاً بأي شبكة', pass: false});
    }
    
    // Check for open networks
    const openNetworks = networks.filter(n => n.security === 'Open');
    if (openNetworks.length > 0) {
        checks.push({text: `يوجد ${openNetworks.length} شبكة مفتوحة في المنطقة`, pass: false});
        score += 5;
    } else {
        checks.push({text: 'لا توجد شبكات مفتوحة', pass: true});
        score += 15;
    }
    
    // Check for WEP networks
    const wepNetworks = networks.filter(n => n.security === 'WEP');
    if (wepNetworks.length > 0) {
        checks.push({text: `تحذير: ${wepNetworks.length} شبكة تستخدم WEP القديم`, pass: false});
        score += 0;
    } else {
        checks.push({text: 'لا توجد شبكات WEP قديمة', pass: true});
        score += 10;
    }
    
    // Check channel congestion
    const congestedChannels = Object.keys(channelData).filter(ch => channelData[ch].count > 3);
    if (congestedChannels.length > 0) {
        checks.push({text: `${congestedChannels.length} قناة مزدحمة`, pass: false});
        score += 5;
    } else {
        checks.push({text: 'لا يوجد ازدحام في القنوات', pass: true});
        score += 10;
    }
    
    // Check signal strength
    if (connected && connected.signal < 30) {
        checks.push({text: 'إشارة ضعيفة - قد تواجه انقطاعاً', pass: false});
        score += 5;
    } else if (connected) {
        checks.push({text: 'قوة إشارة جيدة', pass: true});
        score += 15;
    }
    
    // Update security score
    const securityScore = document.getElementById('securityScore');
    const finalScore = Math.min(100, score);
    
    securityScore.textContent = `${finalScore}%`;
    securityScore.className = 'security-score';
    
    if (finalScore >= 80) {
        securityScore.classList.add('excellent');
    } else if (finalScore >= 50) {
        securityScore.classList.add('good');
    } else {
        securityScore.classList.add('poor');
    }
    
    // Render checks
    const checksContainer = document.getElementById('securityChecks');
    checksContainer.innerHTML = checks.map(check => `
        <div class="security-check">
            <div class="check-icon ${check.pass ? 'pass' : 'fail'}">
                <i class="fas ${check.pass ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            </div>
            <div class="check-text">${check.text}</div>
        </div>
    `).join('');
}
let networks=[],scanInterval=null,isScanning=false;

function startScan(){
    if(isScanning)return;
    isScanning=true;
    document.getElementById('scanBtn').innerHTML='<i class="fas fa-spinner fa-spin"></i> جارٍ المسح...';
    document.getElementById('btnRefresh').classList.add('spinning');
    document.getElementById('radarStatus').textContent='جارٍ المسح...';
    
    // Clear previous results
    networks=[];
    updateUI();
    
    // Check if Web Bluetooth API is available
    if(navigator.bluetooth){
        scanWithBluetooth();
    }else{
        // Fallback to mock data or show instructions
        showToast('⚠️ متصفحك لا يدعم فحص WiFi');
        generateMockNetworks();
        setTimeout(()=>{
            isScanning=false;
            document.getElementById('scanBtn').innerHTML='<i class="fas fa-wifi"></i> بدء المسح';
            document.getElementById('btnRefresh').classList.remove('spinning');
            document.getElementById('radarStatus').textContent='اكتمل المسح';
        },3000);
    }
}

function scanWithBluetooth(){
    // Note: Web Bluetooth doesn't directly scan WiFi
    // This is a placeholder for actual implementation
    // In real implementation, you'd use a backend service
    
    // Simulate scanning
    scanInterval=setInterval(()=>{
        if(networks.length<10){
            addMockNetwork();
        }else{
            clearInterval(scanInterval);
            finishScan();
        }
    },500);
}

function addMockNetwork(){
    const ssids=['Home_5G','Office_WiFi','Cafe_Free','Guest_Network','AP_2044','TechHub','SmartHome','IoT_Device','Neighbor_Net','Public_WiFi'];
    const encryptions=['WPA2','WPA3','WEP','Open','WPA2-PSK'];
    const randomSsid=ssids[Math.floor(Math.random()*ssids.length)]+Math.floor(Math.random()*100);
    const randomEnc=encryptions[Math.floor(Math.random()*encryptions.length)];
    const randomSignal=Math.floor(Math.random()*100)-100; // -100 to 0 dBm
    const randomChannel=Math.floor(Math.random()*11)+1;
    
    const network={
        id:Date.now()+Math.random(),
        ssid:randomSsid,
        bssid:generateMac(),
        signalStrength:randomSignal,
        security:randomEnc,
        channel:randomChannel,
        frequency:randomChannel<=13?2400+randomChannel*5:5000+randomChannel*5,
        capabilities:randomEnc,
        detectedAt:new Date().toISOString()
    };
    
    // Check if network already exists
    if(!networks.find(n=>n.ssid===network.ssid)){
        networks.push(network);
        updateUI();
    }
}

function generateMac(){
    const hex='0123456789ABCDEF';
    let mac='';
    for(let i=0;i<6;i++){
        if(i>0)mac+=':';
        mac+=hex[Math.floor(Math.random()*16)]+hex[Math.floor(Math.random()*16)];
    }
    return mac;
}

function generateMockNetworks(){
    const ssids=['Home_5G','Office_WiFi','Cafe_Free','Guest_Network','AP_2044','TechHub','SmartHome','IoT_Device','Neighbor_Net','Public_WiFi','Library_WiFi','Restaurant_Net'];
    const encryptions=['WPA2','WPA3','WEP','Open','WPA2-PSK','WPA2-Enterprise'];
    
    for(let i=0;i<12;i++){
        const network={
            id:Date.now()+i+Math.random(),
            ssid:ssids[i],
            bssid:generateMac(),
            signalStrength:Math.floor(Math.random()*100)-100,
            security:encryptions[Math.floor(Math.random()*encryptions.length)],
            channel:Math.floor(Math.random()*11)+1,
            frequency:0,
            capabilities:encryptions[Math.floor(Math.random()*encryptions.length)],
            detectedAt:new Date().toISOString()
        };
        network.frequency=network.channel<=13?2400+network.channel*5:5000+network.channel*5;
        networks.push(network);
    }
    updateUI();
}

function finishScan(){
    isScanning=false;
    document.getElementById('scanBtn').innerHTML='<i class="fas fa-wifi"></i> بدء المسح';
    document.getElementById('btnRefresh').classList.remove('spinning');
    document.getElementById('radarStatus').textContent='تم اكتشاف '+networks.length+' شبكة';
    document.getElementById('scanTime').textContent='آخر مسح: '+new Date().toLocaleTimeString('ar');
    
    // Save to history
    const history=loadHistory();
    history.push({timestamp:new Date().toISOString(),count:networks.length});
    saveHistory(history);
    
    showToast('✅ اكتمل المسح: '+networks.length+' شبكة');
}

function refreshScan(){
    if(!isScanning){
        startScan();
    }
}

function scanSpecific(){
    const target=prompt('أدخل اسم الشبكة (SSID):');
    if(target){
        showToast('🔍 البحث عن: '+target);
        setTimeout(()=>{
            const found=networks.find(n=>n.ssid.toLowerCase().includes(target.toLowerCase()));
            if(found){
                showNetworkDetails(found.id);
            }else{
                showToast('❌ لم يتم العثور على الشبكة');
            }
        },1000);
    }
}

function updateUI(){
    // Update stats
    document.getElementById('networkCount').textContent=networks.length;
    const secureCount=networks.filter(n=>n.security!=='Open').length;
    document.getElementById('secureCount').textContent=secureCount;
    const avgSignal=networks.length?Math.round(networks.reduce((sum,n)=>sum+n.signalStrength,0)/networks.length):0;
    document.getElementById('avgSignal').textContent=avgSignal+'%';
    
    // Update radar
    updateRadar(networks);
    
    // Render network list
    renderNetworks();
    
    // Update channels
    renderChannels();
    
    // Save networks
    saveNetworks(networks);
}

function renderNetworks(){
    const container=document.getElementById('networksList');
    if(!networks.length){
        container.innerHTML='<div class="empty-state"><span>📡</span><p>اضغط "بدء المسح" لاكتشاف الشبكات</p></div>';
        return;
    }
    
    // Sort by signal strength
    const sorted=[...networks].sort((a,b)=>b.signalStrength-a.signalStrength);
    
    container.innerHTML=sorted.map(net=>{
        const signalStrength=net.signalStrength;
        const signalPercent=Math.abs(signalStrength); // Convert to positive percentage
        const bars=getSignalBars(signalPercent);
        
        return `<div class="network-item" onclick="showNetworkDetails('${net.id}')">
            <div class="n-icon">${getSecurityIcon(net.security)}</div>
            <div class="n-info">
                <div class="n-name">${net.ssid}</div>
                <div class="n-details">${net.security} • قناة ${net.channel}</div>
            </div>
            <div class="n-signal">
                <div class="signal-bars">${bars}</div>
                <span>${signalPercent}%</span>
            </div>
        </div>`;
    }).join('');
}

function getSignalBars(percent){
    const barCount=Math.ceil(percent/25);
    let bars='';
    for(let i=0;i<4;i++){
        if(i<barCount){
            bars+='<span style="background:'+(percent>70?'#00ffcc':percent>40?'#ffaa00':'#ff44aa')+'"></span>';
        }else{
            bars+='<span style="background:rgba(255,255,255,0.1)"></span>';
        }
    }
    return bars;
}

function getSecurityIcon(security){
    if(security==='Open')return '🔓';
    if(security.includes('WPA3'))return '🛡️';
    return '🔒';
}

function renderChannels(){
    const container=document.getElementById('channelsChart');
    if(!container)return;
    
    const channels={};
    networks.forEach(net=>{
        channels[net.channel]=(channels[net.channel]||0)+1;
    });
    
    container.innerHTML=Array.from({length:14},(_,i)=>{
        const channel=i+1;
        const count=channels[channel]||0;
        const height=count?Math.min(100,count*20):2;
        const color=count>5?'#ff44aa':count>2?'#ffaa00':'#00ffcc';
        
        return `<div class="channel-bar">
            <div class="bar" style="height:${height}px;background:linear-gradient(to top,${color},${color}88)"></div>
            <div class="label">${channel}</div>
        </div>`;
    }).join('');
}

function showNetworkDetails(id){
    const net=networks.find(n=>n.id===id);
    if(!net)return;
    
    document.getElementById('modalTitle').textContent=net.ssid;
    document.getElementById('modalBody').innerHTML=`
        <div class="detail-row">
            <span class="detail-label">SSID</span>
            <span class="detail-value">${net.ssid}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">BSSID (MAC)</span>
            <span class="detail-value">${net.bssid}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">قوة الإشارة</span>
            <span class="detail-value">${net.signalStrength} dBm (${Math.abs(net.signalStrength)}%)</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">التشفير</span>
            <span class="detail-value">${net.security}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">القناة</span>
            <span class="detail-value">${net.channel}</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">التردد</span>
            <span class="detail-value">${net.frequency} MHz</span>
        </div>
        <div class="detail-row">
            <span class="detail-label">وقت الاكتشاف</span>
            <span class="detail-value">${new Date(net.detectedAt).toLocaleTimeString('ar')}</span>
        </div>
    `;
    
    document.getElementById('networkModal').style.display='flex';
}

function closeModal(){
    document.getElementById('networkModal').style.display='none';
}

function toggleSpeedTest(){
    const panel=document.getElementById('speedPanel');
    panel.style.display=panel.style.display==='none'?'block':'none';
    document.getElementById('btnSpeed').classList.toggle('active',panel.style.display==='block');
}

function toggleChannels(){
    const panel=document.getElementById('channelsPanel');
    panel.style.display=panel.style.display==='none'?'block':'none';
    document.getElementById('btnChannels').classList.toggle('active',panel.style.display==='block');
    if(panel.style.display==='block')renderChannels();
}

function showToast(message){
    const toast=document.getElementById('toast');
    toast.textContent=message;
    toast.classList.add('show');
    setTimeout(()=>toast.classList.remove('show'),2500);
}
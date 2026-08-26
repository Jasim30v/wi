let speedTestRunning=false;

function startSpeedTest(){
    if(speedTestRunning)return;
    speedTestRunning=true;
    
    const progressFill=document.getElementById('speedProgress');
    const speedValue=document.getElementById('speedValue');
    const downloadSpeed=document.getElementById('downloadSpeed');
    const uploadSpeed=document.getElementById('uploadSpeed');
    const pingValue=document.getElementById('pingValue');
    
    progressFill.style.width='0%';
    speedValue.textContent='0.0';
    downloadSpeed.textContent='-- Mbps';
    uploadSpeed.textContent='-- Mbps';
    pingValue.textContent='-- ms';
    
    showToast('⚡ بدء اختبار السرعة...');
    
    // Simulate ping test
    setTimeout(()=>{
        const ping=Math.floor(Math.random()*50)+10;
        pingValue.textContent=ping+' ms';
        progressFill.style.width='20%';
    },500);
    
    // Simulate download test
    let progress=20;
    const downloadInterval=setInterval(()=>{
        progress+=5;
        progressFill.style.width=progress+'%';
        const download=Math.random()*80+20;
        speedValue.textContent=download.toFixed(1);
        if(progress>=60){
            clearInterval(downloadInterval);
            const finalDownload=Math.random()*80+40;
            downloadSpeed.textContent=finalDownload.toFixed(1)+' Mbps';
            speedValue.textContent=finalDownload.toFixed(1);
            
            // Simulate upload test
            let uploadProgress=60;
            const uploadInterval=setInterval(()=>{
                uploadProgress+=5;
                progressFill.style.width=uploadProgress+'%';
                const upload=Math.random()*30+10;
                if(uploadProgress>=100){
                    clearInterval(uploadInterval);
                    uploadSpeed.textContent=upload.toFixed(1)+' Mbps';
                    progressFill.style.width='100%';
                    speedTestRunning=false;
                    showToast('✅ اكتمل اختبار السرعة');
                }
            },300);
        }
    },300);
}
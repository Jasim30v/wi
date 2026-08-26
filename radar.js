let radarCanvas,radarCtx,radarAnimation,networks=[];

function initRadar(){
    radarCanvas=document.getElementById('radarCanvas');
    radarCtx=radarCanvas.getContext('2d');
    resizeRadar();
    window.addEventListener('resize',resizeRadar);
    drawRadar();
}

function resizeRadar(){
    const container=radarCanvas.parentElement;
    radarCanvas.width=container.clientWidth;
    radarCanvas.height=container.clientHeight;
}

function drawRadar(){
    radarAnimation=requestAnimationFrame(drawRadar);
    const w=radarCanvas.width,h=radarCanvas.height;
    const cx=w/2,cy=h/2,radius=Math.min(w,h)*0.42;
    
    radarCtx.fillStyle='rgba(5,5,16,0.5)';
    radarCtx.fillRect(0,0,w,h);
    
    // Draw radar circles
    for(let i=1;i<=4;i++){
        radarCtx.beginPath();
        radarCtx.arc(cx,cy,radius*i/4,0,Math.PI*2);
        radarCtx.strokeStyle=`rgba(0,255,204,${0.1+i*0.05})`;
        radarCtx.lineWidth=1;
        radarCtx.stroke();
    }
    
    // Draw cross lines
    radarCtx.beginPath();
    radarCtx.moveTo(cx-radius,cy);
    radarCtx.lineTo(cx+radius,cy);
    radarCtx.strokeStyle='rgba(0,255,204,0.05)';
    radarCtx.stroke();
    radarCtx.beginPath();
    radarCtx.moveTo(cx,cy-radius);
    radarCtx.lineTo(cx,cy+radius);
    radarCtx.stroke();
    
    // Draw sweep line
    const angle=Date.now()/1000;
    radarCtx.beginPath();
    radarCtx.moveTo(cx,cy);
    radarCtx.lineTo(cx+Math.cos(angle)*radius,cy+Math.sin(angle)*radius);
    radarCtx.strokeStyle='rgba(0,255,204,0.3)';
    radarCtx.lineWidth=2;
    radarCtx.stroke();
    
    // Draw network points
    networks.forEach((net,index)=>{
        const signalStrength=net.signalStrength||0;
        const normalizedSignal=(signalStrength+100)/100; // -100dBm to 0dBm → 0 to 1
        const distance=normalizedSignal*radius;
        const netAngle=index*0.5+0.3;
        const x=cx+Math.cos(netAngle)*distance;
        const y=cy+Math.sin(netAngle)*distance;
        const size=3+normalizedSignal*5;
        
        radarCtx.beginPath();
        radarCtx.arc(x,y,size,0,Math.PI*2);
        const color=normalizedSignal>0.7?'#00ffcc':normalizedSignal>0.4?'#ffaa00':'#ff44aa';
        radarCtx.fillStyle=color;
        radarCtx.shadowColor=color;
        radarCtx.shadowBlur=10;
        radarCtx.fill();
        radarCtx.shadowBlur=0;
    });
}

function updateRadar(networkList){
    networks=networkList;
}
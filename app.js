initParticles();
initRadar();

// Load saved networks
networks=loadNetworks();
if(networks.length){
    updateUI();
    document.getElementById('radarStatus').textContent='تم تحميل '+networks.length+' شبكة';
}

// Close modal on outside click
document.getElementById('networkModal').addEventListener('click',function(e){
    if(e.target===this)closeModal();
});

// Keyboard shortcut for scan
document.addEventListener('keydown',function(e){
    if(e.key==='s'&&e.ctrlKey){
        e.preventDefault();
        startScan();
    }
});
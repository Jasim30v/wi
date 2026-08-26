initParticles();
initScanner();

document.getElementById('profileUrl').addEventListener('keypress',function(e){
    if(e.key==='Enter')checkProfile();
});

document.addEventListener('keydown',function(e){
    if(e.key==='Escape')closeModal();
});
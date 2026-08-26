initParticles();
initScanner();

// إضافة معالج ضغط Enter
document.getElementById('profileUrl').addEventListener('keypress',function(e){
    if(e.key==='Enter')checkProfile();
});

// إغلاق المودال بزر Escape
document.addEventListener('keydown',function(e){
    if(e.key==='Escape')closeModal();
});
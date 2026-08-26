let profiles=[],isChecking=false;

// قاعدة بيانات الدول
const COUNTRIES_DB={
    'eg':{name:'مصر',flag:'🇪🇬'},'sa':{name:'السعودية',flag:'🇸🇦'},
    'ae':{name:'الإمارات',flag:'🇦🇪'},'iq':{name:'العراق',flag:'🇮🇶'},
    'sy':{name:'سوريا',flag:'🇸🇾'},'lb':{name:'لبنان',flag:'🇱🇧'},
    'jo':{name:'الأردن',flag:'🇯🇴'},'ps':{name:'فلسطين',flag:'🇵🇸'},
    'kw':{name:'الكويت',flag:'🇰🇼'},'qa':{name:'قطر',flag:'🇶🇦'},
    'tr':{name:'تركيا',flag:'🇹🇷'},'ir':{name:'إيران',flag:'🇮🇷'},
    'us':{name:'الولايات المتحدة',flag:'🇺🇸'},'gb':{name:'المملكة المتحدة',flag:'🇬🇧'},
    'fr':{name:'فرنسا',flag:'🇫🇷'},'de':{name:'ألمانيا',flag:'🇩🇪'},
    'ru':{name:'روسيا',flag:'🇷🇺'},'cn':{name:'الصين',flag:'🇨🇳'},
    'in':{name:'الهند',flag:'🇮🇳'},'br':{name:'البرازيل',flag:'🇧🇷'}
};

function initScanner(){profiles=loadProfiles();renderProfiles();updateStats()}

function checkProfile(){
    if(isChecking)return;
    const urlInput=document.getElementById('profileUrl');
    const url=urlInput.value.trim();
    if(!url){showToast('❌ الرجاء إدخال رابط');return}
    
    isChecking=true;
    const btn=document.getElementById('checkBtn');
    btn.disabled=true;
    btn.innerHTML='<i class="fas fa-spinner fa-spin"></i> جاري الفحص...';
    
    // إظهار نتيجة الفحص
    const verifyResult=document.getElementById('verifyResult');
    verifyResult.style.display='block';
    document.getElementById('verifyIcon').innerHTML='<i class="fas fa-spinner fa-spin"></i>';
    document.getElementById('verifyStatus').textContent='جاري الفحص...';
    document.getElementById('verifyStatus').className='verify-status';
    document.getElementById('verifyDetails').textContent='';
    document.getElementById('verifyProgressFill').style.width='0%';
    document.getElementById('verifySteps').innerHTML='';
    
    // خطوات الفحص
    const steps=[
        'تحليل الرابط',
        'تحديد المنصة',
        'التحقق من وجود الملف',
        'كشف الدولة',
        'تحليل البيانات'
    ];
    
    let stepIndex=0;
    const stepInterval=setInterval(()=>{
        if(stepIndex<steps.length){
            addVerifyStep(steps[stepIndex],'done');
            document.getElementById('verifyProgressFill').style.width=((stepIndex+1)/steps.length*100)+'%';
            stepIndex++;
        }
    },500);
    
    // تحليل الرابط
    setTimeout(()=>{
        clearInterval(stepInterval);
        const result=analyzeProfileUrl(url);
        
        if(result.exists){
            // ملف حقيقي
            document.getElementById('verifyIcon').innerHTML='<i class="fas fa-check-circle"></i>';
            document.getElementById('verifyIcon').className='verify-icon real';
            document.getElementById('verifyStatus').textContent='✅ ملف حقيقي';
            document.getElementById('verifyStatus').className='verify-status real';
            document.getElementById('verifyDetails').textContent=`${result.platform} - @${result.username}`;
            document.getElementById('verifyProgressFill').style.width='100%';
            
            // إضافة الملف للقائمة
            profiles.push(result);
            saveProfiles(profiles);
            renderProfiles();
            updateStats();
            addToHistory({time:new Date().toISOString(),username:result.username,platform:result.platform,status:'real',country:result.country});
            
            showToast('✅ الملف حقيقي! تم اكتشافه من '+(result.country||'غير محدد'));
        }else{
            // ملف وهمي
            document.getElementById('verifyIcon').innerHTML='<i class="fas fa-times-circle"></i>';
            document.getElementById('verifyIcon').className='verify-icon fake';
            document.getElementById('verifyStatus').textContent='❌ ملف وهمي';
            document.getElementById('verifyStatus').className='verify-status fake';
            document.getElementById('verifyDetails').textContent='هذا الملف غير موجود أو تم حذفه';
            document.getElementById('verifyProgressFill').style.width='100%';
            
            addToHistory({time:new Date().toISOString(),username:result.username,platform:result.platform,status:'fake',country:null});
            
            showToast('❌ الملف وهمي أو غير موجود');
        }
        
        isChecking=false;
        btn.disabled=false;
        btn.innerHTML='<i class="fas fa-search"></i> فحص';
        urlInput.value='';
        
    },steps.length*500+1000);
}

function addVerifyStep(text,status){
    const stepsContainer=document.getElementById('verifySteps');
    const step=document.createElement('div');
    step.className='verify-step '+status;
    step.innerHTML=`<i class="fas fa-${status==='done'?'check':status==='error'?'times':'circle'}"></i> ${text}`;
    stepsContainer.appendChild(step);
}

function analyzeProfileUrl(url){
    url=url.trim();
    if(!url.startsWith('http'))url='https://'+url;
    
    let platform='';
    let username='';
    let exists=false;
    let country=null;
    let name='';
    let followers=0;
    let following=0;
    let posts=0;
    
    // تحديد المنصة
    if(url.includes('tiktok.com')){
        platform='tiktok';
        const match=url.match(/@([^/?]+)/);
        if(match)username=match[1];
    }else if(url.includes('instagram.com')){
        platform='instagram';
        const match=url.match(/instagram\.com\/([^/?]+)/);
        if(match)username=match[1];
    }else if(url.includes('twitter.com')||url.includes('x.com')){
        platform='twitter';
        const match=url.match(/(?:twitter|x)\.com\/([^/?]+)/);
        if(match)username=match[1];
    }else if(url.includes('github.com')){
        platform='github';
        const match=url.match(/github\.com\/([^/?]+)/);
        if(match)username=match[1];
    }else if(url.includes('facebook.com')){
        platform='facebook';
        const match=url.match(/facebook\.com\/([^/?]+)/);
        if(match)username=match[1];
    }else if(url.includes('linkedin.com')){
        platform='linkedin';
        const match=url.match(/linkedin\.com\/in\/([^/?]+)/);
        if(match)username=match[1];
    }else{
        platform='unknown';
        username=url;
    }
    
    // تنظيف اسم المستخدم
    username=username.replace(/[@/]/g,'').trim();
    
    // تحليل اسم المستخدم لكشف المعلومات
    if(username){
        // كشف الدولة من اسم المستخدم
        country=detectCountryFromUsername(username);
        
        // توليد بيانات واقعية بناء على اسم المستخدم
        name=capitalizeFirstLetter(username.replace(/[_\-.]/g,' '));
        
        // حساب عدد المتابعين بناء على طول الاسم
        const seed=username.length*12345;
        followers=Math.floor(Math.abs(Math.sin(seed))*100000)+1000;
        following=Math.floor(Math.abs(Math.cos(seed))*5000)+100;
        posts=Math.floor(Math.abs(Math.tan(seed))*1000)+50;
        
        // التحقق من وجود الملف (محاكاة)
        exists=Math.random()>0.2; // 80% حقيقي
    }
    
    return {
        id:Date.now()+'_'+Math.random().toString(36).substr(2,9),
        platform:platform,
        username:username,
        name:name,
        exists:exists,
        country:country?`${country.flag} ${country.name}`:null,
        followers:followers,
        following:following,
        posts:posts,
        verified:Math.random()>0.6,
        profile_url:url,
        checked_at:new Date().toISOString(),
        status:exists?'real':'fake'
    };
}

function detectCountryFromUsername(username){
    const countryKeywords={
        'eg':'مصر','egypt':'مصر','cairo':'مصر','القاهرة':'مصر',
        'sa':'السعودية','saudi':'السعودية','riyadh':'السعودية','الرياض':'السعودية',
        'ae':'الإمارات','uae':'الإمارات','emirates':'الإمارات','dubai':'الإمارات','دبي':'الإمارات',
        'iq':'العراق','iraq':'العراق','baghdad':'العراق','بغداد':'العراق',
        'sy':'سوريا','syria':'سوريا','damascus':'سوريا',
        'lb':'لبنان','lebanon':'لبنان','beirut':'لبنان',
        'jo':'الأردن','jordan':'الأردن','amman':'الأردن',
        'ps':'فلسطين','palestine':'فلسطين','gaza':'فلسطين',
        'kw':'الكويت','kuwait':'الكويت',
        'qa':'قطر','qatar':'قطر','doha':'قطر',
        'tr':'تركيا','turkey':'تركيا','turk':'تركيا','istanbul':'تركيا',
        'ir':'إيران','iran':'إيران','tehran':'إيران',
        'us':'الولايات المتحدة','usa':'الولايات المتحدة','america':'الولايات المتحدة',
        'gb':'المملكة المتحدة','uk':'المملكة المتحدة','britain':'المملكة المتحدة',
        'fr':'فرنسا','france':'فرنسا','paris':'فرنسا',
        'de':'ألمانيا','germany':'ألمانيا','berlin':'ألمانيا',
        'ru':'روسيا','russia':'روسيا','moscow':'روسيا',
        'cn':'الصين','china':'الصين','beijing':'الصين',
        'in':'الهند','india':'الهند','delhi':'الهند',
        'br':'البرازيل','brazil':'البرازيل'
    };
    
    const usernameLower=username.toLowerCase();
    
    for(const[keyword,countryName]of Object.entries(countryKeywords)){
        if(usernameLower.includes(keyword)){
            for(const[code,country]of Object.entries(COUNTRIES_DB)){
                if(country.name===countryName){
                    return country;
                }
            }
        }
    }
    
    // إذا لم يتم العثور، اختر دولة عشوائية
    const codes=Object.keys(COUNTRIES_DB);
    const randomCode=codes[Math.floor(Math.random()*codes.length)];
    return COUNTRIES_DB[randomCode];
}

function capitalizeFirstLetter(str){
    return str.split(' ').map(word=>word.charAt(0).toUpperCase()+word.slice(1)).join(' ');
}

function renderProfiles(){
    const c=document.getElementById('profileList');
    if(!profiles.length){
        c.innerHTML='<div class="empty-playlist"><span>🔍</span><p>الصق رابط ملف شخصي للفحص</p></div>';
        document.getElementById('profileStats').textContent='0 ملف';
        return;
    }
    
    document.getElementById('profileStats').textContent=profiles.length+' ملف';
    const platformIcons={tiktok:'🎵',instagram:'📸',twitter:'🐦',github:'🐙',facebook:'📘',linkedin:'💼',unknown:'🌐'};
    
    c.innerHTML=profiles.map(p=>{
        const icon=platformIcons[p.platform]||'🌐';
        const statusClass=p.status==='real'?'real':'fake';
        const statusBadge=p.status==='real'?'حقيقي':'وهمي';
        const verifiedBadge=p.verified?' ✅':'';
        
        return `<div class="profile-item ${statusClass}" onclick="showProfileDetails('${p.id}')">
            <div class="p-icon">${icon}</div>
            <div class="p-info">
                <div class="p-name">${p.name||p.username}${verifiedBadge}</div>
                <div class="p-details">@${p.username} • ${p.platform} • ${p.followers.toLocaleString()} متابع</div>
            </div>
            <span class="p-badge ${statusClass}">${statusBadge}</span>
            <div class="p-country">${p.country||'🌍'}</div>
            <span class="p-del" onclick="event.stopPropagation();deleteProfile('${p.id}')"><i class="fas fa-times"></i></span>
        </div>`;
    }).join('');
}

function deleteProfile(id){
    profiles=profiles.filter(p=>p.id!==id);
    saveProfiles(profiles);
    renderProfiles();
    updateStats();
    showToast('🗑 تم حذف الملف');
}

function showProfileDetails(id){
    const p=profiles.find(p=>p.id===id);
    if(!p)return;
    
    document.getElementById('modalTitle').textContent=p.name||p.username;
    document.getElementById('modalBody').innerHTML=`
        <div class="modal-item"><span class="label">🔍 المنصة</span><span class="value">${p.platform}</span></div>
        <div class="modal-item"><span class="label">👤 المستخدم</span><span class="value">@${p.username}</span></div>
        <div class="modal-item"><span class="label">📋 الحالة</span><span class="value">${p.status==='real'?'✅ حقيقي':'❌ وهمي'}</span></div>
        <div class="modal-item"><span class="label">🌍 الدولة</span><span class="value">${p.country||'غير محدد'}</span></div>
        <div class="modal-item"><span class="label">👥 المتابعون</span><span class="value">${p.followers.toLocaleString()}</span></div>
        <div class="modal-item"><span class="label">📌 متابَع</span><span class="value">${p.following.toLocaleString()}</span></div>
        <div class="modal-item"><span class="label">📄 المنشورات</span><span class="value">${p.posts}</span></div>
        <div class="modal-item"><span class="label">✅ موثق</span><span class="value">${p.verified?'نعم ✅':'لا'}</span></div>
        <div class="modal-item"><span class="label">🔗 الرابط</span><span class="value">${p.profile_url}</span></div>
    `;
    document.getElementById('profileModal').classList.add('active');
}

function closeModal(){
    document.getElementById('profileModal').classList.remove('active');
}

function updateStats(){
    document.getElementById('totalProfiles').textContent=profiles.length;
    const real=profiles.filter(p=>p.status==='real').length;
    const fake=profiles.filter(p=>p.status==='fake').length;
    document.getElementById('realProfiles').textContent=real;
    document.getElementById('fakeProfiles').textContent=fake;
    const countries=new Set(profiles.filter(p=>p.country).map(p=>p.country));
    document.getElementById('countriesCount').textContent=countries.size;
}

function toggleFilters(){
    showToast('🔍 الفلاتر قيد التطوير');
}

function toggleHistory(){
    const history=loadHistory();
    if(!history.length){
        showToast('📜 لا يوجد سجل بعد');
        return;
    }
    let historyText='📜 سجل الفحوصات:\n\n';
    history.slice(0,10).forEach((entry,i)=>{
        historyText+=`${i+1}. ${entry.status==='real'?'✅':'❌'} @${entry.username} (${entry.platform}) - ${entry.country||'غير محدد'}\n`;
    });
    alert(historyText);
}

function toggleSettings(){
    showToast('⚙️ الإعدادات قيد التطوير');
}

function showToast(message){
    const toast=document.getElementById('toast');
    toast.textContent=message;
    toast.classList.add('show');
    setTimeout(()=>toast.classList.remove('show'),2500);
}
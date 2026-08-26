const KEYS={profiles:'socialnetscan_profiles'};
function saveData(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true}catch(e){return false}}
function loadData(k,d=null){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function saveProfiles(profs){return saveData(KEYS.profiles,profs)}
function loadProfiles(){return loadData(KEYS.profiles,[])}
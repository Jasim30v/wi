const KEYS={profiles:'socialnetscan_profiles',history:'socialnetscan_history'};
function saveData(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true}catch(e){console.error('Save error:',e);return false}}
function loadData(k,d=null){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){console.error('Load error:',e);return d}}
function saveProfiles(profs){return saveData(KEYS.profiles,profs)}
function loadProfiles(){return loadData(KEYS.profiles,[])}
function saveHistory(h){saveData(KEYS.history,h)}
function loadHistory(){return loadData(KEYS.history,[])}
function addToHistory(entry){const h=loadHistory();h.unshift(entry);if(h.length>50)h.pop();saveHistory(h)}
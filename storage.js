const KEYS={networks:'wifinetscan2044_networks',settings:'wifinetscan2044_settings',history:'wifinetscan2044_history',filters:'wifinetscan2044_filters'};
function saveData(k,v){try{localStorage.setItem(k,JSON.stringify(v));return 1}catch(e){return 0}}
function loadData(k,d=null){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function saveNetworks(nets){const data=nets.map(n=>({id:n.id,ssid:n.ssid,mac:n.mac,signal:n.signal,frequency:n.frequency,channel:n.channel,security:n.security,encryption:n.encryption,maxSpeed:n.maxSpeed,firstSeen:n.firstSeen,lastSeen:n.lastSeen,hidden:n.hidden}));return saveData(KEYS.networks,data)}
function loadNetworks(){return loadData(KEYS.networks,[])}
function saveFilters(f){saveData(KEYS.filters,f)}
function loadFilters(){return loadData(KEYS.filters,{type:'all',minSignal:0,showHidden:false})}
function saveHistory(h){saveData(KEYS.history,h)}
function loadHistory(){return loadData(KEYS.history,[])}
function addToHistory(entry){const h=loadHistory();h.unshift(entry);if(h.length>50)h.pop();saveHistory(h)}
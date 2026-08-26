const KEYS={networks:'netscan_networks',history:'netscan_history',settings:'netscan_settings'};
function saveData(k,v){try{localStorage.setItem(k,JSON.stringify(v));return 1}catch(e){return 0}}
function loadData(k,d=null){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}}
function saveNetworks(networks){saveData(KEYS.networks,networks)}
function loadNetworks(){return loadData(KEYS.networks,[])}
function saveHistory(history){saveData(KEYS.history,history)}
function loadHistory(){return loadData(KEYS.history,[])}
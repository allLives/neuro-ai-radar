/* Apply a validated preference before paint, including when storage is unavailable. */
(()=>{
  'use strict';
  const key='neuroai-radar.theme.v1';
  const themes=new Set(['editorial','aero']);
  const root=document.documentElement;
  let saved='editorial';
  try{const value=localStorage.getItem(key);if(themes.has(value))saved=value}catch{}
  root.dataset.theme=saved;
  document.addEventListener('DOMContentLoaded',()=>{
    const dialog=document.getElementById('settingsDialog');
    const open=document.getElementById('settingsOpen');
    const radios=Array.from(dialog.querySelectorAll('input[name="theme"]'));
    const status=document.getElementById('themeStatus');
    function sync(){radios.forEach(r=>{r.checked=r.value===root.dataset.theme})}
    function close(){dialog.close();open.focus()}
    sync();
    open.addEventListener('click',()=>{sync();dialog.showModal()});
    document.getElementById('settingsClose').addEventListener('click',close);
    document.getElementById('settingsDone').addEventListener('click',close);
    dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)close()}});
    radios.forEach(radio=>radio.addEventListener('change',()=>{
      if(!radio.checked||!themes.has(radio.value))return;
      root.dataset.theme=radio.value;
      const label=radio.value==='editorial'?'编辑式杂志':'Frutiger Aero';
      try{localStorage.setItem(key,radio.value);status.textContent=`已选择 ${label}，下次访问会保留。`}
      catch{status.textContent=`已选择 ${label}；浏览器未允许保存偏好，本次访问仍可使用。`}
    }));
    window.addEventListener('storage',event=>{if(event.key===key&&(event.newValue===null||themes.has(event.newValue))){root.dataset.theme=event.newValue||'editorial';sync()}});
  });
})();

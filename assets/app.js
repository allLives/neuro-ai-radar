/* NeuroAI Radar — dependency-free research reading interface. */
(()=>{
  'use strict';
  const DATA=window.RADAR_DATA||{index:{weeks:[]},issues:{}};
  const $=id=>document.getElementById(id);
  const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeUrl=x=>{try{const u=new URL(x);return ['https:','http:'].includes(u.protocol)?u.href:'#'}catch{return '#'}};
  const state={week:null,query:'',category:'all',level:'all'};
  const fmtDate=s=>s?s.replaceAll('-','.'):'—';
  const displayKind=k=>({journal:'期刊发表',review:'期刊综述',perspective:'理论/观点',preprint:'预印本',conference:'会议论文集',unknown:'状态待核实'})[k]||'未分类';
  const prettyCat=c=>c||'未分类';
  function toast(msg){const el=$('toast');el.textContent=msg;el.classList.add('show');clearTimeout(window.__toastTimeout);window.__toastTimeout=setTimeout(()=>el.classList.remove('show'),2200)}
  function getWeek(){return DATA.issues[state.week]||DATA.issues[DATA.index.weeks[0]?.id];}
  function renderSidebar(){
    $('issueTotal').textContent=String(DATA.index.weeks.length).padStart(2,'0');
    $('issueList').innerHTML=DATA.index.weeks.map(w=>`<button class="issue-btn ${w.id===state.week?'active':''}" data-issue="${esc(w.id)}"><span class="issue-number">${esc(w.id.split('-').pop())}</span><span class="issue-meta">${esc(w.title)}<span>${esc(w.from_date)} / ${esc(w.count)} PAPERS</span></span></button>`).join('');
    $('issueList').querySelectorAll('[data-issue]').forEach(b=>b.addEventListener('click',()=>switchWeek(b.dataset.issue)));
  }
  function renderMain(){
    const w=getWeek(); if(!w)return;
    $('crumbWeek').textContent=w.id.replace('-',' ');
    $('heroEdition').textContent=`/ ISSUE NO. ${String(w.edition||w.id.split('W')[1]).padStart(3,'0')}`;
    $('heroDescription').textContent=w.subtitle||'从神经科学到通用人工智能，精选值得认真思考的研究。';
    $('heroDate').textContent=`${fmtDate(w.from_date)} — ${w.to_date?.slice(5).replace('-','.')}`;
    $('heroCuration').textContent=w.curation||'自动收录';
    $('statsCount').textContent=String(w.articles.length).padStart(2,'0');
    $('statsDeep').textContent=String((w.deepdives||[]).length).padStart(2,'0');
    $('statsTopics').textContent=String(new Set(w.articles.map(a=>a.category)).size).padStart(2,'0');
    $('statsWeek').textContent='W'+(w.edition||'—');
    $('statsPeriod').textContent=`${w.from_date}—${w.to_date}`;
    $('leadText').textContent=w.topline||'本周研究论文已按主题和研究关联度完成归档。';
    $('methodHint').textContent=w.method_note||'';
    $('footerYear').textContent=w.from_date?.slice(0,4)||'2026';
    const cats=Array.from(new Set(w.articles.map(a=>a.category))).sort((a,b)=>a.localeCompare(b,'zh'));
    $('categorySelect').innerHTML='<option value="all">全部研究方向</option>'+cats.map(c=>`<option value="${esc(c)}">${esc(prettyCat(c))}</option>`).join('');
    state.category='all';state.level='all';state.query='';$('categorySelect').value='all';$('levelSelect').value='all';$('searchInput').value='';
    $('topicPills').innerHTML=['all',...cats].map(c=>`<button class="pill ${c===state.category?'active':''}" data-cat="${esc(c)}">${c==='all'?'全部主题':esc(c)}</button>`).join('');
    $('topicPills').querySelectorAll('[data-cat]').forEach(b=>b.addEventListener('click',()=>{state.category=b.dataset.cat;$('categorySelect').value=state.category;updatePills();renderPapers()}));
    renderPapers();renderDeep();renderSidebar();
  }
  function updatePills(){$('topicPills').querySelectorAll('.pill').forEach(b=>b.classList.toggle('active',b.dataset.cat===state.category))}
  function renderPapers(){
    const w=getWeek();if(!w)return;
    const q=state.query.trim().toLowerCase();
    const items=w.articles.filter(a=> (state.category==='all'||a.category===state.category)&&(state.level==='all'||a.level===state.level)&&(!q||[a.title,a.authors,a.venue,a.category,a.summary,a.angle,...(a.tags||[])].join(' ').toLowerCase().includes(q)));
    $('matchCount').textContent=items.length;$('empty').hidden=items.length>0;
    $('papers').innerHTML=items.map(a=>{
      const level=a.level==='重点精读'?'':a.level==='值得关注'?'gold':'dim';
      const source=a.kind==='journal'?'':a.kind==='preprint'?'dim':'gold';
      return `<article class="paper"><div class="paper-top"><span class="badge ${level}">${esc(a.level)}</span><span class="badge ${source}">${esc(displayKind(a.kind))}</span><span class="paper-date">${esc(a.date)}</span></div><h3>${esc(a.title)}</h3><p class="paper-author">${esc(a.authors)} · ${esc(a.venue)}</p><p class="paper-summary">${esc(a.summary||a.abstract||'已自动收录；请查看原文摘要。')}</p>${a.evidence?`<p class="method-hint">${esc(a.evidence)}</p>`:''}<div class="paper-footer"><div class="paper-tags">${(a.tags||[]).slice(0,3).map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><a class="paper-link" href="${esc(safeUrl(a.url))}" target="_blank" rel="noopener noreferrer" aria-label="阅读 ${esc(a.title)} 原文">原文 ↗</a></div>${a.angle?`<div class="paper-angle">研究追问 · ${esc(a.angle)}</div>`:''}</article>`
    }).join('');
  }
  function renderDeep(){const w=getWeek(); const list=w?.deepdives||[];
    $('deepDives').innerHTML=list.length?list.map((d,i)=>`<article class="deep-card"><div class="deep-n">RESEARCH NOTE / ${String(i+1).padStart(2,'0')}</div><h3>${esc(d.headline)}</h3><p>${esc(d.insight)}</p><div class="deep-experiment"><span>可验证的小实验 / EXPERIMENT IDEA</span>${esc(d.experiment)}</div></article>`).join(''):'<div class="deep-card"><div class="deep-n">RESEARCH NOTE</div><h3>本期没有可靠的深度分析</h3><p>若元数据不足或自动摘要失败，不会虚构研究评价。</p></div>';
  }
  function switchWeek(id){if(!DATA.issues[id])return;state.week=id;renderMain();history.replaceState(null,'',`#issue=${encodeURIComponent(id)}`);$('sidebar').classList.remove('open');window.scrollTo({top:0,behavior:'smooth'})}
  $('searchInput').addEventListener('input',e=>{state.query=e.target.value;renderPapers()});
  $('categorySelect').addEventListener('change',e=>{state.category=e.target.value;updatePills();renderPapers()});
  $('levelSelect').addEventListener('change',e=>{state.level=e.target.value;renderPapers()});
  $('resetFilter').addEventListener('click',()=>{state.query='';state.category='all';state.level='all';$('searchInput').value='';$('categorySelect').value='all';$('levelSelect').value='all';updatePills();renderPapers()});
  $('navDigest').addEventListener('click',()=>{$('briefingAnchor').scrollIntoView({behavior:'smooth'});$('sidebar').classList.remove('open')});
  $('navFeatured').addEventListener('click',()=>{$('featuredAnchor').scrollIntoView({behavior:'smooth'});$('sidebar').classList.remove('open')});
  $('navArchive').addEventListener('click',()=>{$('issueList').scrollIntoView({behavior:'smooth'});$('sidebar').classList.toggle('open',window.innerWidth<=900)});
  $('menuToggle').addEventListener('click',()=>$('sidebar').classList.toggle('open'));
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)){e.preventDefault();$('searchInput').focus()}if(e.key==='Escape'){$('searchInput').blur();$('sidebar').classList.remove('open')}});
  $('copyLink').addEventListener('click',async()=>{try{const link=new URL(window.location.href);link.hash=`issue=${encodeURIComponent(state.week)}`;await navigator.clipboard.writeText(link.href);toast('已复制本期链接')}catch{toast('可直接复制浏览器地址栏链接')}});
  const readFragment=()=>{try{return decodeURIComponent((location.hash.match(/issue=([^&]+)/)||[])[1]||'')}catch{return ''}};
  const frag=readFragment();
  window.addEventListener('hashchange',()=>{const id=readFragment();if(DATA.issues[id]){state.week=id;renderMain()}});
  state.week=DATA.issues[frag]?frag:DATA.index.weeks[0]?.id;
  if(!state.week){$('leadText').textContent='暂无已发布的周报。';return;}
  renderMain();
  if(location.protocol==='file:'){$('localStatus').innerHTML='<span></span> OFFLINE PREVIEW';}
})();

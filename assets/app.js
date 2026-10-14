/* NeuroAI Radar — dependency-free research reading interface. */
(()=>{
  'use strict';
  const DATA=window.RADAR_DATA||{index:{weeks:[]},issues:{}};
  const $=id=>document.getElementById(id);
  const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeUrl=x=>{try{const u=new URL(x);return ['https:','http:'].includes(u.protocol)?u.href:'#'}catch{return '#'}};
  const state={week:null,query:'',category:'all',level:'all'};
  const fmtDate=s=>s?s.replaceAll('-','.'):'—';
  const weekLabel=id=>{const [year,week]=id.split('-W');return `${year} 年第 ${Number(week)} 周`};
  const dateRange=w=>`${fmtDate(w.from_date)} — ${fmtDate(w.to_date)}`;
  const priority=l=>l==='重点精读'?'优先阅读':l;
  const displayKind=k=>({journal:'期刊发表',review:'期刊综述',perspective:'理论/观点',preprint:'预印本',conference:'会议论文集',unknown:'状态待核实'})[k]||'未分类';
  const prettyCat=c=>c||'未分类';
  function toast(msg){const el=$('toast');el.textContent=msg;el.classList.add('show');clearTimeout(window.__toastTimeout);window.__toastTimeout=setTimeout(()=>el.classList.remove('show'),2200)}
  function getWeek(){return DATA.issues[state.week]||DATA.issues[DATA.index.weeks[0]?.id];}
  function renderSidebar(){
    $('issueTotal').textContent=String(DATA.index.weeks.length);
    $('issueList').innerHTML=DATA.index.weeks.map(w=>`<button class="issue-btn ${w.id===state.week?'active':''}" data-issue="${esc(w.id)}" aria-current="${w.id===state.week?'true':'false'}"><span class="issue-number">${esc(weekLabel(w.id))}</span><span class="issue-meta">${esc(w.title)}<span>${esc(dateRange(w))} · ${esc(w.count)} 篇论文</span></span></button>`).join('');
    $('issueList').querySelectorAll('[data-issue]').forEach(b=>b.addEventListener('click',()=>switchWeek(b.dataset.issue)));
  }
  function renderMain(){
    const w=getWeek(); if(!w)return;
    $('crumbWeek').textContent=weekLabel(w.id);
    $('heroTitle').textContent=w.title||'本周神经科学 × AI 精选';
    $('heroDescription').textContent=w.subtitle||'从神经科学到通用人工智能，精选值得认真思考的研究。';
    $('heroDate').textContent=dateRange(w);
    $('heroCuration').textContent=w.editorial?.basis==='existing_briefs'?'人工精选试刊':w.editorial?'AI 辅助导读':w.curation?.includes('人工')?'人工精选试刊':'文献自动索引';
    $('statsCount').textContent=w.articles.length;
    $('statsDeep').textContent=(w.deepdives||[]).length;
    $('statsTopics').textContent=new Set(w.articles.map(a=>a.category)).size;
    $('leadText').textContent=w.topline||'本周研究论文已按主题和研究关联度完成归档。';
    $('methodHint').textContent=w.method_note||'';
    $('readingBasis').textContent=w.editorial?.basis==='abstracts'?'中文导读基于公开摘要，未阅读全文。':w.editorial?.basis==='existing_briefs'?'本期为人工精选试刊，部分论文信息仍待核实。':w.articles.some(a=>a.ai_status==='generated')?'AI 解读基于公开摘要，未阅读全文。':'中文导读待补充。当前仅展示论文信息与来源摘要。';
    $('footerYear').textContent=w.from_date?.slice(0,4)||'2026';
    const cats=Array.from(new Set(w.articles.map(a=>a.category))).sort((a,b)=>a.localeCompare(b,'zh'));
    $('categorySelect').innerHTML='<option value="all">全部研究方向</option>'+cats.map(c=>`<option value="${esc(c)}">${esc(prettyCat(c))}</option>`).join('');
    state.category='all';state.level='all';state.query='';$('categorySelect').value='all';$('levelSelect').value='all';$('searchInput').value='';
    $('topicPills').innerHTML=['all',...cats].map(c=>`<button class="pill ${c===state.category?'active':''}" data-cat="${esc(c)}">${c==='all'?'全部主题':esc(c)}</button>`).join('');
    $('topicPills').querySelectorAll('[data-cat]').forEach(b=>b.addEventListener('click',()=>{state.category=b.dataset.cat;$('categorySelect').value=state.category;updatePills();renderPapers()}));
    renderPapers();renderDeep();renderSidebar();renderHighlights();
  }
  function renderHighlights(){const w=getWeek();const items=w.highlights||[];
    const section=$('highlights').closest('section');section.hidden=!items.length;
    $('highlights').innerHTML=items.map((h,i)=>`<button class="highlight-card" data-read="${esc(h.id)}"><span class="highlight-number">先读 ${i+1}</span><h3>${esc(h.headline)}</h3><p>${esc(h.summary)}</p><span class="highlight-action">查看论文 ↓</span></button>`).join('');
    $('highlights').querySelectorAll('[data-read]').forEach(b=>b.addEventListener('click',()=>{resetFilters();const paper=document.getElementById(`paper-${b.dataset.read}`);paper?.scrollIntoView({behavior:'smooth',block:'start'});paper?.focus({preventScroll:true})}));
  }
  function updatePills(){$('topicPills').querySelectorAll('.pill').forEach(b=>b.classList.toggle('active',b.dataset.cat===state.category))}
  function renderPapers(){
    const w=getWeek();if(!w)return;
    const q=state.query.trim().toLowerCase();
    const items=w.articles.filter(a=> (state.category==='all'||a.category===state.category)&&(state.level==='all'||a.level===state.level)&&(!q||[a.title,a.title_zh,a.authors,a.venue,a.category,a.summary,a.angle,...(a.tags||[])].join(' ').toLowerCase().includes(q)));
    $('matchCount').textContent=`${items.length} 篇${items.length!==w.articles.length?` / 共 ${w.articles.length} 篇`:''}`;$('empty').hidden=items.length>0;
    $('papers').innerHTML=items.map(a=>{
      const level=a.level==='重点精读'?'':a.level==='值得关注'?'gold':'dim';
      const source=a.kind==='journal'?'':a.kind==='preprint'?'dim':'gold';
      const excerpt=(a.summary||'').replace(/^摘要摘录（英文）：/,'').replace(/^作者摘要报告（AI 概括）：/,'');
      const author=String(a.authors||'作者信息待补充').split(',')[0]+(String(a.authors||'').includes(',')?' 等':'');
      return `<article class="paper" id="paper-${esc(a.id)}" tabindex="-1"><span class="paper-index">${String(w.articles.indexOf(a)+1).padStart(2,'0')}</span><div class="paper-top"><span class="badge ${level}">${esc(priority(a.level))}</span><span class="badge ${source}">${esc(displayKind(a.kind))}</span><span class="paper-category">${esc(a.category)}</span></div><div class="paper-body"><h3><a href="${esc(safeUrl(a.url))}" target="_blank" rel="noopener noreferrer">${esc(a.title_zh||a.title)}</a></h3>${a.title_zh?`<p class="paper-original-title" lang="en">${esc(a.title)}</p>`:''}<p class="paper-author">${esc(a.venue)} · ${esc(fmtDate(a.date))} · ${esc(author)}</p><p class="paper-summary">${esc(excerpt||'来源未提供摘要，暂不作研究解读。请查看原文。')}</p>${a.angle?`<div class="paper-angle"><strong>研究思考</strong>${esc(a.angle.replace(/^(研究思考：|模型推测 \/ 研究建议：)/,''))}</div>`:''}<details class="paper-details"><summary>摘要与收录依据</summary><p>${esc(a.evidence||'基于摘要与元数据整理，未阅读全文。')}</p><p>作者：${esc(a.authors)}</p>${a.doi?`<p>DOI：${esc(a.doi)}</p>`:''}${a.abstract?`<p class="source-abstract" lang="en">${esc(a.abstract)}</p>`:'<p>当前归档未保存原始摘要，请到原文页面核对。</p>'}</details></div><div class="paper-footer"><div class="paper-tags">${(a.tags||[]).slice(0,3).map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div><a class="paper-link" href="${esc(safeUrl(a.url))}" target="_blank" rel="noopener noreferrer" aria-label="阅读 ${esc(a.title)} 原文">阅读原文 ↗</a></div></article>`
    }).join('');
  }
  function renderDeep(){const w=getWeek(); const list=w?.deepdives||[];
    $('featuredAnchor').hidden=!list.length;$('navFeatured').hidden=!list.length;
    $('deepDives').innerHTML=list.map((d,i)=>`<article class="deep-card"><div class="deep-n">研究思考 ${i+1}</div><h3>${esc(d.headline)}</h3><p>${esc(d.insight)}</p><div class="deep-experiment"><span>可尝试的实验（未经验证）</span>${esc(d.experiment)}</div><a class="note-source" href="${esc(safeUrl(w.articles.find(a=>a.id===d.id)?.url))}" target="_blank" rel="noopener noreferrer">相关论文 ↗</a></article>`).join('');
  }
  function switchWeek(id){if(!DATA.issues[id])return;state.week=id;renderMain();history.replaceState(null,'',`#issue=${encodeURIComponent(id)}`);$('archiveDisclosure').open=false;$('sidebar').classList.remove('open');$('menuToggle').setAttribute('aria-expanded','false');window.scrollTo({top:0,behavior:'smooth'})}
  document.querySelector('.brand').addEventListener('click',e=>{e.preventDefault();switchWeek(DATA.index.weeks[0]?.id)});
  $('searchInput').addEventListener('input',e=>{state.query=e.target.value;renderPapers()});
  $('categorySelect').addEventListener('change',e=>{state.category=e.target.value;updatePills();renderPapers()});
  $('levelSelect').addEventListener('change',e=>{state.level=e.target.value;renderPapers()});
  function resetFilters(){state.query='';state.category='all';state.level='all';$('searchInput').value='';$('categorySelect').value='all';$('levelSelect').value='all';updatePills();renderPapers()}
  $('resetFilter').addEventListener('click',resetFilters);
  $('navDigest').addEventListener('click',()=>{window.scrollTo({top:0,behavior:'smooth'});$('sidebar').classList.remove('open');$('menuToggle').setAttribute('aria-expanded','false')});
  $('navFeatured').addEventListener('click',()=>{$('featuredAnchor').scrollIntoView({behavior:'smooth'});$('sidebar').classList.remove('open');$('menuToggle').setAttribute('aria-expanded','false')});
  $('navArchive').addEventListener('click',()=>{$('archiveDisclosure').open=!$('archiveDisclosure').open;if($('archiveDisclosure').open)$('archiveDisclosure').scrollIntoView({behavior:'smooth',block:'nearest'});$('sidebar').classList.remove('open');$('menuToggle').setAttribute('aria-expanded','false')});
  $('archiveDisclosure').addEventListener('toggle',()=>{$('navArchive').setAttribute('aria-expanded',String($('archiveDisclosure').open))});
  $('menuToggle').addEventListener('click',()=>{const open=$('sidebar').classList.toggle('open');$('menuToggle').setAttribute('aria-expanded',String(open))});
  document.addEventListener('keydown',e=>{if(e.key==='/'&&!$('settingsDialog').open&&!/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)){e.preventDefault();$('searchInput').focus()}if(e.key==='Escape'){$('searchInput').blur();$('sidebar').classList.remove('open');$('menuToggle').setAttribute('aria-expanded','false')}});
  $('copyLink').addEventListener('click',async()=>{try{const link=new URL(window.location.href);link.hash=`issue=${encodeURIComponent(state.week)}`;await navigator.clipboard.writeText(link.href);toast('已复制本期链接')}catch{toast('可直接复制浏览器地址栏链接')}});
  const readFragment=()=>{try{return decodeURIComponent((location.hash.match(/issue=([^&]+)/)||[])[1]||'')}catch{return ''}};
  const frag=readFragment();
  window.addEventListener('hashchange',()=>{const id=readFragment();if(DATA.issues[id]){state.week=id;renderMain()}});
  state.week=DATA.issues[frag]?frag:DATA.index.weeks[0]?.id;
  if(!state.week){$('leadText').textContent='暂无已发布的周报。';return;}
  renderMain();
  if(location.protocol==='file:'){$('localStatus').innerHTML='<span></span> OFFLINE PREVIEW';}
})();

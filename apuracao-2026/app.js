import { adaptUnified, calcularProporcional, tseInt } from './engine.js';

const UFS=[
['AC','Acre'],['AL','Alagoas'],['AP','Amapá'],['AM','Amazonas'],['BA','Bahia'],['CE','Ceará'],['DF','Distrito Federal'],['ES','Espírito Santo'],['GO','Goiás'],['MA','Maranhão'],['MT','Mato Grosso'],['MS','Mato Grosso do Sul'],['MG','Minas Gerais'],['PA','Pará'],['PB','Paraíba'],['PR','Paraná'],['PE','Pernambuco'],['PI','Piauí'],['RJ','Rio de Janeiro'],['RN','Rio Grande do Norte'],['RS','Rio Grande do Sul'],['RO','Rondônia'],['RR','Roraima'],['SC','Santa Catarina'],['SP','São Paulo'],['SE','Sergipe'],['TO','Tocantins']
];
const UF_NAME=Object.fromEntries(UFS);
const CARGO={'1':'Presidente','3':'Governador','5':'Senador','6':'Deputado Federal','7':'Deputado Estadual','8':'Deputado Distrital'};
const COLORS=['#7c3aed','#2563eb','#0891b2','#0f9f6e','#d97706','#db2777','#4f46e5','#65a30d','#ea580c','#9333ea','#0284c7','#059669','#ca8a04','#be123c','#6366f1','#15803d','#c2410c','#a21caf'];
const S={
  codes:{fed:'6257',est:'6259'},view:'agora',uf:'MG',cargo:'3',cache:new Map(),governors:null,
  congress:{camara:null,senado:null},poll:null,loading:new Set(),lastRefresh:null,candidateIndex:new Map()
};
const API_BASE=location.hostname.endsWith('.vercel.app')?'':'https://apuracao-2026-lake.vercel.app';
const apiUrl=path=>API_BASE+path;

const $=s=>document.querySelector(s);
const $$=s=>[...document.querySelectorAll(s)];
const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const fmt=n=>Number(n||0).toLocaleString('pt-BR');
const pct=n=>Number(n||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%';
const clamp=n=>Math.max(0,Math.min(100,Number(n||0)));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function hashColor(s=''){let h=0;for(const c of String(s))h=(h*31+c.charCodeAt(0))>>>0;return COLORS[h%COLORS.length]}
function tsePath(path){return apiUrl('/api/tse?path='+encodeURIComponent(path))}
function resultPath(cargo,uf){
  const ele=cargo==='1'?S.codes.fed:S.codes.est;
  const abr=cargo==='1'?'br':uf.toLowerCase();
  return `/oficial/ele2026/${ele}/dados/${abr}/${abr}-c${String(cargo).padStart(4,'0')}-e${String(ele).padStart(6,'0')}-u.json`;
}
async function discoverCodes(){
  try{
    const r=await fetch(tsePath('/oficial/comum/config/ele-c.json'),{cache:'no-store'}); if(!r.ok)return;
    const j=await r.json();
    for(const pl of j.pl||[]) if(pl.c==='ele2026') for(const e of pl.e||[]){
      const cs=new Set((e.abr||[]).flatMap(a=>(a.cp||[]).map(c=>String(c.cd))));
      if(cs.has('1'))S.codes.fed=String(e.cd);
      if(cs.has('3')||cs.has('5')||cs.has('6'))S.codes.est=String(e.cd);
    }
  }catch{}
}
async function fetchResult(cargo,uf='BR',force=false){
  const key=cargo+':'+uf; const hit=S.cache.get(key);
  if(!force&&hit&&Date.now()-hit.at<18000)return hit.data;
  const ele=cargo==='1'?S.codes.fed:S.codes.est;
  const r=await fetch(tsePath(resultPath(cargo,uf)),{cache:'no-store'});
  if(!r.ok){if(hit)return hit.data;throw new Error('TSE '+r.status)}
  const raw=await r.json();
  const data=adaptUnified(raw,{electionCode:ele,uf,cargoCode:cargo,photoBase:apiUrl('/api/tse?path=')});
  S.cache.set(key,{at:Date.now(),data,raw}); S.lastRefresh=Date.now(); updateLive();
  return data;
}
async function batchMap(items,limit,fn){
  const out=[];for(let i=0;i<items.length;i+=limit)out.push(...await Promise.all(items.slice(i,i+limit).map(fn)));return out;
}
async function governorSummaryClient(force=false){
  const rows=await batchMap(UFS,4,async ([uf])=>{
    try{
      const r=await fetchResult('3',uf,force),official=r.candidatos.filter(c=>c.eleitoTse||c.situacaoOficial);
      return{uf,ok:true,pct:r.pctTotalizado,md:r.meta.md,tf:r.meta.tf,updated:r.totalizadoEm,
        leader:r.pctTotalizado>0?(r.candidatos[0]||null):null,
        official:official.map(c=>({...c,e:c.eleitoTse,st:c.situacaoOficial}))};
    }catch{return{uf,ok:false,pct:0,md:'n',tf:'n',official:[]}}
  });
  return{updatedAt:new Date().toISOString(),states:rows};
}
function officialCandidate(c){return !!(c.eleitoTse||(/^Eleito/i.test(c.situacaoOficial||'')&&!/^Não eleito/i.test(c.situacaoOficial||'')))}
async function congressClient(force=false){
  const pairs=await batchMap(UFS,4,async ([uf])=>{
    const [cam,sen]=await Promise.all([
      fetchResult('6',uf,force).catch(()=>null),
      fetchResult('5',uf,force).catch(()=>null)
    ]);
    return{uf,cam,sen};
  });
  const groups=new Map(),camOfficial=[];let seatsTotal=0,camLoaded=0,camPct=0;
  const senParty=new Map(),senUfs=[];let senLoaded=0,senPct=0,officialCount=0;
  for(const x of pairs){
    if(x.cam){
      camLoaded++;camPct+=x.cam.pctTotalizado;seatsTotal+=x.cam.vagas;
      for(const g of x.cam.partidos){
        const key=g.sigla||g.nome,cur=groups.get(key)||{sigla:key,nome:g.nome||key,seats:0,votes:0};
        cur.seats+=Number(g.vagasOficiais||0);cur.votes+=Number(g.votosValidos||0);groups.set(key,cur);
      }
      camOfficial.push(...x.cam.candidatos.filter(officialCandidate));
    }
    if(x.sen){
      senLoaded++;senPct+=x.sen.pctTotalizado;
      const official=x.sen.candidatos.filter(officialCandidate).map(c=>({...c,official:true}));
      officialCount+=official.length;
      for(const c of official){
        const key=c.partido||'OUTROS',cur=senParty.get(key)||{sigla:key,seats:0};cur.seats++;senParty.set(key,cur);
      }
      const leaders=x.sen.pctTotalizado>0?x.sen.candidatos.slice(0,2).map(c=>({...c,official:false})):[];
      senUfs.push({uf:x.uf,pct:x.sen.pctTotalizado,tf:x.sen.meta.tf,official,leaders});
    }else senUfs.push({uf:x.uf,pct:0,tf:'n',official:[],leaders:[]});
  }
  return{
    cam:{kind:'camara',updatedAt:new Date().toISOString(),ufsLoaded:camLoaded,ufsTotal:27,pctAverage:camLoaded?camPct/camLoaded:0,seatsTotal,
      officialSeats:[...groups.values()].sort((a,b)=>b.seats-a.seats||b.votes-a.votes),officialElected:camOfficial},
    sen:{kind:'senado',updatedAt:new Date().toISOString(),ufsLoaded:senLoaded,ufsTotal:27,pctAverage:senLoaded?senPct/senLoaded:0,
      seatsContested:54,officialCount,byParty:[...senParty.values()].sort((a,b)=>b.seats-a.seats),ufs:senUfs}
  };
}

function cachedRaw(cargo,uf='BR'){return S.cache.get(cargo+':'+uf)?.raw}
function updateLive(){
  const el=$('#liveTime'); if(!el)return;
  const t=S.lastRefresh?new Date(S.lastRefresh).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit',second:'2-digit'}):'conectando';
  el.textContent='TSE · '+t;
}
function avatar(c,size=''){
  const num=esc(c.numero||'');
  let src=c.fotoUrl||c.foto||'';
  if(API_BASE&&String(src).startsWith('/api/'))src=apiUrl(src);
  return `<div class="avatar ${size}"><img loading="lazy" src="${esc(src)}" alt="" onerror="this.remove();this.parentElement.textContent='${num}'"></div>`;
}
function officialInfo(c,r,cargo,index){
  const st=String(c.situacaoOficial||c.st||'').trim();
  if(st){
    const low=st.toLowerCase();
    const cls=low.includes('não eleito')?'supp-badge':low.includes('suplente')?'supp-badge':'official-badge';
    return {label:st+' · TSE',cls,official:!low.includes('não eleito')};
  }
  if(c.eleitoTse||c.e){
    if((cargo==='1'||cargo==='3')&&r?.meta?.md==='s')return{label:'2º TURNO · TSE',cls:'official-badge',official:true};
    return{label:'ELEITO · TSE',cls:'official-badge',official:true};
  }
  if((r?.pctTotalizado||0)>0){
    if(cargo==='5'&&index<2)return{label:'Liderando',cls:'leader-badge',official:false};
    if((cargo==='1'||cargo==='3')&&index===0)return{label:'Liderando',cls:'leader-badge',official:false};
  }
  return null;
}
function electionAlert(r,cargo){
  if(r?.meta?.esae==='s'){
    const why=(r.meta.mnae||[]).join(' · ');
    return `<div class="alert danger"><strong>TSE: sem atribuição de eleito.</strong>${why?' '+esc(why):''}</div>`;
  }
  if(r?.meta?.tf==='s')return '<div class="alert success"><strong>TSE: totalização final concluída.</strong> Os selos abaixo refletem a situação oficial final.</div>';
  if((cargo==='1'||cargo==='3')&&r?.meta?.md==='e')return '<div class="alert success"><strong>TSE: eleição matematicamente definida.</strong> O candidato marcado como ELEITO já não pode ser alcançado pelos votos restantes.</div>';
  if((cargo==='1'||cargo==='3')&&r?.meta?.md==='s')return '<div class="alert success"><strong>TSE: segundo turno matematicamente definido.</strong> Os candidatos marcados irão ao 2º turno.</div>';
  if((r?.pctTotalizado||0)===0)return '<div class="alert waiting">Aguardando o início da totalização. Candidatos e vagas já estão carregados; votos, QE e cadeiras surgirão conforme o TSE publicar.</div>';
  return `<div class="alert waiting">Apuração parcial do TSE: <strong>${pct(r.pctTotalizado)}</strong> das seções totalizadas. “Liderando” não significa eleito.</div>`;
}
function candidateRow(c,r,cargo,index){
  const oi=officialInfo(c,r,cargo,index),fav=candidateForFavorite(c,r,cargo);
  return `<div class="candidate-row">
    <div class="rank">${index+1}º</div>${avatar(c)}
    <div><div class="cand-name">${esc(c.nome)}</div><div class="cand-meta">${esc(c.numero)} · ${esc(c.partido)} · ${fmt(c.votos)} votos</div>
      <div class="vote-bar"><span style="width:${clamp(c.pct)}%"></span></div>${oi?`<span class="${oi.cls}">${esc(oi.label)}</span>`:''}
    </div>
    <div class="right-stat candidate-actions">${favoriteButton(fav)}<strong>${pct(c.pct)}</strong><small>${r?.pctTotalizado?pct(r.pctTotalizado)+' apurado':''}</small></div>
  </div>`;
}
function donut(r){
  const valid=Math.max(0,r.validos||0),blank=Math.max(0,r.brancos||0),nul=Math.max(0,r.nulos||0),total=valid+blank+nul;
  const pv=total?valid/total*100:0,pb=total?blank/total*100:0;
  const bg=`conic-gradient(var(--accent) 0 ${pv}%, #f59e0b ${pv}% ${pv+pb}%, #ef4444 ${pv+pb}% 100%)`;
  return `<div class="donut-wrap"><div class="donut" style="background:${bg}"><div class="donut-center"><div><strong>${fmt(total)}</strong><small>votos computados</small></div></div></div></div>
  <div class="legend"><div class="legend-row"><i class="legend-dot" style="background:var(--accent)"></i><span>Válidos</span><strong>${fmt(valid)}</strong></div><div class="legend-row"><i class="legend-dot" style="background:#f59e0b"></i><span>Brancos</span><strong>${fmt(blank)}</strong></div><div class="legend-row"><i class="legend-dot" style="background:#ef4444"></i><span>Nulos</span><strong>${fmt(nul)}</strong></div></div>`;
}
function officialSelected(r,cargo){
  return r.candidatos.filter((c,i)=>officialInfo(c,r,cargo,i)?.official);
}
function orderedCandidates(r){
  const cs=(r?.candidatos||[]).slice();
  return (r?.pctTotalizado||0)===0 ? cs.sort((a,b)=>a.nome.localeCompare(b.nome,'pt-BR')) : cs;
}
function renderLeaderCards(r,cargo,limit=2){
  if((r?.pctTotalizado||0)===0)return `<div class="empty">Aguardando votos · ${(r?.candidatos||[]).length} candidaturas carregadas.</div>`;
  const cs=orderedCandidates(r).slice(0,limit);
  return cs.map((c,i)=>{const oi=officialInfo(c,r,cargo,i),fav=candidateForFavorite(c,r,cargo);return `<div class="leader-card">${avatar(c)}<div><div class="cand-name">${esc(c.nome)}</div><div class="cand-meta">${esc(c.numero)} · ${esc(c.partido)} · ${fmt(c.votos)} votos</div>${oi?`<span class="${oi.cls}">${esc(oi.label)}</span>`:''}</div><div class="leader-side">${favoriteButton(fav)}<div class="cand-pct">${pct(c.pct)}</div></div></div>`}).join('')||'<div class="empty">Aguardando candidatos.</div>';
}
function recordPresident(r){
  if(!(r.pctTotalizado>0))return;
  let h=[];try{h=JSON.parse(localStorage.getItem('ap26-pres-history')||'[]')}catch{}
  const top=r.candidatos.slice(0,4).map(c=>({id:c.id,n:c.nome,p:c.pct}));
  const last=h[h.length-1];if(last&&Math.abs((last.ap||0)-r.pctTotalizado)<.01)return;
  h.push({t:Date.now(),ap:r.pctTotalizado,top});h=h.slice(-50);localStorage.setItem('ap26-pres-history',JSON.stringify(h));
}
function evolution(){
  let h=[];try{h=JSON.parse(localStorage.getItem('ap26-pres-history')||'[]')}catch{}
  if(h.length<2)return '<div class="empty">O gráfico de evolução aparecerá após duas atualizações com votos.</div>';
  const ids=[...new Set(h.flatMap(x=>x.top.map(c=>c.id)))].slice(0,4),W=420,H=150,pad=12;
  const x=i=>pad+(W-2*pad)*(i/(h.length-1)),y=p=>H-pad-(H-2*pad)*(p/100);
  const lines=ids.map((id,k)=>{const pts=h.map((a,i)=>{const c=a.top.find(x=>x.id===id);return c?x(i)+','+y(c.p):null}).filter(Boolean).join(' ');const name=h.flatMap(a=>a.top).find(c=>c.id===id)?.n||id;return `<polyline points="${pts}" fill="none" stroke="${COLORS[k]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/><text x="${pad+3}" y="${18+k*14}" fill="${COLORS[k]}" font-size="9">${esc(name)}</text>`}).join('');
  return `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Evolução da apuração">${lines}</svg>`;
}
async function loadAgora(force=false){
  const host=$('#agoraContent');host.innerHTML='<div class="card pad loading"><div class="empty">Carregando dados oficiais do TSE…</div></div>';
  const [pres,gov]=await Promise.all([
    fetchResult('1','BR',force),
    API_BASE?governorSummaryClient(force):fetch('/api/summary'+(force?'?t='+Date.now():'')).then(r=>r.ok?r.json():null).catch(()=>null)
  ]);
  S.governors=gov;recordPresident(pres);
  const official=officialSelected(pres,'1');
  const defined=pres.meta.md==='e'?'Eleito definido':pres.meta.md==='s'?'2º turno definido':pres.meta.tf==='s'?'Final':'Em apuração';
  const govDefined=(gov?.states||[]).filter(x=>x.md==='e'||x.md==='s'||x.tf==='s').length;
  host.innerHTML=`
    <div class="page-head"><div><div class="eyebrow">Eleições Gerais 2026</div><h1 class="page-title">Apuração em tempo real</h1><div class="page-sub">Dados oficiais do TSE, com atualização automática a cada 30 segundos.</div></div><div class="source-pill"><span class="live-dot"></span> Fonte oficial · TSE</div></div>
    <div class="hero-grid">
      <section class="card hero-card"><div class="section-head"><div><div class="eyebrow">Presidente · Brasil</div><div class="section-title">${esc(defined)}</div></div><button class="card-action" data-go="presidente">Detalhes <span>→</span></button></div>
        <div class="progress-row"><div class="progress"><span style="width:${clamp(pres.pctTotalizado)}%"></span></div><strong class="progress-pct">${pct(pres.pctTotalizado)}</strong></div>
        ${electionAlert(pres,'1')}<div class="leader-grid">${renderLeaderCards(pres,'1',2)}</div>
      </section>
      <aside class="metric-stack">
        <div class="card metric-card"><div class="metric-label">Situação presidencial</div><div class="metric-value" style="font-size:20px">${esc(official[0]?.situacaoOficial||official[0]?.nome||defined)}</div><div class="metric-foot">${official.length?official.length+' candidato(s) marcado(s) pelo TSE':'sem definição oficial ainda'}</div></div>
        <div class="card metric-card"><div class="metric-label">Governadores definidos</div><div class="metric-value">${govDefined}<span style="font-size:14px;color:var(--muted)"> / 27</span></div><div class="metric-foot">eleito, 2º turno ou totalização final</div></div>
        <div class="card metric-card"><div class="metric-label">Próxima atualização</div><div class="metric-value" style="font-size:20px">30 segundos</div><div class="metric-foot">somente nas telas em uso</div></div>
      </aside>
    </div>
    <section class="section"><div class="section-head"><div><div class="eyebrow">Mapa rápido</div><div class="section-title">Governadores por UF</div></div><div class="section-note">clique para abrir o estado</div></div><div class="uf-grid">${renderGovernorGrid(gov)}</div></section>
    <section class="section"><div class="info-grid"><div class="card info-card"><h3>Câmara dos Deputados</h3><p>513 cadeiras. O painel Congresso mostra a distribuição nacional por partido/federação usando <strong>TSE agora</strong> e as cadeiras já atribuídas em cada UF.</p><button class="card-action" data-go="congresso">Congresso <span>→</span></button></div><div class="card info-card"><h3>Senado Federal</h3><p>54 vagas em disputa em 2026, duas por UF. Antes da definição oficial mostramos os dois líderes; depois, somente o status de eleito informado pelo TSE.</p><button class="card-action" data-go="congresso">Senado <span>→</span></button></div></div></section>`;
  wireGo();syncFavoriteButtons();wireFavorites(host);
}
function renderGovernorGrid(gov){
  if(!gov?.states)return UFS.map(([uf])=>`<button class="uf-card" data-uf="${uf}"><strong>${uf}</strong><span>abrir</span></button>`).join('');
  return gov.states.map(x=>{
    const c=x.official?.find(c=>c.e)||x.leader, label=x.md==='s'?'2º turno TSE':x.md==='e'?'eleito TSE':x.tf==='s'?'final':x.pct>0?(c?.nome||'apurando'):'aguardando';
    return `<button class="uf-card" data-uf="${x.uf}"><strong>${x.uf}</strong><span class="${x.md==='e'||x.tf==='s'?'mini-status':''}">${esc(label)}</span><span>${pct(x.pct||0)}</span></button>`;
  }).join('');
}
async function loadPresident(force=false){
  const host=$('#presidentContent');host.innerHTML='<div class="card pad loading"><div class="empty">Carregando Presidente…</div></div>';
  const r=await fetchResult('1','BR',force);recordPresident(r);
  const official=officialSelected(r,'1');
  host.innerHTML=`
  <div class="page-head"><div><div class="eyebrow">Brasil · 1º turno</div><h1 class="page-title">Presidente da República</h1><div class="page-sub">Ranking, situação oficial, votos e evolução da totalização.</div></div><div class="ring-wrap"><div class="ring" style="--p:${clamp(r.pctTotalizado)}%"><span>${pct(r.pctTotalizado)}</span></div><div class="ring-copy"><strong>seções totalizadas</strong><small>${esc(r.totalizadoEm||'aguardando')}</small></div></div></div>
  ${electionAlert(r,'1')}
  <div class="pres-grid section">
    <section class="card pad"><div class="section-head"><div><div class="eyebrow">Placar oficial</div><div class="section-title">Candidatos</div></div><div class="section-note">${r.candidatos.length} candidaturas</div></div><div class="candidate-list">${orderedCandidates(r).map((c,i)=>candidateRow(c,r,'1',i)).join('')}</div></section>
    <aside class="stack">
      <div class="card pad"><div class="section-head"><div><div class="eyebrow">Situação TSE</div><div class="section-title">${r.meta.md==='e'?'Eleição definida':r.meta.md==='s'?'Segundo turno definido':r.meta.tf==='s'?'Totalização final':'Acompanhamento'}</div></div></div><div class="status-board">${official.length?official.map(c=>`<span class="status-chip official">${esc(c.nome)} · ${esc(officialInfo(c,r,'1',0)?.label||'TSE')}</span>`).join(''):'<span class="status-chip">Nenhum eleito/2º turno oficial ainda</span>'}</div></div>
      <div class="card pad"><div class="eyebrow">Votos</div><div class="section-title">Composição</div>${donut(r)}<div class="stats-grid"><div class="stat-box"><span>Eleitorado</span><strong>${fmt(r.eleitorado)}</strong></div><div class="stat-box"><span>Comparecimento</span><strong>${fmt(r.comparecimento)}</strong></div><div class="stat-box"><span>Abstenção</span><strong>${fmt(r.abstencao)}</strong></div><div class="stat-box"><span>Válidos</span><strong>${fmt(r.validos)}</strong></div></div></div>
      <div class="card pad"><div class="eyebrow">Evolução local</div><div class="section-title">Percentuais ao longo das atualizações</div><div style="margin-top:9px">${evolution()}</div></div>
    </aside>
  </div>`;syncFavoriteButtons();wireFavorites(host);
}
function buildStateToolbar(){
  const opts=UFS.map(([u,n])=>`<option value="${u}" ${u===S.uf?'selected':''}>${n} (${u})</option>`).join('');
  const dep=S.uf==='DF'?['8','Distrital']:['7','Estadual'];
  return `<div class="state-toolbar"><div class="select-group"><label>UF</label><select id="ufSelect" class="select">${opts}</select></div><div class="section-note">Fonte: arquivo unificado EA20 do TSE</div></div>
  <div class="cargo-tabs"><button class="cargo-tab ${S.cargo==='3'?'active':''}" data-cargo="3">Governador</button><button class="cargo-tab ${S.cargo==='5'?'active':''}" data-cargo="5">Senado</button><button class="cargo-tab ${S.cargo==='6'?'active':''}" data-cargo="6">Dep. Federal</button><button class="cargo-tab ${S.cargo===dep[0]?'active':''}" data-cargo="${dep[0]}">Dep. ${dep[1]}</button></div>`;
}
async function loadState(force=false){
  const host=$('#stateContent');host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Resultados por UF</div><h1 class="page-title">Estados</h1></div></div>${buildStateToolbar()}<div class="card pad loading"><div class="empty">Carregando ${esc(CARGO[S.cargo])} · ${S.uf}…</div></div>`;
  wireStateControls();
  const cargo=S.uf==='DF'&&S.cargo==='7'?'8':S.uf!=='DF'&&S.cargo==='8'?'7':S.cargo;S.cargo=cargo;
  const r=await fetchResult(cargo,S.uf,force);
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">${esc(UF_NAME[S.uf])}</div><h1 class="page-title">${esc(CARGO[cargo])}</h1><div class="page-sub">${S.uf} · ${pct(r.pctTotalizado)} das seções totalizadas</div></div><div class="source-pill">TSE · ${esc(r.meta.dataGeracao||'')} ${esc(r.meta.horaGeracao||'')}</div></div>${buildStateToolbar()}${cargo==='3'||cargo==='5'?renderMajorState(r,cargo):renderProportional(r,cargo)}`;
  wireStateControls();wireProportionalCandidateRanking(host);syncFavoriteButtons();wireFavorites(host);
}
function wireStateControls(){
  const sel=$('#ufSelect');if(sel)sel.onchange=()=>{S.uf=sel.value;if(S.uf==='DF'&&S.cargo==='7')S.cargo='8';if(S.uf!=='DF'&&S.cargo==='8')S.cargo='7';loadState(true)};
  $$('.cargo-tab').forEach(b=>b.onclick=()=>{S.cargo=b.dataset.cargo;loadState(true)});
}
function renderMajorState(r,cargo){
  const isSen=cargo==='5',official=officialSelected(r,cargo);
  return `<div class="major-grid"><section class="card pad">${electionAlert(r,cargo)}<div class="section-head" style="margin-top:13px"><div><div class="eyebrow">${isSen?'Duas vagas':'Disputa majoritária'}</div><div class="section-title">${isSen?'Senado · '+S.uf:'Governador · '+S.uf}</div></div><div class="section-note">${r.candidatos.length} candidaturas</div></div><div class="candidate-list">${orderedCandidates(r).map((c,i)=>candidateRow(c,r,cargo,i)).join('')}</div></section>
  <aside class="stack"><div class="card pad"><div class="eyebrow">Situação oficial</div><div class="section-title">${official.length?official.length+' definido(s) pelo TSE':'Ainda sem definição'}</div><div class="status-board" style="margin-top:10px">${official.length?official.map(c=>`<span class="status-chip official">${esc(c.nome)} · ${esc(c.situacaoOficial||officialInfo(c,r,cargo,0)?.label||'TSE')}</span>`).join(''):'<span class="status-chip">'+(isSen?'Os dois líderes são apenas líderes, não eleitos.':'O primeiro colocado ainda é apenas líder.')+'</span>'}</div></div>
  <div class="card pad"><div class="eyebrow">Votos</div><div class="section-title">Resumo</div>${donut(r)}<div class="stats-grid"><div class="stat-box"><span>Eleitorado</span><strong>${fmt(r.eleitorado)}</strong></div><div class="stat-box"><span>Comparecimento</span><strong>${fmt(r.comparecimento)}</strong></div><div class="stat-box"><span>Abstenção</span><strong>${fmt(r.abstencao)}</strong></div><div class="stat-box"><span>Válidos</span><strong>${fmt(r.validos)}</strong></div></div></div></aside></div>`;
}
function officialSeatBar(r){
  const rows=r.partidos.map(g=>({sigla:g.sigla,seats:g.vagasOficiais||0})).filter(x=>x.seats>0).sort((a,b)=>b.seats-a.seats),total=Math.max(1,rows.reduce((s,x)=>s+x.seats,0));
  if(!rows.length)return '<div class="empty">O TSE ainda não atribuiu cadeiras.</div>';
  return `<div class="seat-bar">${rows.map(x=>`<span title="${esc(x.sigla)} · ${x.seats}" style="width:${x.seats/total*100}%;background:${hashColor(x.sigla)}"></span>`).join('')}</div><div class="seat-legend">${rows.slice(0,10).map(x=>`<span><i class="legend-dot" style="display:inline-block;background:${hashColor(x.sigla)}"></i> ${esc(x.sigla)} ${x.seats}</span>`).join('')}</div>`;
}
function renderProportionalCandidateRanking(r,cargo){
  const list=orderedCandidates(r);
  const first=list.slice(0,80),rest=list.slice(80);
  const rows=first.map((c,i)=>candidateRow(c,r,cargo,i)).join('');
  const extra=rest.length?`<div class="candidate-list prop-candidate-more hidden">${rest.map((c,i)=>candidateRow(c,r,cargo,i+80)).join('')}</div>
    <button class="modern-link-btn prop-show-all" data-show-prop-all type="button">Mostrar todos os ${fmt(list.length)} candidatos <span>↓</span></button>`:'';
  return `<section class="card pad section prop-candidates-card">
    <div class="section-head"><div><div class="eyebrow">Votação nominal</div><div class="section-title">Candidatos e votos</div></div><div class="section-note">${fmt(list.length)} candidaturas · ordem atual do TSE</div></div>
    <div class="prop-candidate-note">Cada linha mostra <strong>votos nominais</strong>, percentual, partido e situação oficial quando o TSE já tiver atribuído.</div>
    <div class="candidate-list">${rows||'<div class="empty">Nenhuma candidatura disponível neste arquivo.</div>'}</div>
    ${extra}
  </section>`;
}
function wireProportionalCandidateRanking(host){
  const btn=host?.querySelector('[data-show-prop-all]');
  if(!btn)return;
  btn.onclick=()=>{
    const more=host.querySelector('.prop-candidate-more');
    if(!more)return;
    const hidden=more.classList.toggle('hidden');
    btn.innerHTML=hidden?'Mostrar todos os candidatos <span>↓</span>':'Mostrar menos <span>↑</span>';
    if(!hidden)wireFavorites(more);
  };
}

function renderProportional(r,cargo){
  const calc=calcularProporcional(r),calcBy=new Map(calc.partidos.map(x=>[x.id,x])),officialElected=r.candidatos.filter(c=>c.eleitoTse||(/Eleito/i.test(c.situacaoOficial)&&!/Não eleito/i.test(c.situacaoOficial)));
  const rows=r.partidos.map(g=>{const c=calcBy.get(g.id);return{...g,app:c?.total||0,qp:c?.qp||0,sobra:c?.vagasSobra||0,pctQE:c?.pctQE||0}}).sort((a,b)=>(b.vagasOficiais||0)-(a.vagasOficiais||0)||b.app-a.app||b.votosValidos-a.votosValidos);
  const qeTse=r.qe||0,qeApp=calc.qe||0;
  return `
  <div class="prop-metrics">
    <div class="card prop-metric"><span>Vagas do cargo</span><strong>${fmt(r.vagas)}</strong><small>TSE · campo nv</small></div>
    <div class="card prop-metric"><span>QE oficial TSE</span><strong>${fmt(qeTse)}</strong><small>${qeTse?'publicado pelo TSE':'aguardando votos válidos'}</small></div>
    <div class="card prop-metric"><span>QE cálculo app</span><strong>${fmt(qeApp)}</strong><small>auditável com os dados atuais</small></div>
    <div class="card prop-metric"><span>Votos válidos</span><strong>${fmt(r.validos)}</strong><small>${pct(r.pctTotalizado)} apurado</small></div>
  </div>
  <div class="thresholds"><div class="threshold"><small>10% do QE · mínimo individual do QP</small><strong>${fmt(Math.ceil(qeApp*.10))}</strong></div><div class="threshold"><small>20% do QE · candidato na 1ª sobra</small><strong>${fmt(Math.ceil(qeApp*.20))}</strong></div><div class="threshold"><small>80% do QE · grupo na 1ª sobra</small><strong>${fmt(Math.ceil(qeApp*.80))}</strong></div></div>
  ${r.pctTotalizado===0?'<div class="alert waiting" style="margin-top:12px">As <strong>'+fmt(r.vagas)+' vagas</strong> já são conhecidas. QE, QP, sobras e distribuição de cadeiras permanecem em zero até o TSE publicar votos válidos.</div>':''}
  <div class="prop-grid">
    <section class="card pad"><div class="section-head"><div><div class="eyebrow">Cadeiras por partido/federação</div><div class="section-title">TSE agora × cálculo do app</div></div><div class="section-note">“TSE agora” usa exatamente o campo vag do EA20</div></div>
      ${officialSeatBar(r)}
      <div class="table-wrap"><table class="seat-table"><thead><tr><th>Grupo</th><th>Votos</th><th>QP</th><th>Sobras app</th><th>TSE agora</th><th>App</th></tr></thead><tbody>${rows.map(g=>`<tr><td><strong>${esc(g.sigla)}</strong><br><span class="muted">${esc(g.tipo==='federacao'?'federação':'partido')}</span></td><td>${fmt(g.votosValidos)}</td><td>${g.qp}</td><td>${g.sobra}</td><td class="seat-big">${g.vagasOficiais||0}</td><td class="seat-big">${g.app}</td></tr>`).join('')}</tbody></table></div>
    </section>
    <aside class="stack">
      <div class="card pad"><div class="eyebrow">A conta</div><div class="section-title">Como as cadeiras foram calculadas</div><div class="steps" style="margin-top:12px">${calc.passos.map((x,i)=>`<div class="step"><div class="step-no">${i+1}</div><p>${esc(x)}</p></div>`).join('')}</div>${calc.warnings.length?'<div class="alert waiting" style="margin-top:10px">'+calc.warnings.map(esc).join('<br>')+'</div>':''}</div>
      <div class="card pad"><div class="eyebrow">Sobras</div><div class="section-title">Rodadas por maiores médias</div><div class="round-list">${calc.rodadas.length?calc.rodadas.slice(0,12).map(x=>`<div class="round"><div class="round-head"><span>Rodada ${x.rodada} · ${esc(x.fase)}</span><span>${x.empateIndefinido?'empate':''}</span></div><div class="round-winner">${x.vencedorSigla?esc(x.vencedorSigla)+' · '+esc(x.candidatoNome||''):'sem cadeira atribuída'}</div></div>`).join(''):'<div class="empty">As rodadas aparecerão quando houver votos válidos.</div>'}</div></div>
    </aside>
  </div>
  ${renderProportionalCandidateRanking(r,cargo)}
  <div class="two-col section" style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
    <section class="card pad"><div class="section-head"><div><div class="eyebrow">Situação oficial TSE</div><div class="section-title">Eleitos e suplentes</div></div><div class="section-note">${officialElected.length} eleito(s) oficial(is)</div></div><div class="candidate-list">${r.candidatos.filter(c=>c.situacaoOficial||c.eleitoTse).slice(0,80).map((c,i)=>candidateRow(c,r,cargo,i)).join('')||'<div class="empty">O TSE ainda não atribuiu situação final aos candidatos.</div>'}</div></section>
    <section class="card pad"><div class="section-head"><div><div class="eyebrow">Projeção auditável</div><div class="section-title">Eleitos pelo cálculo atual</div></div><div class="section-note">${calc.eleitos.length} identidade(s) calculada(s)</div></div><div class="candidate-list">${calc.eleitos.slice(0,80).map((e,i)=>candidateRow(e.candidato,r,cargo,i)).join('')||'<div class="empty">Sem projeção enquanto não houver votos suficientes.</div>'}</div></section>
  </div>`;
}
function createHemicycle(groups,totalSeats=513){
  const seats=[];for(const g of groups)for(let i=0;i<g.seats;i++)seats.push({color:hashColor(g.sigla),sigla:g.sigla});
  while(seats.length<totalSeats)seats.push({color:'var(--border)',sigla:'não atribuída'});seats.length=totalSeats;
  const rings=12,rads=Array.from({length:rings},(_,i)=>62+i*14),sum=rads.reduce((a,b)=>a+b,0),counts=rads.map(r=>Math.floor(totalSeats*r/sum));let diff=totalSeats-counts.reduce((a,b)=>a+b,0);for(let i=rings-1;diff>0;i=(i-1+rings)%rings,diff--)counts[i]++;
  let idx=0,circles='';for(let ri=0;ri<rings;ri++){const count=counts[ri],rad=rads[ri];for(let j=0;j<count;j++){const a=Math.PI+(Math.PI*(j+.5)/count),x=260+Math.cos(a)*rad,y=222+Math.sin(a)*rad,s=seats[idx++];circles+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.1" fill="${s.color}"><title>${esc(s.sigla)}</title></circle>`}}
  return `<svg viewBox="0 0 520 240" role="img" aria-label="Hemiciclo com ${totalSeats} cadeiras">${circles}<text x="260" y="218" text-anchor="middle" fill="var(--text)" font-size="24" font-weight="900">${groups.reduce((s,g)=>s+g.seats,0)} / ${totalSeats}</text><text x="260" y="234" text-anchor="middle" fill="var(--muted)" font-size="9">cadeiras atribuídas pelo TSE agora</text></svg>`;
}
function bars(rows,key='seats',maxRows=14){
  const data=rows.slice().sort((a,b)=>(b[key]||0)-(a[key]||0)).slice(0,maxRows),max=Math.max(1,...data.map(x=>x[key]||0));
  return `<div class="chart-bars">${data.map(x=>`<div class="chart-row"><div class="chart-label">${esc(x.sigla)}</div><div class="chart-track"><span style="width:${(x[key]||0)/max*100}%;background:${hashColor(x.sigla)}"></span></div><div class="chart-value">${fmt(x[key]||0)}</div></div>`).join('')}</div>`;
}
async function loadCongress(force=false){
  const host=$('#congressContent');host.innerHTML='<div class="page-head"><div><div class="eyebrow">Congresso Nacional</div><h1 class="page-title">Câmara e Senado</h1></div></div><div class="card pad loading"><div class="empty">Carregando as 27 UFs em lotes seguros…</div></div>';
  let cam,sen;
  if(API_BASE){const agg=await congressClient(force);cam=agg.cam;sen=agg.sen}
  else{
    const suffix=force?'&t='+Date.now():'';
    [cam,sen]=await Promise.all([fetch('/api/congress?kind=camara'+suffix,{cache:'no-store'}).then(r=>r.json()),fetch('/api/congress?kind=senado'+suffix,{cache:'no-store'}).then(r=>r.json())]);
  }
  S.congress={camara:cam,senado:sen};const seats=(cam.officialSeats||[]).reduce((s,x)=>s+x.seats,0);
  host.innerHTML=`
  <div class="page-head"><div><div class="eyebrow">Congresso Nacional</div><h1 class="page-title">Câmara e Senado</h1><div class="page-sub">Distribuição oficial atualizada UF por UF. Cadeiras ainda não atribuídas permanecem neutras.</div></div><div class="source-pill">${cam.ufsLoaded}/27 UFs carregadas</div></div>
  <div class="congress-top">
    <section class="card hemi-card"><div class="section-head"><div><div class="eyebrow">Câmara dos Deputados</div><div class="section-title">Hemiciclo · TSE agora</div></div><div class="section-note">${seats} de ${cam.seatsTotal||513} cadeiras atribuídas</div></div><div class="hemicycle-wrap">${createHemicycle(cam.officialSeats||[],cam.seatsTotal||513)}</div><div class="seat-legend">${(cam.officialSeats||[]).slice(0,14).map(x=>`<span><i class="legend-dot" style="display:inline-block;background:${hashColor(x.sigla)}"></i> ${esc(x.sigla)} ${x.seats}</span>`).join('')}</div></section>
    <aside class="congress-side"><div class="card metric-card"><div class="metric-label">Cadeiras Câmara</div><div class="metric-value">${seats}<span style="font-size:14px;color:var(--muted)"> / ${cam.seatsTotal||513}</span></div><div class="metric-foot">campo vag agregado das 27 UFs</div></div><div class="card metric-card"><div class="metric-label">Senadores oficiais em 2026</div><div class="metric-value">${sen.officialCount||0}<span style="font-size:14px;color:var(--muted)"> / 54</span></div><div class="metric-foot">2 vagas por UF</div></div><div class="card pad"><div class="eyebrow">Cadeiras por grupo</div><div class="section-title">Distribuição atual</div><div style="margin-top:12px">${bars(cam.officialSeats||[])}</div></div></aside>
  </div>
  <section class="section"><div class="section-head"><div><div class="eyebrow">Senado Federal</div><div class="section-title">Duas vagas por UF</div></div><div class="section-note">“líder” só vira “eleito TSE” quando o arquivo oficial indicar</div></div><div class="senate-grid">${renderSenateGrid(sen)}</div></section>
  <section class="section"><div class="two-col" style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div class="card pad"><div class="eyebrow">Câmara</div><div class="section-title">Tabela de cadeiras</div><div class="table-wrap"><table class="seat-table"><thead><tr><th>Partido/Federação</th><th>Votos</th><th>Cadeiras</th></tr></thead><tbody>${(cam.officialSeats||[]).map(x=>`<tr><td><strong>${esc(x.sigla)}</strong></td><td>${fmt(x.votes)}</td><td class="seat-big">${x.seats}</td></tr>`).join('')}</tbody></table></div></div><div class="card pad"><div class="eyebrow">Senado</div><div class="section-title">Eleitos por partido</div><div style="margin-top:12px">${sen.officialCount?bars(sen.byParty||[]):'<div class="empty">O TSE ainda não atribuiu senadores eleitos.</div>'}</div></div></div></section>`;
}
function renderSenateGrid(sen){
  return (sen.ufs||[]).map(u=>{const list=u.official?.length?u.official:u.leaders||[];return `<div class="senate-uf"><strong>${u.uf} · ${pct(u.pct||0)}</strong>${list.slice(0,2).map(c=>`<div class="senate-name ${c.official?'official':''}">${c.official?'✓ ':''}${esc(c.nome)} · ${esc(c.partido)}</div>`).join('')||'<div class="senate-name">aguardando</div>'}</div>`}).join('');
}

const FAVORITES_KEY='ap26-favorites-v1';
function favoriteKey(c){
  return [c.sqcand||c.id||c.numero||'',c.cargoCodigo||c.cargo||'',c.uf||''].join('|');
}
function getFavorites(){
  try{
    const list=JSON.parse(localStorage.getItem(FAVORITES_KEY)||'[]');
    return Array.isArray(list)?list:[];
  }catch{return[]}
}
function saveFavorites(list){
  localStorage.setItem(FAVORITES_KEY,JSON.stringify(list.slice(0,100)));
}
function registerCandidate(c){
  const key=favoriteKey(c);
  if(key)S.candidateIndex.set(key,c);
  return key;
}
function isFavorite(c){
  const key=favoriteKey(c);
  return getFavorites().some(x=>favoriteKey(x)===key);
}
function candidateForFavorite(c,r,cargo){
  return {
    ...c,
    sqcand:c.sqcand||c.id||'',
    cargoCodigo:String(cargo||c.cargoCodigo||''),
    cargo:c.cargo||CARGO[String(cargo)]||String(cargo||'Candidato'),
    uf:c.uf||r?.abrangencia||(String(cargo)==='1'?'BR':''),
    percentual:c.percentual??c.pct??0,
    status:c.status||c.st||c.situacaoOficial||'',
    foto:c.foto||c.fotoUrl||''
  };
}
function favoriteButton(c){
  const key=registerCandidate(c),favs=getFavorites(),idx=favs.findIndex(x=>favoriteKey(x)===key),on=idx>=0;
  if(on){
    favs[idx]={...favs[idx],...c};
    saveFavorites(favs);
  }
  return `<button class="favorite-btn ${on?'active':''}" data-favorite-key="${encodeURIComponent(key)}" aria-label="${on?'Remover dos favoritos':'Adicionar aos favoritos'}" title="${on?'Remover dos favoritos':'Favoritar'}">${on?'★':'☆'}</button>`;
}
function updateFavoriteSnapshots(results){
  const fresh=new Map((results||[]).map(c=>[favoriteKey(c),c]));
  const favs=getFavorites();let changed=false;
  const next=favs.map(old=>{const n=fresh.get(favoriteKey(old));if(n){changed=true;return n}return old});
  if(changed)saveFavorites(next);
}
function searchResultCard(c,{favoriteContext=false}={}){
  const status=c.status||c.st||'';
  return `<div class="search-result ${favoriteContext?'favorite-card':''}" data-candidate-key="${esc(favoriteKey(c))}">
    ${avatar(c)}
    <div><div class="result-context">${esc(c.cargo)} · ${esc(c.uf)}</div><div class="cand-name">${esc(c.nome)}</div>
      <div class="cand-meta">${esc(c.numero)} · ${esc(c.partido)} · ${fmt(c.votos)} votos</div>
      ${status?`<span class="${/Não eleito|Suplente/i.test(status)?'supp-badge':'official-badge'}">${esc(status)} · TSE</span>`:''}
    </div>
    <div class="result-actions">${favoriteButton(c)}<div class="right-stat"><strong>${pct(c.percentual??c.pct)}</strong></div></div>
  </div>`;
}
function updateFavoriteBadges(){
  const n=getFavorites().length;
  $$('[data-fav-badge]').forEach(el=>{el.textContent=String(n);el.classList.toggle('hidden',n===0)});
}
function renderFavorites(){
  updateFavoriteBadges();
}
function favoriteCargoCode(c){
  if(c.cargoCodigo)return String(c.cargoCodigo);
  const label=String(c.cargo||'').toLowerCase();
  if(label.includes('presidente'))return '1';
  if(label.includes('governador'))return '3';
  if(label.includes('senador'))return '5';
  if(label.includes('federal'))return '6';
  if(label.includes('distrital'))return '8';
  if(label.includes('estadual'))return '7';
  return '';
}
function favoritePageCard(c){
  registerCandidate(c);
  const status=c.status||c.st||c.situacaoOficial||'';
  return `<div class="favorite-page-card">
    ${avatar(c)}
    <div class="favorite-main"><div class="result-context">${esc(c.cargo||CARGO[favoriteCargoCode(c)]||'Candidato')} · ${esc(c.uf||'')}</div>
      <div class="cand-name">${esc(c.nome)}</div>
      <div class="cand-meta">${esc(c.numero)} · ${esc(c.partido)} · ${fmt(c.votos)} votos</div>
      ${status?`<span class="${/Não eleito|Suplente/i.test(status)?'supp-badge':'official-badge'}">${esc(status)} · TSE</span>`:''}
    </div>
    <div class="favorite-side">${favoriteButton(c)}<strong>${pct(c.percentual??c.pct)}</strong></div>
  </div>`;
}
function renderFavoritesPage(){
  const host=$('#favoritesContent');if(!host)return;
  const favs=getFavorites();
  favs.forEach(registerCandidate);
  updateFavoriteBadges();
  if(!favs.length){
    host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Acompanhamento</div><h1 class="page-title">Favoritos</h1><div class="page-sub">Seus candidatos favoritos, de qualquer cargo, ficam reunidos aqui.</div></div></div>
      <div class="card pad favorite-empty"><div class="favorite-empty-star">☆</div><h3>Nenhum favorito ainda</h3><p>Vá em Buscar ou abra um cargo e toque na estrela do candidato.</p><button class="modern-link-btn" data-go="buscar">Buscar candidatos <span>→</span></button></div>`;
    wireGo();return;
  }
  const order=['1','3','5','6','7','8'];
  const groups=new Map();
  for(const c of favs){const code=favoriteCargoCode(c)||'outro';if(!groups.has(code))groups.set(code,[]);groups.get(code).push(c)}
  const codes=[...order.filter(x=>groups.has(x)),...([...groups.keys()].filter(x=>!order.includes(x)))];
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Acompanhamento</div><h1 class="page-title">Favoritos</h1><div class="page-sub">${favs.length} candidato(s) salvo(s) neste aparelho · atualizados com dados do TSE.</div></div><div class="favorite-total">★ ${favs.length}</div></div>
    <div class="favorite-groups">${codes.map(code=>{
      const items=groups.get(code).slice().sort((x,y)=>String(x.uf||'').localeCompare(String(y.uf||''),'pt-BR')||String(x.nome||'').localeCompare(String(y.nome||''),'pt-BR'));
      return `<section class="card favorite-group"><div class="favorite-group-head"><div><span class="eyebrow">${esc(CARGO[code]||'Candidatos')}</span><strong>${items.length} favorito(s)</strong></div></div><div class="favorite-page-list">${items.map(favoritePageCard).join('')}</div></section>`;
    }).join('')}</div>`;
  wireFavorites(host);
}
async function refreshFavorites(force=false){
  const favs=getFavorites();if(!favs.length){renderFavoritesPage();return}
  const groups=new Map();
  for(const f of favs){
    const cargo=favoriteCargoCode(f);if(!cargo)continue;
    const uf=cargo==='1'?'BR':String(f.uf||'').toUpperCase();if(!uf)continue;
    const k=cargo+':'+uf;if(!groups.has(k))groups.set(k,{cargo,uf,items:[]});groups.get(k).items.push(f);
  }
  const entries=[...groups.values()];
  const updated=new Map(favs.map(x=>[favoriteKey(x),x]));
  for(let i=0;i<entries.length;i+=4){
    const batch=entries.slice(i,i+4);
    const docs=await Promise.all(batch.map(async g=>{try{return{g,r:await fetchResult(g.cargo,g.uf,force)}}catch{return{g,r:null}}}));
    for(const {g,r} of docs){
      if(!r)continue;
      for(const old of g.items){
        const id=String(old.sqcand||old.id||''),num=String(old.numero||'');
        const c=r.candidatos.find(x=>String(x.id||x.sqcand||'')===id)||(num?r.candidatos.find(x=>String(x.numero||'')===num):null);
        if(c){
          const fresh=candidateForFavorite(c,r,g.cargo);
          const oldKey=favoriteKey(old);
          updated.delete(oldKey);
          updated.set(favoriteKey(fresh),fresh);
        }
      }
    }
  }
  saveFavorites([...updated.values()]);
  renderFavoritesPage();
  syncFavoriteButtons();
}
async function loadFavorites(force=false){
  renderFavoritesPage();
  await refreshFavorites(force);
}
function syncFavoriteButtons(){
  $$('[data-favorite-key]').forEach(btn=>{
    let key='';try{key=decodeURIComponent(btn.dataset.favoriteKey||'')}catch{key=btn.dataset.favoriteKey||''}
    const on=getFavorites().some(x=>favoriteKey(x)===key);
    btn.classList.toggle('active',on);
    btn.textContent=on?'★':'☆';
    btn.setAttribute('aria-label',on?'Remover dos favoritos':'Adicionar aos favoritos');
    btn.title=on?'Remover dos favoritos':'Favoritar';
  });
}
function toggleFavorite(key){
  const favs=getFavorites(),idx=favs.findIndex(x=>favoriteKey(x)===key);
  if(idx>=0)favs.splice(idx,1);
  else{
    const c=S.candidateIndex.get(key);
    if(!c)return;
    favs.unshift(c);
  }
  saveFavorites(favs);
  if(navigator.vibrate)navigator.vibrate(25);
  renderFavorites();
  syncFavoriteButtons();
  if(S.view==='favoritos')renderFavoritesPage();
}
function wireFavorites(root=document){
  root.querySelectorAll('[data-favorite-key]').forEach(btn=>{
    btn.onclick=e=>{
      e.preventDefault();e.stopPropagation();
      let key='';try{key=decodeURIComponent(btn.dataset.favoriteKey||'')}catch{key=btn.dataset.favoriteKey||''}
      toggleFavorite(key);
    };
  });
}

function searchUI(){
  const ufOpts='<option value="">Brasil inteiro</option>'+UFS.map(([u,n])=>`<option value="${u.toLowerCase()}" ${u==='MG'?'selected':''}>${n} (${u})</option>`).join('');
  return `<div class="page-head"><div><div class="eyebrow">Base oficial 2026</div><h1 class="page-title">Buscar candidato</h1><div class="page-sub">Busque e toque na estrela para acompanhar seus candidatos favoritos.</div></div></div>
  <div class="card search-card">
    <div class="search-controls"><input id="searchInput" class="search-input" placeholder="Ex.: Ana Paula Siqueira, 13444, PT" autocomplete="off"><select id="searchUF" class="search-select">${ufOpts}</select><select id="searchCargo" class="search-select"><option value="">Todos os cargos</option><option value="1">Presidente</option><option value="3">Governador</option><option value="5">Senador</option><option value="6">Dep. Federal</option><option value="7">Dep. Estadual</option><option value="8">Dep. Distrital</option></select><button id="searchBtn" class="primary-btn">Buscar</button></div>
    <div class="search-meta" id="searchMeta">UF padrão: Minas Gerais. Escolha “Brasil inteiro” para varrer todas as UFs.</div>
    <div id="searchResults" class="search-results"></div>
  </div>`;
}
function initSearch(){
  const host=$('#searchContent');
  if(!host.dataset.ready){host.innerHTML=searchUI();host.dataset.ready='1'}
  const btn=$('#searchBtn'),input=$('#searchInput');
  btn.onclick=doSearch;
  input.onkeydown=e=>{if(e.key==='Enter')doSearch()};
  updateFavoriteBadges();
}
async function doSearch(){
  const q=$('#searchInput').value.trim(),uf=$('#searchUF').value,cargo=$('#searchCargo').value;
  if(q.length<3){$('#searchMeta').textContent='Digite pelo menos 3 caracteres.';return}
  const btn=$('#searchBtn');
  btn.disabled=true;btn.textContent='Buscando…';
  $('#searchResults').innerHTML='<div class="card compact-pad loading"><div class="empty">Consultando arquivos oficiais do TSE…</div></div>';
  try{
    const r=await fetch(apiUrl('/api/search?q='+encodeURIComponent(q)+(uf?'&uf='+encodeURIComponent(uf):'')+(cargo?'&cargo='+encodeURIComponent(cargo):'')),{cache:'no-store'});
    const j=await r.json();
    const results=j.results||[];
    results.forEach(registerCandidate);
    updateFavoriteSnapshots(results);
    $('#searchMeta').textContent=`${j.count||0} resultado(s) · ${j.scanned||0} arquivo(s) oficiais consultados`;
    $('#searchResults').innerHTML=results.map(c=>searchResultCard(c)).join('')||'<div class="empty">Nenhum candidato encontrado nos arquivos consultados.</div>';
    wireFavorites($('#searchResults'));
    syncFavoriteButtons();
  }catch(e){
    $('#searchMeta').textContent='Falha temporária ao consultar o TSE.';
    $('#searchResults').innerHTML='<div class="empty">Tente novamente em alguns segundos.</div>';
  }finally{
    btn.disabled=false;btn.textContent='Buscar';
  }
}


function loadHow(){
  const host=$('#howContent');host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Transparência</div><h1 class="page-title">Como funciona</h1><div class="page-sub">O app separa dado oficial de cálculo próprio.</div></div></div><div class="info-grid">
  <div class="card info-card"><h3>ELEITO / 2º TURNO · TSE</h3><p>Para Presidente e Governador, o campo <strong>md</strong> do arquivo oficial indica quando a eleição fica matematicamente definida antes do fim: <strong>e</strong> = eleito e <strong>s</strong> = segundo turno. O candidato correspondente vem com <strong>e=s</strong>.</p></div>
  <div class="card info-card"><h3>Situação final do candidato</h3><p>Na totalização final, usamos diretamente o campo <strong>st</strong> do TSE: Eleito, Eleito por QP, Eleito por média, Não eleito, 2º turno ou Suplente.</p></div>
  <div class="card info-card"><h3>TSE agora</h3><p>Para deputados, “TSE agora” usa o campo oficial <strong>vag</strong> de cada partido/federação. Ele pode mudar a cada totalização e só é definitivo no fim.</p></div>
  <div class="card info-card"><h3>Cálculo do app</h3><p>Mostramos QE, QP, limiares e sobras por maiores médias de forma separada. Essa coluna serve para auditoria e nunca substitui o status oficial do TSE.</p></div></div>`;
}
async function loadView(view,force=false){
  try{
    if(view==='agora')await loadAgora(force);
    else if(view==='presidente')await loadPresident(force);
    else if(view==='estados')await loadState(force);
    else if(view==='congresso')await loadCongress(force);
    else if(view==='favoritos')await loadFavorites(force);
    else if(view==='buscar')initSearch();
    else if(view==='como')loadHow();
  }catch(e){const id=view==='presidente'?'presidentContent':view==='estados'?'stateContent':view==='congresso'?'congressContent':view==='buscar'?'searchContent':view==='favoritos'?'favoritesContent':view==='como'?'howContent':'agoraContent';$('#'+id).innerHTML=`<div class="card pad"><div class="alert danger">Não foi possível carregar esta tela agora. ${esc(e.message||'')} <button class="ghost-btn" id="retryBtn">tentar novamente</button></div></div>`;$('#retryBtn')?.addEventListener('click',()=>loadView(view,true))}
}
function showView(view){
  S.view=view;$$('.view').forEach(v=>v.classList.toggle('active',v.id==='view-'+view));$$('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));window.scrollTo(0,0);loadView(view,false);restartPoll();
}
function wireGo(){
  $$('[data-go]').forEach(b=>b.onclick=()=>showView(b.dataset.go));$$('[data-uf]').forEach(b=>b.onclick=()=>{S.uf=b.dataset.uf;S.cargo='3';showView('estados')});
}
function restartPoll(){clearInterval(S.poll);if(['agora','presidente','estados','congresso','favoritos'].includes(S.view))S.poll=setInterval(()=>{if(document.visibilityState==='visible')loadView(S.view,true)},30000)}
function setTheme(t){document.documentElement.dataset.theme=t;localStorage.setItem('ap26-theme',t);$('#themeBtn').textContent=t==='dark'?'☀':'☾'}
function initTheme(){const t=localStorage.getItem('ap26-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');setTheme(t)}
async function boot(){
  initTheme();$('#themeBtn').onclick=()=>setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark');$('#refreshBtn').onclick=()=>loadView(S.view,true);
  $$('[data-view]').forEach(b=>b.onclick=()=>showView(b.dataset.view));$('.brand').onclick=()=>showView('agora');
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')loadView(S.view,true)});
  await discoverCodes();updateFavoriteBadges();showView('agora');
}
boot();

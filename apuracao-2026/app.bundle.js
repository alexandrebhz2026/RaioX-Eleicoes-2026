/* Apuracao 2026 browser bundle v5.16 */
function tseInt(v){return Number(String(v??'0').replace(/\./g,'').replace(',','.'))||0}
function tsePct(v){return Number(String(v??'0').replace(',','.'))||0}
function roundQE(vv,seats){if(seats<=0)return 0;const raw=vv/seats,f=Math.floor(raw);return raw-f>0.5?f+1:f}
function birthTimestamp(s){if(!s)return undefined;const m=/^(\d{2})\/(\d{2})\/(\d{4})$/.exec(String(s).trim());if(!m)return undefined;return Date.UTC(+m[3],+m[2]-1,+m[1])}
function candidateSort(a,b){if(b.votos!==a.votos)return b.votos-a.votos;const at=birthTimestamp(a.dataNascimento),bt=birthTimestamp(b.dataNascimento);if(at!==undefined&&bt!==undefined&&at!==bt)return at-bt;return a.nome.localeCompare(b.nome,'pt-BR')}
function validDest(c){return !c.destinacao||(/válid|valido/i.test(c.destinacao)&&!/anulad/i.test(c.destinacao))}
function candidateTieUndefined(a,b){if(!a||!b||a.votos!==b.votos)return false;const at=birthTimestamp(a.dataNascimento),bt=birthTimestamp(b.dataNascimento);return at===undefined||bt===undefined||at===bt}
function sortedCandidates(group,minVotes,electedIds){return group.candidatos.filter(c=>validDest(c)&&!electedIds.has(c.id)&&c.votos>=minVotes).slice().sort(candidateSort)}
function chooseCandidate(group,minVotes,electedIds){const candidates=sortedCandidates(group,minVotes,electedIds);return{candidates,candidate:candidates[0],tieUndefined:candidateTieUndefined(candidates[0],candidates[1])}}
function exactAverageCompare(a,b){const l=a.votos*b.divisor,r=b.votos*a.divisor;if(l!==r)return r-l;if(a.votos!==b.votos)return b.votos-a.votos;if((a.candidatoVotos??-1)!==(b.candidatoVotos??-1))return(b.candidatoVotos??-1)-(a.candidatoVotos??-1);return a.sigla.localeCompare(b.sigla,'pt-BR')}
function sameLegalPriority(a,b){if(!a||!b)return false;return a.votos*b.divisor===b.votos*a.divisor&&a.votos===b.votos&&(a.candidatoVotos??-1)===(b.candidatoVotos??-1)}
function adaptUnified(raw,{electionCode,uf,cargoCode,photoBase='/api/tse?path='}){
 const parsed=raw||{},cargoRaw=(parsed.carg||[]).find(c=>String(c.cd)===String(cargoCode))||(parsed.carg||[])[0];if(!cargoRaw)throw new Error('Arquivo TSE sem cargo');
 const partidos=(cargoRaw.agr||[]).map((agr,ai)=>{const first=(agr.par||[])[0]||{},tipo=agr.tp==='f'?'federacao':'partido',sigla=agr.com||first.sg||agr.nm||`AGR ${ai+1}`,nome=agr.nm||first.nm||sigla;let nNom=0,nLeg=0;for(const p of agr.par||[]){nNom+=tseInt(p.tvtn);nLeg+=tseInt(p.tvtl)}const agrNom=tseInt(agr.tvtn),agrLeg=tseInt(agr.tvtl),votosNominais=agrNom>0?agrNom:nNom,votosLegenda=agrLeg>0?agrLeg:nLeg;const candidatos=[];for(const p of agr.par||[])for(const c of p.cand||[]){const abr=parsed.tpabr==='br'?'br':String(uf).toLowerCase();const path=`/oficial/ele2026/${electionCode}/fotos/${abr}/${c.sqcand}.jpeg`;candidatos.push({id:c.sqcand||`${p.n}-${c.n}-${c.seq}`,numero:c.n||'',nome:c.nmu||c.nm||'',partido:p.sg||p.nm||'',federacao:tipo==='federacao'?sigla:undefined,grupoId:agr.n||`agr-${ai}`,dataNascimento:c.dt||undefined,votos:tseInt(c.vap),pct:tsePct(c.pvap),eleitoTse:String(c.e).toLowerCase()==='s',situacaoOficial:(c.st||''),destinacao:c.dvt||p.dvt||'Válido',fotoUrl:photoBase+encodeURIComponent(path)})}candidatos.sort(candidateSort);return{id:agr.n||`agr-${ai}`,sigla,nome,tipo,composicao:agr.com||undefined,votosNominais,votosLegenda,votosValidos:votosNominais+votosLegenda,vagasOficiais:tseInt(agr.vag),candidatos}});
 const candidatos=partidos.flatMap(p=>p.candidatos).sort(candidateSort),s=parsed.s||{},e=parsed.e||{},v=parsed.v||{};
 return{cargoCode:String(cargoRaw.cd||cargoCode),abrangencia:String(uf).toUpperCase(),pctTotalizado:tsePct(s.pst),secoesTotal:tseInt(s.ts),secoesTotalizadas:tseInt(s.st),secoesNaoTotalizadas:tseInt(s.snt),totalizadoEm:[parsed.dg,parsed.hg].filter(Boolean).join(' '),eleitorado:tseInt(e.te),comparecimento:tseInt(e.c),abstencao:tseInt(e.a),validos:tseInt(v.vv),brancos:tseInt(v.vb),nulos:tseInt(v.vn||v.tvn),vagas:tseInt(cargoRaw.nv),qe:tseInt(cargoRaw.qe),candidatos,partidos,meta:{awaiting:parsed.and==='n'||tsePct(s.pst)===0,turno:String(parsed.t||'1'),tf:String(parsed.tf||'n'),and:String(parsed.and||'n'),md:String(parsed.md||'n'),esae:String(parsed.esae||'n'),mnae:Array.isArray(parsed.mnae)?parsed.mnae:[],fase:String(parsed.f||'o'),idg:String(parsed.idg||''),dataGeracao:String(parsed.dg||''),horaGeracao:String(parsed.hg||'')}}
}
function calcularProporcional(resultado){
 const groups=resultado.partidos.filter(g=>g.votosValidos>0||g.candidatos.some(c=>c.votos>0)),seats=Math.max(0,Math.trunc(resultado.vagas)),vvFromGroups=groups.reduce((s,g)=>s+g.votosValidos,0),vv=Math.max(resultado.validos,vvFromGroups),qe=resultado.qe>0?Math.trunc(resultado.qe):roundQE(vv,seats),warnings=[],electedIds=new Set(),elected=[],actual=new Map(groups.map(g=>[g.id,0])),qpMap=new Map(),qpSeats=new Map(),sobra=new Map(groups.map(g=>[g.id,0])),rodadas=[];let blocked=false,identityUnresolved=false;
 const addPending=(id,n)=>{if(n>0)actual.set(id,(actual.get(id)||0)+n)},allocated=()=>[...actual.values()].reduce((a,b)=>a+b,0);
 if(!seats||!qe||!groups.length)return{vagas:seats,votosValidos:vv,qe,partidos:groups.map(g=>({id:g.id,sigla:g.sigla,nome:g.nome,votos:g.votosValidos,pctQE:0,qp:0,vagasQP:0,vagasSobra:0,total:g.vagasOficiais||0,oficial:g.vagasOficiais||0,apto80:false,candidatosElegiveis10:0,candidatosElegiveis20:0})),rodadas:[],eleitos:[],passos:[`Ainda não há votos válidos suficientes para calcular o QE. ${seats} vaga(s) estão previstas para este cargo.`],warnings,linhaDeCorte:{primeirosDeFora:[],primeirosSuplentesPorGrupo:[]}};
 const elect=(g,c,motivo,rodada)=>{if(!c||electedIds.has(c.id)||elected.length>=seats)return;electedIds.add(c.id);actual.set(g.id,(actual.get(g.id)||0)+1);elected.push({candidato:c,grupoId:g.id,grupoSigla:g.sigla,motivo,rodada})};
 const ten=qe*.10;for(const g of groups){const qp=Math.floor(g.votosValidos/qe);qpMap.set(g.id,qp);const cs=sortedCandidates(g,ten,electedIds),alloc=Math.min(qp,cs.length);let certain=alloc,pending=0;if(alloc>0&&alloc<cs.length&&candidateTieUndefined(cs[alloc-1],cs[alloc])){const tied=cs[alloc-1].votos;let start=alloc-1;while(start>0&&cs[start-1]?.votos===tied)start--;certain=start;pending=alloc-certain;identityUnresolved=true;blocked=true;warnings.push(`${g.sigla}: empate sem idade suficiente em ${pending} vaga(s) de QP.`)}qpSeats.set(g.id,alloc);cs.slice(0,certain).forEach(c=>elect(g,c,'QP'));addPending(g.id,pending);if(qp-alloc>0)warnings.push(`${g.sigla}: ${qp-alloc} vaga(s) de QP seguem para sobras por falta de candidato com 10% do QE.`)}
 let remaining=Math.max(0,seats-allocated()),roundNo=0;
 const runRound=phase=>{roundNo++;const entries=[],choices=new Map();for(const g of groups){const qp=qpMap.get(g.id)||0,sv=sobra.get(g.id)||0,divisor=qp+sv+1,threshold=phase==='fase 1'?qe*.20:0,choice=chooseCandidate(g,threshold,electedIds);choices.set(g.id,choice);const partyEligible=phase==='fase 1'?g.votosValidos>=qe*.80:true,candidateEligible=!!choice.candidate,apto=partyEligible&&candidateEligible;entries.push({grupoId:g.id,sigla:g.sigla,votos:g.votosValidos,divisor,vagasAteAgora:actual.get(g.id)||0,media:g.votosValidos/divisor,candidatoId:choice.candidate?.id,candidatoNome:choice.candidate?.nome,candidatoVotos:choice.candidate?.votos,apto,motivoInaptidao:!partyEligible?'menos de 80% do QE':!candidateEligible?(phase==='fase 1'?'sem candidato com 20% do QE':'sem candidato remanescente'):undefined})}const eligible=entries.filter(e=>e.apto).sort(exactAverageCompare),winner=eligible[0],runner=eligible[1];if(!winner){rodadas.push({rodada:roundNo,fase:phase,entries});return'no-eligible'}if(sameLegalPriority(winner,runner)){rodadas.push({rodada:roundNo,fase:phase,entries,empateIndefinido:true});warnings.push(`Empate indefinido na rodada ${roundNo}.`);return'blocked'}const g=groups.find(x=>x.id===winner.grupoId),choice=choices.get(g.id);if(choice.tieUndefined){addPending(g.id,1);sobra.set(g.id,(sobra.get(g.id)||0)+1);identityUnresolved=true;rodadas.push({rodada:roundNo,fase:phase,entries,vencedorId:g.id,vencedorSigla:g.sigla,empateIndefinido:true});return'blocked'}elect(g,choice.candidate,phase==='fase 1'?'média fase 1':'média final',roundNo);sobra.set(g.id,(sobra.get(g.id)||0)+1);rodadas.push({rodada:roundNo,fase:phase,entries,vencedorId:g.id,vencedorSigla:g.sigla,candidatoId:choice.candidate.id,candidatoNome:choice.candidate.nome});return'awarded'};
 if(!blocked)while(remaining>0){const o=runRound('fase 1');if(o==='awarded'){remaining--;continue}if(o==='blocked')blocked=true;break}if(!blocked)while(remaining>0){const o=runRound('final');if(o==='awarded'){remaining--;continue}if(o==='blocked')blocked=true;break}
 remaining=Math.max(0,seats-allocated());if(remaining>0)warnings.push(`${remaining} vaga(s) ficaram pendentes nos dados atuais.`);
 const partyRows=groups.map(g=>({id:g.id,sigla:g.sigla,nome:g.nome,votos:g.votosValidos,pctQE:qe?g.votosValidos/qe*100:0,qp:qpMap.get(g.id)||0,vagasQP:qpSeats.get(g.id)||0,vagasSobra:sobra.get(g.id)||0,total:actual.get(g.id)||0,oficial:g.vagasOficiais||0,apto80:g.votosValidos>=qe*.80,candidatosElegiveis10:g.candidatos.filter(c=>validDest(c)&&c.votos>=qe*.10).length,candidatosElegiveis20:g.candidatos.filter(c=>validDest(c)&&c.votos>=qe*.20).length})).sort((a,b)=>b.total-a.total||b.votos-a.votos);
 const unelected=groups.flatMap(g=>g.candidatos).filter(c=>validDest(c)&&!electedIds.has(c.id)).sort(candidateSort),electedByVotes=elected.slice().sort((a,b)=>candidateSort(a.candidato,b.candidato)),last=identityUnresolved?undefined:electedByVotes[electedByVotes.length-1],firstOut=identityUnresolved?undefined:unelected[0];
 return{vagas:seats,votosValidos:vv,qe,partidos:partyRows,rodadas,eleitos:elected,suplentes:identityUnresolved?[]:unelected,linhaDeCorte:{ultimoEleito:last,primeirosDeFora:identityUnresolved?[]:unelected.slice(0,5),diferencaVotos:last&&firstOut?Math.abs(last.candidato.votos-firstOut.votos):undefined,primeirosSuplentesPorGrupo:[]},passos:[`Foram considerados ${vv.toLocaleString('pt-BR')} votos válidos para ${seats} vaga(s).`,`O quociente eleitoral (QE) é ${qe.toLocaleString('pt-BR')} votos por cadeira.`,`O QP de cada grupo é piso(votos do grupo ÷ QE), com mínimo individual de 10% do QE.`,`As primeiras sobras exigem grupo com 80% do QE e candidatura com 20% do QE.`,`As sobras finais usam maiores médias entre grupos com candidatura remanescente.`],warnings}
}

const UFS=[
['AC','Acre'],['AL','Alagoas'],['AP','Amapá'],['AM','Amazonas'],['BA','Bahia'],['CE','Ceará'],['DF','Distrito Federal'],['ES','Espírito Santo'],['GO','Goiás'],['MA','Maranhão'],['MT','Mato Grosso'],['MS','Mato Grosso do Sul'],['MG','Minas Gerais'],['PA','Pará'],['PB','Paraíba'],['PR','Paraná'],['PE','Pernambuco'],['PI','Piauí'],['RJ','Rio de Janeiro'],['RN','Rio Grande do Norte'],['RS','Rio Grande do Sul'],['RO','Rondônia'],['RR','Roraima'],['SC','Santa Catarina'],['SP','São Paulo'],['SE','Sergipe'],['TO','Tocantins']
];
const UF_NAME=Object.fromEntries(UFS);
const CARGO={'1':'Presidente','3':'Governador','5':'Senador','6':'Deputado Federal','7':'Deputado Estadual','8':'Deputado Distrital'};
const COLORS=['#7c3aed','#2563eb','#0891b2','#0f9f6e','#d97706','#db2777','#4f46e5','#65a30d','#ea580c','#9333ea','#0284c7','#059669','#ca8a04','#be123c','#6366f1','#15803d','#c2410c','#a21caf'];
const S={
  codes:{fed:'6257',est:'6259',fed2:null,est2:null},view:'agora',uf:'MG',cargo:'3',cache:new Map(),governors:null,
  congress:{camara:null,senado:null},poll:null,loading:new Set(),lastRefresh:null,candidateIndex:new Map(),electedMode:'official',electedUf:'MG',electedCargo:'all',electedName:'',electedParty:'all',electedChartMode:'party',
  presidentMode:'auto',pollData:null,pollScope:'BR',round2Ready:false
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
const PARTY_COLORS={
  AGIR:'#00A6B2',
  AVANTE:'#F58220',
  CIDADANIA:'#00A7CE',
  DC:'#005CA9',
  MDB:'#00843D',
  MOBILIZA:'#214E8A',
  NOVO:'#F58220',
  PCB:'#C8102E',
  PCDOB:'#D71920',
  PCO:'#D71920',
  PDT:'#E31B23',
  PL:'#0052A4',
  PMB:'#D81B60',
  PODE:'#00A99D',
  PODEMOS:'#00A99D',
  PP:'#0050A4',
  PRD:'#225AA8',
  PRTB:'#1D4D3E',
  PSB:'#F2C500',
  PSD:'#00529B',
  PSDB:'#005CA9',
  PSOL:'#F4C300',
  PSTU:'#C8102E',
  PT:'#E30613',
  PV:'#008C45',
  REDE:'#00A859',
  REPUBLICANOS:'#00529B',
  SOLIDARIEDADE:'#F58220',
  UNIAO:'#0066B3',
  UP:'#6A1B9A'
};
const FEDERATION_PARTIES=[
  {test:/BRASIL\s+DA\s+ESPERANCA|FE\s+BRASIL/,parties:['PT','PCDOB','PV']},
  {test:/PSDB.*CIDADANIA|CIDADANIA.*PSDB/,parties:['PSDB','CIDADANIA']},
  {test:/PSOL.*REDE|REDE.*PSOL/,parties:['PSOL','REDE']}
];
function partyKey(v=''){
  return String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase().replace(/[^A-Z0-9]/g,'');
}
function partyColor(v=''){
  const key=partyKey(v);
  return PARTY_COLORS[key]||hashColor(key||v);
}
function federationParties(v=''){
  const raw=String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase();
  const exact=FEDERATION_PARTIES.find(x=>x.test.test(raw));
  if(exact)return exact.parties;
  const tokens=raw.split(/[^A-Z0-9]+/).map(partyKey).filter(Boolean);
  const parties=[...new Set(tokens.filter(t=>PARTY_COLORS[t]))];
  return parties.length>1?parties:[];
}
function politicalColor(v=''){
  const fed=federationParties(v);
  return fed.length?partyColor(fed[0]):partyColor(v);
}
function politicalFill(v=''){
  const fed=federationParties(v);
  if(fed.length<2)return politicalColor(v);
  const stops=fed.map((p,i)=>`${partyColor(p)} ${Math.round(i/fed.length*100)}% ${Math.round((i+1)/fed.length*100)}%`).join(',');
  return `linear-gradient(90deg,${stops})`;
}
function tsePath(path){return apiUrl('/api/tse?path='+encodeURIComponent(path))}
function electionCode(cargo,round=1){
  const isFed=String(cargo)==='1';
  if(Number(round)===2)return isFed?S.codes.fed2:S.codes.est2;
  return isFed?S.codes.fed:S.codes.est;
}
function resultPath(cargo,uf,round=1){
  const ele=electionCode(cargo,round);
  if(!ele)throw new Error(round===2?'2º turno ainda não publicado no TSE':'Código da eleição indisponível');
  const abr=String(cargo)==='1'?'br':String(uf).toLowerCase();
  return `/oficial/ele2026/${ele}/dados/${abr}/${abr}-c${String(cargo).padStart(4,'0')}-e${String(ele).padStart(6,'0')}-u.json`;
}
async function discoverCodes(){
  try{
    const r=await fetch(tsePath('/oficial/comum/config/ele-c.json'),{cache:'no-store'});if(!r.ok)return;
    const j=await r.json();
    for(const pl of j.pl||[]) if(pl.c==='ele2026') for(const e of pl.e||[]){
      const cs=new Set((e.abr||[]).flatMap(x=>(x.cp||[]).map(c=>String(c.cd))));
      const name=String(e.nm||'');
      const round=String(e.t||'')==='2'||/2º\s*turno|2o\s*turno|segundo turno/i.test(name)?2:1;
      if(cs.has('1')){
        if(round===2)S.codes.fed2=String(e.cd);else S.codes.fed=String(e.cd);
      }
      if(cs.has('3')){
        if(round===2)S.codes.est2=String(e.cd);else S.codes.est=String(e.cd);
      }
    }
    S.round2Ready=!!(S.codes.fed2||S.codes.est2);
  }catch{}
}
async function fetchResult(cargo,uf='BR',force=false,round=1){
  const key=`r${round}:${cargo}:${uf}`;const hit=S.cache.get(key);
  if(!force&&hit&&Date.now()-hit.at<18000)return hit.data;
  const ele=electionCode(cargo,round);
  if(!ele){if(hit)return hit.data;throw new Error(round===2?'2º turno ainda não publicado no TSE':'Código da eleição indisponível')}
  const r=await fetch(tsePath(resultPath(cargo,uf,round)),{cache:'no-store'});
  if(!r.ok){if(hit)return hit.data;throw new Error('TSE '+r.status)}
  const raw=await r.json();
  const data=adaptUnified(raw,{electionCode:ele,uf,cargoCode:cargo,photoBase:apiUrl('/api/tse?path=')});
  data.meta={...(data.meta||{}),round:Number(round)};
  S.cache.set(key,{at:Date.now(),data,raw});S.lastRefresh=Date.now();updateLive();
  return data;
}
async function batchMap(items,limit,fn){
  const out=[];for(let i=0;i<items.length;i+=limit)out.push(...await Promise.all(items.slice(i,i+limit).map(fn)));return out;
}
async function governorSummaryClient(force=false){
  const rows=await batchMap(UFS,4,async ([uf])=>{
    try{
      const r=await fetchResult('3',uf,force),official=r.candidatos.filter(c=>c.eleitoTse||c.situacaoOficial);
      return{uf,ok:true,pct:r.pctTotalizado,secoesTotal:r.secoesTotal,secoesTotalizadas:r.secoesTotalizadas,secoesNaoTotalizadas:r.secoesNaoTotalizadas,md:r.meta.md,tf:r.meta.tf,updated:r.totalizadoEm,
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
  const groups=new Map(),camOfficial=[],camProjected=[];let seatsTotal=0,camLoaded=0,camPct=0,camSectionsTotal=0,camSectionsDone=0;
  const senParty=new Map(),senUfs=[];let senLoaded=0,senPct=0,officialCount=0,senSectionsTotal=0,senSectionsDone=0;
  for(const x of pairs){
    if(x.cam){
      camLoaded++;camPct+=x.cam.pctTotalizado;seatsTotal+=x.cam.vagas;camSectionsTotal+=Number(x.cam.secoesTotal||0);camSectionsDone+=Number(x.cam.secoesTotalizadas||0);
      for(const g of x.cam.partidos){
        const key=g.sigla||g.nome,cur=groups.get(key)||{sigla:key,nome:g.nome||key,seats:0,votes:0};
        cur.seats+=Number(g.vagasOficiais||0);cur.votes+=Number(g.votosValidos||0);groups.set(key,cur);
      }
      camOfficial.push(...x.cam.candidatos.filter(officialCandidate).map(c=>({...c,uf:x.uf,cargoCodigo:'6'})));const pc=calcularProporcional(x.cam);camProjected.push(...(pc.eleitos||[]).map(e=>({...e.candidato,uf:x.uf,cargoCodigo:'6',projectionReason:e.motivo})));
    }
    if(x.sen){
      senLoaded++;senPct+=x.sen.pctTotalizado;senSectionsTotal+=Number(x.sen.secoesTotal||0);senSectionsDone+=Number(x.sen.secoesTotalizadas||0);
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
      sectionsTotal:camSectionsTotal,sectionsDone:camSectionsDone,pctSections:camSectionsTotal?camSectionsDone/camSectionsTotal*100:0,officialSeats:[...groups.values()].sort((a,b)=>b.seats-a.seats||b.votes-a.votes),officialElected:camOfficial,projectedElected:camProjected},
    sen:{kind:'senado',updatedAt:new Date().toISOString(),ufsLoaded:senLoaded,ufsTotal:27,pctAverage:senLoaded?senPct/senLoaded:0,
      seatsContested:54,sectionsTotal:senSectionsTotal,sectionsDone:senSectionsDone,pctSections:senSectionsTotal?senSectionsDone/senSectionsTotal*100:0,officialCount,byParty:[...senParty.values()].sort((a,b)=>b.seats-a.seats),ufs:senUfs}
  };
}

function cachedRaw(cargo,uf='BR',round=1){return S.cache.get(`r${round}:${cargo}:${uf}`)?.raw}
function sectionsSummary(r){
  const done=Number(r?.secoesTotalizadas||0),total=Number(r?.secoesTotal||0),remaining=Number(r?.secoesNaoTotalizadas||Math.max(0,total-done));
  return{done,total,remaining,pct:Number(r?.pctTotalizado||0),label:`${fmt(done)} de ${fmt(total)} seções/urnas totalizadas`};
}
function sectionsBadge(r,compact=false){
  const s=sectionsSummary(r);
  if(!s.total)return '<span class="apuration-count">Aguardando contagem de seções</span>';
  return `<div class="apuration-count ${compact?'compact':''}"><strong>${fmt(s.done)}</strong><span> de ${fmt(s.total)} seções/urnas</span><b>${pct(s.pct)}</b></div>`;
}
const LIVE_EVENTS_KEY='ap26-live-events-v1';
const LIVE_STATE_KEY='ap26-live-state-v1';
function readJsonLocal(key,fallback){try{const v=JSON.parse(localStorage.getItem(key)||'null');return v??fallback}catch{return fallback}}
function pushLiveEvent(type,text,meta={}){
  const events=readJsonLocal(LIVE_EVENTS_KEY,[]);
  const sig=type+'|'+text;
  if(events[0]?.sig===sig&&Date.now()-(events[0]?.at||0)<30000)return;
  events.unshift({id:String(Date.now())+'-'+Math.random().toString(36).slice(2,7),sig,type,text,at:Date.now(),meta});
  localStorage.setItem(LIVE_EVENTS_KEY,JSON.stringify(events.slice(0,80)));
}
function recordMajorEvents(pres,gov){
  const prev=readJsonLocal(LIVE_STATE_KEY,{});
  const next={};
  if(pres){
    const top=(pres.candidatos||[])[0];
    next.presLeader=top?.id||'';
    next.presLeaderName=top?.nome||'';
    next.presMd=pres.meta?.md||'n';
    if(prev.presLeader&&next.presLeader&&prev.presLeader!==next.presLeader)pushLiveEvent('lead',`Mudança na liderança presidencial: ${next.presLeaderName} assumiu a 1ª posição.`,{cargo:'1'});
    if(prev.presMd&&prev.presMd!=='e'&&next.presMd==='e')pushLiveEvent('official','Presidência matematicamente definida pelo TSE.',{cargo:'1'});
    if(prev.presMd&&prev.presMd!=='s'&&next.presMd==='s')pushLiveEvent('runoff','TSE definiu segundo turno para Presidente.',{cargo:'1'});
  }
  next.gov={};
  for(const x of gov?.states||[]){
    const s=governorVisualState(x),tone=s.elected?'elected':s.runoff?'runoff':'counting';
    next.gov[x.uf]={tone,leader:s.candidate?.id||s.candidate?.nome||'',name:s.candidate?.nome||''};
    const old=prev.gov?.[x.uf];
    if(old&&old.tone!==tone){
      if(tone==='elected')pushLiveEvent('official',`${x.uf}: ${s.candidate?.nome||'governador'} passou a ELEITO TSE.`,{uf:x.uf,cargo:'3'});
      if(tone==='runoff')pushLiveEvent('runoff',`${x.uf}: eleição para governador foi definida para 2º turno.`,{uf:x.uf,cargo:'3'});
    }else if(old&&tone==='counting'&&old.leader&&next.gov[x.uf].leader&&old.leader!==next.gov[x.uf].leader){
      pushLiveEvent('lead',`${x.uf}: ${s.candidate?.nome||'novo candidato'} assumiu a liderança para governador.`,{uf:x.uf,cargo:'3'});
    }
  }
  localStorage.setItem(LIVE_STATE_KEY,JSON.stringify(next));
}
function recordDeputyProjectionEvents(r,cargo,calc){
  if(!r||!calc||!['6','7','8'].includes(String(cargo)))return;
  const key=`ap26-proj-${cargo}-${r.abrangencia}`;
  const prev=readJsonLocal(key,{ids:[]});
  const nowIds=(calc.eleitos||[]).map(e=>String(e.candidato?.id||'')).filter(Boolean);
  const prevSet=new Set(prev.ids||[]),nowSet=new Set(nowIds);
  for(const e of calc.eleitos||[])if(!prevSet.has(String(e.candidato?.id||''))&&(prev.ids||[]).length){
    pushLiveEvent('projection',`${r.abrangencia}: ${e.candidato.nome} entrou nas vagas projetadas de ${CARGO[String(cargo)]}.`,{uf:r.abrangencia,cargo:String(cargo)});
  }
  for(const id of prev.ids||[])if(!nowSet.has(String(id))){
    const old=prev.items?.[id];if(old)pushLiveEvent('projection-out',`${r.abrangencia}: ${old.nome} saiu das vagas projetadas de ${CARGO[String(cargo)]}.`,{uf:r.abrangencia,cargo:String(cargo)});
  }
  const items=Object.fromEntries((calc.eleitos||[]).map(e=>[String(e.candidato.id),{nome:e.candidato.nome}]));
  localStorage.setItem(key,JSON.stringify({ids:nowIds,items,at:Date.now()}));
}
function liveEventsPanel(){
  const cutoff=Date.now()-5*60*1000;
  const events=readJsonLocal(LIVE_EVENTS_KEY,[]).filter(e=>(e.at||0)>=cutoff);
  const icon=t=>t==='official'?'✓':t==='runoff'?'↔':t==='lead'?'↑':t==='projection'?'＋':'−';
  return `<section class="section live-events-section"><div class="section-head"><div><div class="eyebrow">Últimos 5 minutos</div><div class="section-title">O que mudou</div></div><div class="section-note">${events.length?events.length+' mudança(s) detectada(s)':'sem mudanças relevantes'}</div></div>
    <div class="card live-events-card">${events.length?events.slice(0,10).map(e=>`<button class="live-event-row" data-event-uf="${esc(e.meta?.uf||'')}" data-event-cargo="${esc(e.meta?.cargo||'')}"><i class="live-event-icon ${esc(e.type)}">${icon(e.type)}</i><span><strong>${esc(e.text)}</strong><small>${new Date(e.at).toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'})}</small></span><b>›</b></button>`).join(''):'<div class="empty">Quando houver mudança de liderança, definição oficial ou entrada/saída de uma vaga projetada, ela aparecerá aqui.</div>'}</div>
  </section>`;
}
function wireLiveEvents(){
  $$('[data-event-uf]').forEach(b=>b.onclick=()=>{
    const uf=b.dataset.eventUf,cargo=b.dataset.eventCargo;
    if(uf){S.uf=uf;S.cargo=cargo||'3';showView('estados')}
    else if(cargo==='1')showView('presidente');
  });
}
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
  if((cargo==='1'||cargo==='3')&&r?.meta?.md==='s'&&index<2){
    return{label:'2º TURNO · TSE',cls:'official-badge',official:true};
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
function candidateCardState(c,r,cargo,index){
  const oi=officialInfo(c,r,cargo,index);
  const label=String(oi?.label||c.situacaoOficial||'').toLowerCase();
  const elected=!!oi?.official&&(/eleit/.test(label)||c.eleitoTse===true||String(c.e||'').toLowerCase()==='s')&&!/não|nao|suplente|2.?\s*turno|segundo turno/.test(label);
  const runoff=!!oi?.official&&/2.?\s*turno|segundo turno/.test(label);
  return{oi,elected,runoff};
}
function candidateRow(c,r,cargo,index,opts={}){
  const state=candidateCardState(c,r,cargo,index),oi=state.oi,fav=candidateForFavorite(c,r,cargo);
  const deputy=['6','7','8'].includes(String(cargo));
  const projected=deputy&&!!opts.projected&&!state.elected;
  const rowClass=state.elected?' candidate-official-elected':state.runoff?' candidate-official-runoff':projected?' candidate-projected-elected':'';
  const projectionBadge=projected?'<span class="projection-badge">Projetado eleito · cálculo atual</span>':'';
  return `<div class="candidate-row${rowClass}">
    <div class="rank">${index+1}º</div>${avatar(c)}
    <div><div class="cand-name">${esc(c.nome)}</div><div class="cand-meta">${esc(c.numero)} · ${esc(c.partido)} · ${fmt(c.votos)} votos</div>
      <div class="vote-bar"><span style="width:${clamp(c.pct)}%"></span></div>${oi?`<span class="${oi.cls}">${esc(oi.label)}</span>`:''}${projectionBadge}
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
  return cs.map((c,i)=>{
    const state=candidateCardState(c,r,cargo,i),oi=state.oi,fav=candidateForFavorite(c,r,cargo);
    const cls=state.elected?' leader-official-elected':state.runoff?' leader-official-runoff':'';
    return `<div class="leader-card${cls}">${avatar(c)}<div><div class="cand-name">${esc(c.nome)}</div><div class="cand-meta">${esc(c.numero)} · ${esc(c.partido)} · ${fmt(c.votos)} votos</div>${oi?`<span class="${oi.cls}">${esc(oi.label)}</span>`:''}</div><div class="leader-side">${favoriteButton(fav)}<div class="cand-pct">${pct(c.pct)}</div></div></div>`;
  }).join('')||'<div class="empty">Aguardando candidatos.</div>';
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
function secondRoundHomeCallout(pres,gov){
  if(pres?.meta?.md!=='s')return'';
  const cs=firstRoundRunoffCandidates(pres),count=round2GovernorStates(gov).length,cd=secondRoundCountdown();
  return `<section class="card round2-home-callout">
    <div class="round2-home-copy"><span class="eyebrow">2º turno · 25/10</span><h2>${cs.map(c=>esc(c.nome)).join(' × ')}</h2><p>${cd.label} · ${count} UF(s) com segundo turno para governador.</p></div>
    <div class="round2-home-actions"><button class="primary-btn" data-president-mode="round2" data-open-president>Ver 2º turno</button><button class="ghost-btn" data-president-mode="polls" data-open-president>Pesquisas</button></div>
  </section>`;
}
function wireSecondRoundHome(){
  $$('[data-open-president]').forEach(b=>b.onclick=()=>{S.presidentMode=b.dataset.presidentMode||'round2';showView('presidente')});
}
async function loadSecondRoundHome(host,force=false){
  const [r1,r2,gov]=await Promise.all([
    fetchResult('1','BR',force,1),
    fetchResult('1','BR',force,2),
    governorSummaryClient(force)
  ]);
  S.governors=gov;
  const cands=r2.candidatos.slice(0,2),diff=round2Difference(r2);
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Eleições Gerais 2026 · 2º turno</div><h1 class="page-title">Apuração em tempo real</h1><div class="page-sub">Dados oficiais do TSE referentes ao 2º turno.</div></div><div class="source-pill"><span class="live-dot"></span> Fonte oficial · TSE</div></div>
    <section class="card round2-live-home">
      <div class="section-head"><div><div class="eyebrow">Presidente · Brasil</div><div class="section-title">${r2.meta?.md==='e'?'Resultado definido pelo TSE':'2º turno em apuração'}</div></div><button class="card-action" data-president-mode="round2" data-open-president>Detalhes <span>→</span></button></div>
      ${sectionsBadge(r2)}
      <div class="round2-faceoff">${cands.map((c,i)=>secondRoundFaceoffCard(c,r1,r2,i)).join('')}</div>
      ${diff?`<div class="round2-difference"><span>Diferença agora</span><strong>${fmt(diff.votes)} votos</strong><small>${pct(diff.pctGap)} p.p. · liderança não é resultado oficial</small></div>`:''}
      ${electionAlert(r2,'1')}
    </section>
    <section class="section"><div class="section-head"><div><div class="eyebrow">Governadores</div><div class="section-title">2º turno por UF</div></div><div class="section-note">${round2GovernorStates(gov).length} disputa(s)</div></div>${round2GovernorCards(gov)}</section>
    ${liveEventsPanel()}
    <section class="section"><div class="info-grid"><div class="card info-card"><h3>Pesquisas</h3><p>Compare os levantamentos por instituto, data, amostra e margem de erro. O app não cria média própria.</p><button class="card-action" data-president-mode="polls" data-open-president>Ver pesquisas <span>→</span></button></div><div class="card info-card"><h3>Resultados do 1º turno</h3><p>Presidente, Senado, Câmara e Assembleias continuam disponíveis nas telas originais.</p><button class="card-action" data-president-mode="round1" data-open-president>1º turno <span>→</span></button></div></div></section>`;
  wireSecondRoundHome();wireRound2GovernorCards();wireLiveEvents();syncFavoriteButtons();wireFavorites(host);
}

async function loadAgora(force=false){
  const host=$('#agoraContent');
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Eleições Gerais 2026</div><h1 class="page-title">Apuração em tempo real</h1><div class="page-sub">Dados oficiais do TSE.</div></div><div class="source-pill"><span class="live-dot"></span> Fonte oficial · TSE</div></div>
    <section class="card round2-home-callout"><div class="round2-home-copy"><span class="eyebrow">2º turno · 25/10</span><h2>2º turno 2026</h2><p>Preparando confronto presidencial, governadores e pesquisas.</p></div><div class="round2-home-actions"><button class="primary-btn" data-president-mode="round2" data-open-president>Ver 2º turno</button><button class="ghost-btn" data-president-mode="polls" data-open-president>Pesquisas</button></div></section>
    <div class="card pad loading"><div class="empty">Atualizando resultado oficial do 1º turno…</div></div>`;
  wireSecondRoundHome();
  const pres=await fetchResult('1','BR',force);
  const gov=S.governors||{states:[]};
  recordPresident(pres);
  if(S.governors)recordMajorEvents(pres,gov);
  if(S.codes.fed2&&Date.now()>=ROUND2_ELECTION_DAY.getTime()){await loadSecondRoundHome(host,force);return}
  const official=officialSelected(pres,'1');
  const defined=pres.meta.md==='e'?'Eleito definido':pres.meta.md==='s'?'2º turno definido':pres.meta.tf==='s'?'Final':'Em apuração';
  const govDefined=(gov?.states||[]).filter(x=>x.md==='e'||x.md==='s'||x.tf==='s').length;
  const govLoaded=(gov?.states||[]).length>0;
  host.innerHTML=`
    <div class="page-head"><div><div class="eyebrow">Eleições Gerais 2026</div><h1 class="page-title">Apuração em tempo real</h1><div class="page-sub">Dados oficiais do TSE, com atualização automática a cada 30 segundos.</div></div><div class="source-pill"><span class="live-dot"></span> Fonte oficial · TSE</div></div>
    ${secondRoundHomeCallout(pres,gov)}
    <div class="hero-grid">
      <section class="card hero-card"><div class="section-head"><div><div class="eyebrow">Presidente · Brasil</div><div class="section-title">${esc(defined)}</div></div><button class="card-action" data-go="presidente">Detalhes <span>→</span></button></div>
        <div class="progress-row"><div class="progress"><span style="width:${clamp(pres.pctTotalizado)}%"></span></div><strong class="progress-pct">${pct(pres.pctTotalizado)}</strong></div>
        ${sectionsBadge(pres)}
        ${electionAlert(pres,'1')}<div class="leader-grid">${renderLeaderCards(pres,'1',2)}</div>
      </section>
      <aside class="metric-stack">
        <div class="card metric-card"><div class="metric-label">Situação presidencial</div><div class="metric-value" style="font-size:20px">${esc(official[0]?.situacaoOficial||official[0]?.nome||defined)}</div><div class="metric-foot">${official.length?official.length+' candidato(s) marcado(s) pelo TSE':'sem definição oficial ainda'}</div></div>
        <div class="card metric-card"><div class="metric-label">Governadores definidos</div><div class="metric-value">${govLoaded?govDefined:'…'}<span style="font-size:14px;color:var(--muted)"> / 27</span></div><div class="metric-foot">${govLoaded?'eleito, 2º turno ou totalização final':'carregando estados em segundo plano'}</div></div>
        <div class="card metric-card"><div class="metric-label">Próxima atualização</div><div class="metric-value" style="font-size:20px">30 segundos</div><div class="metric-foot">somente nas telas em uso</div></div>
      </aside>
    </div>
    <section class="section"><div class="section-head"><div><div class="eyebrow">Mapa rápido</div><div class="section-title">Governadores por UF</div></div><div class="section-note">${govLoaded?'toque no estado · abre resumo':'carregando estados…'}</div></div>${governorMapPanel(gov)}</section>
    ${liveEventsPanel()}
    <section class="section"><div class="info-grid"><div class="card info-card"><h3>Câmara dos Deputados</h3><p>513 cadeiras. O painel Congresso mostra a distribuição nacional por partido/federação usando <strong>TSE agora</strong> e as cadeiras já atribuídas em cada UF.</p><button class="card-action" data-go="congresso">Congresso <span>→</span></button></div><div class="card info-card"><h3>Senado Federal</h3><p>54 vagas em disputa em 2026, duas por UF. Antes da definição oficial mostramos os dois líderes; depois, somente o status de eleito informado pelo TSE.</p><button class="card-action" data-go="congresso">Senado <span>→</span></button></div></div></section>`;
  wireGo();wireSecondRoundHome();wireLiveEvents();syncFavoriteButtons();wireFavorites(host);mountGovernorBrazilMap(gov);

  if((!S.governors||force)&&S.view==='agora'){
    governorSummaryClient(force).then(fresh=>{
      S.governors=fresh;recordMajorEvents(pres,fresh);
      if(S.view==='agora')loadAgora(false);
    }).catch(()=>{});
  }
}
function governorVisualState(x){
  const officials=x?.official||[];
  const statusTexts=officials.map(c=>String(c.st||c.situacaoOficial||'').toLowerCase());
  const elected=String(x?.md||'').toLowerCase()==='e'||officials.some(c=>{
    const st=String(c.st||c.situacaoOficial||'').toLowerCase();
    return String(c.e||'').toLowerCase()==='s'||(st.includes('eleito')&&!st.includes('não eleito')&&!st.includes('2º turno')&&!st.includes('2o turno')&&!st.includes('segundo turno'));
  });
  const runoff=!elected&&(String(x?.md||'').toLowerCase()==='s'||statusTexts.some(st=>st.includes('2º turno')||st.includes('2o turno')||st.includes('segundo turno')));
  const winner=officials.find(c=>{
    const st=String(c.st||c.situacaoOficial||'').toLowerCase();
    return String(c.e||'').toLowerCase()==='s'||(st.includes('eleito')&&!st.includes('não eleito')&&!st.includes('turno'));
  });
  const candidate=winner||x?.leader||officials[0]||null;
  return{elected,runoff,candidate};
}

function governorMapStats(gov){
  const states=gov?.states||[];
  let elected=0,runoff=0,counting=0;
  for(const x of states){
    const s=governorVisualState(x);
    if(s.elected)elected++;
    else if(s.runoff)runoff++;
    else counting++;
  }
  return{elected,runoff,counting,total:states.length};
}
function governorMapPanel(gov){
  const stats=governorMapStats(gov);
  return `<div class="card governor-map-card">
    <div class="governor-map-counters">
      <div class="governor-map-counter elected"><span>Eleitos TSE</span><strong>${stats.elected}</strong></div>
      <div class="governor-map-counter runoff"><span>2º turno</span><strong>${stats.runoff}</strong></div>
      <div class="governor-map-counter counting"><span>Em apuração</span><strong>${stats.counting}</strong></div>
    </div>
    <div class="governor-map-wrap"><div id="governorBrazilMap" aria-label="Mapa interativo do Brasil"></div></div>
    <div class="governor-map-legend" aria-label="Legenda do mapa">
      <span><i class="map-legend-dot elected"></i><b>Eleito TSE</b><small>governador eleito oficialmente</small></span>
      <span><i class="map-legend-dot runoff"></i><b>2º turno TSE</b><small>disputa definida para o segundo turno</small></span>
      <span><i class="map-legend-dot counting"></i><b>Em apuração</b><small>ainda sem definição oficial</small></span>
    </div>
    <div id="governorMapFocus" class="governor-map-focus"><strong>Toque em um estado</strong><span>abre um resumo da UF com Governador, Senado e Deputados</span></div>
  </div>`;
}
function governorMapFocusText(x){
  if(!x)return '<strong>Toque em um estado</strong><span>abre um resumo da UF</span>';
  const state=governorVisualState(x);
  const status=state.elected?'Eleito TSE':state.runoff?'2º turno TSE':'Em apuração';
  const name=state.candidate?.nome||'Aguardando candidato';
  return `<strong>${esc(x.uf)} · ${esc(name)}</strong><span>${esc(status)} · ${fmt(x.secoesTotalizadas||0)} de ${fmt(x.secoesTotal||0)} seções · ${pct(x.pct||0)}</span>`;
}
function ensureStateQuickModal(){
  let modal=$('#stateQuickModal');if(modal)return modal;
  modal=document.createElement('div');modal.id='stateQuickModal';modal.className='state-quick-modal hidden';
  modal.innerHTML='<div class="state-quick-backdrop" data-close-state-quick></div><div class="state-quick-sheet"><button class="state-quick-close" data-close-state-quick aria-label="Fechar">×</button><div id="stateQuickBody"></div></div>';
  document.body.appendChild(modal);
  modal.querySelectorAll('[data-close-state-quick]').forEach(x=>x.onclick=()=>modal.classList.add('hidden'));
  return modal;
}
function stateQuickCandidate(c,label=''){
  if(!c)return '<div class="quick-empty">aguardando dados</div>';
  return `<div class="quick-candidate">${avatar(c)}<div><small>${esc(label)}</small><strong>${esc(c.nome)}</strong><span>${esc(c.numero||'')} · ${esc(c.partido||'')} · ${fmt(c.votos||0)} votos · ${pct(c.pct||0)}</span></div></div>`;
}
function openStateCargo(uf,cargo){
  const modal=$('#stateQuickModal');if(modal)modal.classList.add('hidden');
  S.uf=uf;S.cargo=cargo;showView('estados');
}
async function createStateShareImage(data){
  const canvas=document.createElement('canvas');canvas.width=1080;canvas.height=1350;const ctx=canvas.getContext('2d');
  ctx.fillStyle='#F7F5FB';ctx.fillRect(0,0,1080,1350);
  ctx.fillStyle='#7C3AED';ctx.fillRect(0,0,1080,150);
  ctx.fillStyle='#fff';ctx.font='900 52px system-ui';ctx.fillText('Apuração 2026',70,95);
  ctx.fillStyle='#17171D';ctx.font='900 82px system-ui';ctx.fillText(data.uf,70,270);
  ctx.font='700 30px system-ui';ctx.fillStyle='#6B7280';ctx.fillText(`${pct(data.pct)} das seções totalizadas`,70,320);
  const blocks=[
    ['GOVERNADOR',data.govText],
    ['SENADO',data.senText],
    ['DEP. FEDERAL',data.fedText],
    [data.uf==='DF'?'DEP. DISTRITAL':'DEP. ESTADUAL',data.estText]
  ];
  let y=390;
  for(const [title,body] of blocks){
    ctx.fillStyle='#fff';ctx.strokeStyle='#E5E7EB';ctx.lineWidth=2;ctx.beginPath();ctx.roundRect(55,y,970,190,26);ctx.fill();ctx.stroke();
    ctx.fillStyle='#7C3AED';ctx.font='900 24px system-ui';ctx.fillText(title,90,y+48);
    ctx.fillStyle='#17171D';ctx.font='800 31px system-ui';
    const words=String(body||'Aguardando dados').split(' ');let line='',ly=y+98;
    for(const w of words){const test=line+w+' ';if(ctx.measureText(test).width>860){ctx.fillText(line,90,ly);line=w+' ';ly+=42}else line=test}
    if(line)ctx.fillText(line,90,ly);y+=215;
  }
  ctx.fillStyle='#6B7280';ctx.font='600 22px system-ui';ctx.fillText('Fonte: TSE · projeções do app identificadas separadamente',70,1290);
  return await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
}
async function shareStateQuick(data){
  const blob=await createStateShareImage(data);if(!blob)return;
  const file=new File([blob],`apuracao-2026-${data.uf}.png`,{type:'image/png'});
  if(navigator.share&&navigator.canShare?.({files:[file]})){try{await navigator.share({title:`Apuração 2026 · ${data.uf}`,files:[file]});return}catch{}}
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=file.name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1500);
}
async function openStateQuickSummary(uf){
  uf=String(uf||'').toUpperCase();if(!uf)return;
  const modal=ensureStateQuickModal(),body=$('#stateQuickBody');modal.classList.remove('hidden');
  const gx=(S.governors?.states||[]).find(x=>x.uf===uf),gv=governorVisualState(gx);
  body.innerHTML=`<div class="quick-head"><div><span class="eyebrow">Resumo da UF</span><h2>${esc(UF_NAME[uf]||uf)} · ${uf}</h2><p>${fmt(gx?.secoesTotalizadas||0)} de ${fmt(gx?.secoesTotal||0)} seções · ${pct(gx?.pct||0)}</p></div></div>
    <div class="quick-loading">Carregando Senado e Deputados…</div>`;
  const [sen,fed,est]=await Promise.all([
    fetchResult('5',uf,false).catch(()=>null),
    fetchResult('6',uf,false).catch(()=>null),
    fetchResult(uf==='DF'?'8':'7',uf,false).catch(()=>null)
  ]);
  const senLeaders=sen?.candidatos?.slice(0,2)||[];
  const fedCalc=fed?calcularProporcional(fed):null,estCalc=est?calcularProporcional(est):null;
  const govStatus=gv.elected?'Eleito TSE':gv.runoff?'2º turno TSE':'Em apuração';
  const data={
    uf,pct:gx?.pct||0,
    govText:`${gv.candidate?.nome||'Aguardando'} · ${govStatus}`,
    senText:senLeaders.length?senLeaders.map((c,i)=>`${i+1}º ${c.nome} (${fmt(c.votos)} votos)`).join(' · '):'Aguardando dados',
    fedText:fedCalc?.eleitos?.length?`${fedCalc.eleitos.length} projetado(s) · linha de corte ${fedCalc.linhaDeCorte?.ultimoEleito?.candidato?.nome||'—'}`:'Aguardando projeção',
    estText:estCalc?.eleitos?.length?`${estCalc.eleitos.length} projetado(s) · linha de corte ${estCalc.linhaDeCorte?.ultimoEleito?.candidato?.nome||'—'}`:'Aguardando projeção'
  };
  modal._shareData=data;
  body.innerHTML=`<div class="quick-head"><div><span class="eyebrow">Resumo da UF</span><h2>${esc(UF_NAME[uf]||uf)} · ${uf}</h2><p>${fmt(gx?.secoesTotalizadas||0)} de ${fmt(gx?.secoesTotal||0)} seções · ${pct(gx?.pct||0)}</p></div><span class="quick-status ${gv.elected?'elected':gv.runoff?'runoff':'counting'}">${esc(govStatus)}</span></div>
    <div class="quick-grid">
      <section class="quick-block"><div class="quick-block-title">Governador</div>${stateQuickCandidate(gv.candidate,govStatus)}<button data-open-cargo="3">Abrir Governador →</button></section>
      <section class="quick-block"><div class="quick-block-title">Senado</div>${senLeaders.map((c,i)=>stateQuickCandidate(c,(c.eleitoTse||/Eleito/i.test(c.situacaoOficial||''))?'Eleito TSE':`${i+1}º agora`)).join('')||'<div class="quick-empty">aguardando</div>'}<button data-open-cargo="5">Abrir Senado →</button></section>
      <section class="quick-block"><div class="quick-block-title">Deputado Federal</div><div class="quick-cut">${fedCalc?.linhaDeCorte?.ultimoEleito?`Última vaga projetada: <strong>${esc(fedCalc.linhaDeCorte.ultimoEleito.candidato.nome)}</strong> · ${fmt(fedCalc.linhaDeCorte.ultimoEleito.candidato.votos)} votos`:'Aguardando linha de corte'}</div><button data-open-cargo="6">Abrir Federal →</button></section>
      <section class="quick-block"><div class="quick-block-title">${uf==='DF'?'Deputado Distrital':'Deputado Estadual'}</div><div class="quick-cut">${estCalc?.linhaDeCorte?.ultimoEleito?`Última vaga projetada: <strong>${esc(estCalc.linhaDeCorte.ultimoEleito.candidato.nome)}</strong> · ${fmt(estCalc.linhaDeCorte.ultimoEleito.candidato.votos)} votos`:'Aguardando linha de corte'}</div><button data-open-cargo="${uf==='DF'?'8':'7'}">Abrir ${uf==='DF'?'Distrital':'Estadual'} →</button></section>
    </div>
    <button id="shareStateQuick" class="primary-btn quick-share">Compartilhar resumo da UF</button>`;
  body.querySelectorAll('[data-open-cargo]').forEach(b=>b.onclick=()=>openStateCargo(uf,b.dataset.openCargo));
  $('#shareStateQuick').onclick=()=>shareStateQuick(data);
}
function mountGovernorBrazilMap(gov){
  const host=$('#governorBrazilMap');
  if(!host)return;
  const byUf=new Map((gov?.states||[]).map(x=>[String(x.uf||'').toUpperCase(),x]));
  const focus=$('#governorMapFocus');
  const openSenate=uf=>openStateQuickSummary(uf);
  const updateFocus=uf=>{
    const x=byUf.get(String(uf||'').toUpperCase());
    if(focus)focus.innerHTML=governorMapFocusText(x);
  };

  if(typeof BrMap==='undefined'){
    host.innerHTML=`<div class="uf-grid governor-map-fallback">${renderGovernorGrid(gov)}</div>`;
    host.querySelectorAll('[data-uf]').forEach(el=>el.onclick=()=>openSenate(el.dataset.uf));
    return;
  }

  BrMap.Draw({
    wrapper:'#governorBrazilMap',
    cssFill:{shape:'#D7DAE1',icon_state:'#D7DAE1',label_icon_state:'#242631',label_state:'#FFFFFF',selected:'#C7CBD5'},
    callbacks:{
      click:(element,uf)=>openSenate(uf),
      mouseover:(element,uf)=>updateFocus(uf)
    }
  });

  const injected=[...document.head.querySelectorAll('style')].filter(s=>String(s.textContent||'').includes('.state .shape { fill:'));
  injected.slice(0,-1).forEach(s=>s.remove());

  for(const [uf] of UFS){
    const id=uf.toLowerCase(),x=byUf.get(uf),state=governorVisualState(x);
    const tone=state.elected?'elected':state.runoff?'runoff':'counting';
    const fill=state.elected?'#22C55E':state.runoff?'#F59E0B':'#D1D5DB';
    const darkFill=state.elected?'#16A34A':state.runoff?'#D97706':'#525866';
    const shape=document.querySelector(id==='df'?`#icon_${id}`:`#shape_${id}`);
    const label=document.querySelector(`#label_icon_state_${id}`);
    const link=document.querySelector(`#state_${id}`);
    if(shape){
      shape.style.fill=document.documentElement.dataset.theme==='dark'?darkFill:fill;
      shape.style.stroke='var(--surface)';
      shape.style.strokeWidth='1.2px';
    }
    if(label){
      label.style.fill=state.elected||state.runoff?'#111827':'#374151';
      label.style.fontWeight='900';
      label.style.pointerEvents='none';
    }
    if(link){
      link.classList.add('map-state-'+tone);
      link.setAttribute('tabindex','0');
      link.setAttribute('role','button');
      link.setAttribute('aria-label',governorMapFocusText(x).replace(/<[^>]+>/g,' '));
      link.addEventListener('focus',()=>updateFocus(uf));
      link.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openSenate(uf)}});
    }
  }
}

function renderGovernorGrid(gov){
  if(!gov?.states)return UFS.map(([uf])=>`<button class="uf-card" data-uf="${uf}"><strong>${uf}</strong><span class="gov-name">Carregando…</span></button>`).join('');
  return gov.states.map(x=>{
    const state=governorVisualState(x);
    const cls=state.elected?'gov-elected':state.runoff?'gov-runoff':'gov-counting';
    const status=state.elected?'Eleito TSE':state.runoff?'2º turno TSE':'';
    const name=state.candidate?.nome||((x.pct||0)>0?'Apurando':'Aguardando');
    return `<button class="uf-card ${cls}" data-uf="${x.uf}">
      <strong>${x.uf}</strong>
      <span class="gov-name">${esc(name)}</span>
      ${status?`<span class="gov-status-pill">${esc(status)}</span>`:''}
      <span class="gov-sections">${fmt(x.secoesTotalizadas||0)} / ${fmt(x.secoesTotal||0)} seções</span>
      <span class="gov-pct">${pct(x.pct||0)}</span>
    </button>`;
  }).join('');
}
function presidentApurationPanel(r){
  const total=Number(r.secoesTotal||0),done=Number(r.secoesTotalizadas||0),remaining=Math.max(0,total-done);
  return `<div class="pres-apuration-card">
    <div class="pres-apuration-top">
      <div><span class="pres-apuration-label">Apuração nacional</span><strong class="pres-apuration-pct">${pct(r.pctTotalizado)}</strong></div>
      <div class="pres-apuration-count"><strong>${fmt(done)} <span>de ${fmt(total)}</span></strong><small>seções/urnas totalizadas</small></div>
    </div>
    <div class="pres-apuration-track" aria-label="${pct(r.pctTotalizado)} das seções totalizadas"><span style="width:${clamp(r.pctTotalizado)}%"></span></div>
    <div class="pres-apuration-foot">
      <span><b>${fmt(remaining)}</b> seções restantes</span>
      <span>Atualizado ${esc(r.totalizadoEm||'aguardando')}</span>
    </div>
  </div>`;
}

const ROUND2_VOTING_START=new Date('2026-10-25T08:00:00-03:00');
const ROUND2_APURATION_START=new Date('2026-10-25T17:00:00-03:00');
function presidentModeTabs(active){
  return `<div class="president-mode-tabs">
    <button class="seg ${active==='round1'?'active':''}" data-president-mode="round1">1º turno</button>
    <button class="seg ${active==='round2'?'active':''}" data-president-mode="round2">2º turno</button>
    <button class="seg ${active==='polls'?'active':''}" data-president-mode="polls">Pesquisas</button>
  </div>`;
}
function wirePresidentModeTabs(){
  $$('[data-president-mode]').forEach(b=>b.onclick=()=>{
    S.presidentMode=b.dataset.presidentMode;
    showView('presidente');
  });
}
function secondRoundStage(){
  const now=Date.now();
  if(now<ROUND2_VOTING_START.getTime()){
    const diff=ROUND2_VOTING_START.getTime()-now,days=Math.floor(diff/86400000),hours=Math.floor((diff%86400000)/3600000);
    return{phase:'countdown',label:`${days} dia(s) e ${hours}h para a votação`,short:'25 OUT'};
  }
  if(now<ROUND2_APURATION_START.getTime()){
    const diff=ROUND2_APURATION_START.getTime()-now,hours=Math.floor(diff/3600000),mins=Math.floor((diff%3600000)/60000);
    return{phase:'voting',label:`Votação em andamento · apuração em ${hours}h ${mins}min`,short:'VOTANDO'};
  }
  return{phase:'counting',label:S.codes.fed2?'Apuração do 2º turno disponível':'Aguardando publicação da apuração pelo TSE',short:'APURAÇÃO'};
}
function secondRoundCountdown(){return secondRoundStage()}
function firstRoundRunoffCandidates(r){
  if(!r?.candidatos?.length)return[];
  return r.candidatos.slice(0,2);
}
async function loadPollData(force=false){
  if(S.pollData&&!force)return S.pollData;
  const r=await fetch(`./polls-2026.json?v=${force?Date.now():'1'}`,{cache:force?'no-store':'default'});
  if(!r.ok)throw new Error('Não foi possível carregar pesquisas');
  S.pollData=await r.json();
  return S.pollData;
}
function pollValue(v){
  return Number(v||0).toLocaleString('pt-BR',{minimumFractionDigits:Number(v)%1?1:0,maximumFractionDigits:1})+'%';
}
function presidentialIdentity(candidateOrName,party=''){
  const obj=typeof candidateOrName==='object'&&candidateOrName?candidateOrName:null;
  const name=String(obj?.nome||obj?.name||candidateOrName||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toUpperCase();
  const sigla=String(obj?.partido||obj?.party||party||'').toUpperCase();
  if(name.includes('LULA')||sigla==='PT')return{key:'lula',color:'#E30613',soft:'#FDE8EA',label:'Lula'};
  if(name.includes('FLAVIO')||name.includes('FLÁVIO'))return{key:'flavio',color:'#1565C0',soft:'#E8F1FB',label:'Flávio'};
  return{key:'other',color:'#7C3AED',soft:'#F1EBFD',label:String(obj?.nome||obj?.name||candidateOrName||'')};
}
function pollCard(p){
  const cs=(p.candidates||[]).slice(0,2);
  return `<article class="poll-card">
    <div class="poll-card-head"><div><span class="eyebrow">${esc(p.institute)}</span><strong>${new Date(p.published+'T12:00:00').toLocaleDateString('pt-BR')}</strong></div><span class="poll-phase">${esc(p.phase||'')}</span></div>
    <div class="poll-bars">${cs.map(c=>{const id=presidentialIdentity(c.name,c.party);return `<div class="poll-row poll-candidate-${id.key}" style="--candidate-color:${id.color};--candidate-soft:${id.soft}"><div class="poll-row-head"><span><i class="candidate-color-dot"></i>${esc(c.name)} <small>${esc(c.party)}</small></span><strong>${pollValue(c.value)}</strong></div><div class="poll-track"><span style="width:${clamp(c.value)}%;background:var(--candidate-color)"></span></div></div>`}).join('')}</div>
    <div class="poll-other">${p.blankNull!==null&&p.blankNull!==undefined?`<span>Branco/nulo <b>${pollValue(p.blankNull)}</b></span>`:''}${p.undecided!==null&&p.undecided!==undefined?`<span>Indecisos <b>${pollValue(p.undecided)}</b></span>`:''}</div>
    <div class="poll-meta">
      <span>Campo: ${new Date(p.fieldStart+'T12:00:00').toLocaleDateString('pt-BR')}–${new Date(p.fieldEnd+'T12:00:00').toLocaleDateString('pt-BR')}</span>
      <span>${fmt(p.sample)} entrevistas</span><span>Margem ±${String(p.margin).replace('.',',')} p.p.</span>
      <span>${esc(p.basis)}</span>${p.registration?`<span>TSE ${esc(p.registration)}</span>`:''}
    </div>
    <a class="poll-source-link" href="${esc(p.source)}" target="_blank" rel="noopener noreferrer">Abrir fonte ↗</a>
  </article>`;
}
function pollScopeTabs(data){
  const scopes=[...new Set((data?.polls||[]).map(p=>String(p.scope||'BR').toUpperCase()))];
  if(!scopes.includes(S.pollScope))S.pollScope=scopes[0]||'BR';
  if(scopes.length<=1)return'';
  return `<div class="poll-scope-tabs">${scopes.map(scope=>`<button class="seg ${S.pollScope===scope?'active':''}" data-poll-scope="${esc(scope)}">${scope==='BR'?'Brasil':esc(UF_NAME[scope]||scope)}</button>`).join('')}</div>`;
}
function wirePollScope(){
  $$('[data-poll-scope]').forEach(b=>b.onclick=()=>{S.pollScope=b.dataset.pollScope||'BR';S.presidentMode='polls';loadPresident(false)});
}
function stateGovernorPolls(data,uf){
  const rows=(data?.polls||[]).filter(p=>String(p.scope).toUpperCase()===String(uf).toUpperCase()&&p.race==='governador').sort((a,b)=>String(b.published).localeCompare(String(a.published)));
  if(!rows.length)return'';
  return `<section class="quick-polls"><div class="quick-block-title">Pesquisas · Governador</div><div class="poll-grid">${rows.slice(0,3).map(pollCard).join('')}</div></section>`;
}
function pollsPanel(data,{limit=0,scope=S.pollScope}={}){
  const polls=(data?.polls||[]).filter(p=>p.scope===scope&&p.race==='presidente').sort((a,b)=>String(b.published).localeCompare(String(a.published)));
  const shown=limit?polls.slice(0,limit):polls;
  const scopeName=scope==='MG'?'Minas Gerais':'Brasil';
  return `<div class="polls-head-note"><strong>${esc(scopeName)}</strong> · pesquisas são retratos do momento, não previsão de resultado. O app <strong>não calcula média própria</strong> entre institutos nem mistura votos totais com votos válidos.</div>
    <div class="poll-grid">${shown.map(pollCard).join('')||'<div class="empty">Nenhuma pesquisa cadastrada neste recorte.</div>'}</div>`;
}
async function renderPollsPresident(host,r1,force=false){
  const data=await loadPollData(force);
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">2º turno 2026</div><h1 class="page-title">Pesquisas eleitorais</h1><div class="page-sub">Levantamentos de diferentes institutos, exibidos individualmente e com ficha técnica.</div></div><div class="source-pill">${(data.polls||[]).length} pesquisas cadastradas</div></div>
    ${presidentModeTabs('polls')}
    ${pollScopeTabs(data)}
    <div class="card poll-context-card"><strong>Contexto</strong><span>${esc(data.note||'')}</span></div>
    ${pollsPanel(data)}`;
  wirePresidentModeTabs();wirePollScope();
}
function secondRoundFaceoffCard(c,r1,r2,index){
  const old=r1?.candidatos?.find(x=>String(x.numero)===String(c.numero));
  const state=r2?candidateCardState(c,r2,'1',index):{elected:false,runoff:true,oi:null};
  const id=presidentialIdentity(c);
  const cls=state.elected?' official-card-green':'';
  return `<article class="round2-candidate round2-candidate-${id.key}${cls}" style="--candidate-color:${id.color};--candidate-soft:${id.soft}">
    ${avatar(c,'large')}
    <div class="round2-candidate-main"><span class="result-context"><i class="candidate-color-dot"></i>${esc(c.numero)} · ${esc(c.partido)}</span><h3>${esc(c.nome)}</h3>
      <div class="round2-votes">${r2?`<strong>${fmt(c.votos)}</strong> votos · <b>${pct(c.pct)}</b>`:`<strong>${fmt(old?.votos||c.votos)}</strong> votos no 1º turno · <b>${pct(old?.pct||c.pct)}</b>`}</div>
      ${old&&r2?`<small>1º turno: ${fmt(old.votos)} votos · ${pct(old.pct)}</small>`:''}
      ${state.oi?`<span class="${state.oi.cls}">${esc(state.oi.label)}</span>`:'<span class="leader-badge">CLASSIFICADO AO 2º TURNO · TSE</span>'}
    </div>
    <div class="round2-star">${favoriteButton(candidateForFavorite(c,r2||r1,'1'))}</div>
  </article>`;
}
function round2Difference(r){
  if(!r?.candidatos?.length||r.candidatos.length<2)return null;
  const a=r.candidatos[0],b=r.candidatos[1];
  return{votes:Math.abs(Number(a.votos||0)-Number(b.votos||0)),leader:a,pctGap:Math.abs(Number(a.pct||0)-Number(b.pct||0))};
}
function round2GovernorStates(gov){
  return (gov?.states||[]).filter(x=>String(x.md||'').toLowerCase()==='s'||governorVisualState(x).runoff);
}
function round2GovernorCards(gov){
  const rows=round2GovernorStates(gov);
  if(!rows.length)return '<div class="empty">Nenhum estado identificado para 2º turno neste momento.</div>';
  return `<div class="round2-state-grid">${rows.map(x=>`<button class="round2-state-card" data-round2-uf="${esc(x.uf)}"><strong>${esc(x.uf)}</strong><span>2º turno TSE</span><small>${fmt(x.secoesTotalizadas||0)} / ${fmt(x.secoesTotal||0)} seções no 1º turno</small><b>Abrir confronto →</b></button>`).join('')}</div>`;
}
async function openRound2Governor(uf){
  const modal=ensureStateQuickModal(),body=$('#stateQuickBody');modal.classList.remove('hidden');
  body.innerHTML=`<div class="quick-head"><div><span class="eyebrow">2º turno · Governador</span><h2>${esc(UF_NAME[uf]||uf)} · ${esc(uf)}</h2><p>Carregando confronto…</p></div></div>`;
  let r2=null,r1=null;
  try{r1=await fetchResult('3',uf,false,1)}catch{}
  if(S.codes.est2){try{r2=await fetchResult('3',uf,true,2)}catch{}}
  const base=r2||r1,cands=r2?.candidatos?.slice(0,2)||r1?.candidatos?.slice(0,2)||[];const pollData=await loadPollData(false).catch(()=>null);
  const diff=r2?round2Difference(r2):null;
  body.innerHTML=`<div class="quick-head"><div><span class="eyebrow">2º turno · Governador</span><h2>${esc(UF_NAME[uf]||uf)} · ${esc(uf)}</h2><p>${r2?`${fmt(r2.secoesTotalizadas)} de ${fmt(r2.secoesTotal)} seções · ${pct(r2.pctTotalizado)}`:'TSE ainda não publicou a apuração do 2º turno'}</p></div></div>
    <div class="round2-modal-candidates">${cands.map((c,i)=>candidateRow(c,base,'3',i)).join('')}</div>
    ${diff?`<div class="round2-difference"><span>Diferença agora</span><strong>${fmt(diff.votes)} votos</strong><small>${pct(diff.pctGap)} p.p. entre os dois</small></div>`:''}${pollData?stateGovernorPolls(pollData,uf):''}`;
  syncFavoriteButtons();wireFavorites(body);
}
function wireRound2GovernorCards(){
  $$('[data-round2-uf]').forEach(b=>b.onclick=()=>openRound2Governor(b.dataset.round2Uf));
}
async function renderSecondRoundPresident(host,r1,force=false){
  const gov=S.governors||{states:[]};
  let r2=null;
  if(S.codes.fed2){try{r2=await fetchResult('1','BR',force,2)}catch{}}
  const candidates=r2?.candidatos?.slice(0,2)||firstRoundRunoffCandidates(r1);
  const countdown=secondRoundStage(),diff=r2?round2Difference(r2):null;
  const pollData=await loadPollData(false).catch(()=>null);
  const govLoaded=(gov?.states||[]).length>0;
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Brasil · 2º turno</div><h1 class="page-title">Presidente da República</h1><div class="page-sub">${r2?'Apuração oficial do 2º turno em tempo real.':'Confronto definido pelo TSE · votação em 25/10/2026.'}</div></div><div class="round2-countdown"><span>${r2?'Apuração do 2º turno':countdown.label}</span><strong>${r2?pct(r2.pctTotalizado):countdown.short}</strong></div></div>
    ${presidentModeTabs('round2')}
    <section class="card round2-hero">
      <div class="section-head"><div><div class="eyebrow">${r2?'TSE · 2º turno':'Confronto presidencial'}</div><div class="section-title">${r2?'Apuração ao vivo':'Classificados pelo TSE'}</div></div><div class="section-note">${S.codes.fed2?'código TSE do 2º turno detectado':'aguardando código TSE do 2º turno'}</div></div>
      ${r2?sectionsBadge(r2):'<div class="round2-prep-note">O app continuará consultando a configuração oficial do TSE. Assim que o pleito de 2º turno aparecer, passa a usar o novo arquivo sem perder o histórico do 1º turno.</div>'}
      <div class="round2-faceoff">${candidates.map((c,i)=>secondRoundFaceoffCard(c,r1,r2,i)).join('')}</div>
      ${diff?(()=>{const id=presidentialIdentity(diff.leader);return `<div class="round2-difference" style="--candidate-color:${id.color}"><span>Diferença agora</span><strong><i class="candidate-color-dot"></i>${fmt(diff.votes)} votos</strong><small>${esc(diff.leader.nome)} à frente · ${pct(diff.pctGap)} p.p. · liderança não significa resultado oficial</small></div>`})():''}
      ${r2?electionAlert(r2,'1'):''}
    </section>
    <section class="section"><div class="section-head"><div><div class="eyebrow">Governadores</div><div class="section-title">Estados com 2º turno</div></div><div class="section-note">${govLoaded?round2GovernorStates(gov).length+' UF(s)':'carregando estados…'}</div></div>${govLoaded?round2GovernorCards(gov):'<div class="card empty">Carregando confrontos estaduais em segundo plano…</div>'}</section>
    <section class="section"><div class="section-head"><div><div class="eyebrow">Pesquisas</div><div class="section-title">Levantamentos recentes</div></div><button class="card-action" data-president-mode="polls">Ver todas <span>→</span></button></div>${pollData?pollsPanel(pollData,{limit:3,scope:'BR'}):'<div class="card empty">Pesquisas indisponíveis agora.</div>'}</section>`;
  wirePresidentModeTabs();wireRound2GovernorCards();syncFavoriteButtons();wireFavorites(host);

  if((!S.governors||force)&&S.view==='presidente'&&S.presidentMode==='round2'){
    governorSummaryClient(force).then(fresh=>{
      S.governors=fresh;
      if(S.view==='presidente'&&S.presidentMode==='round2')renderSecondRoundPresident(host,r1,false);
    }).catch(()=>{});
  }
}
async function loadPresident(force=false){
  const host=$('#presidentContent');
  let active=S.presidentMode;

  if(active==='polls'){
    host.innerHTML='<div class="page-head"><div><div class="eyebrow">2º turno 2026</div><h1 class="page-title">Pesquisas eleitorais</h1><div class="page-sub">Carregando levantamentos verificados…</div></div></div>';
    await renderPollsPresident(host,null,force);
    return;
  }

  if(active==='round2'){
    host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Brasil · 2º turno</div><h1 class="page-title">Presidente da República</h1><div class="page-sub">Confronto definido pelo TSE · votação em 25/10/2026.</div></div></div>
      ${presidentModeTabs('round2')}
      <section class="card round2-hero"><div class="section-head"><div><div class="eyebrow">Confronto presidencial</div><div class="section-title">Classificados pelo TSE</div></div></div><div class="empty">Carregando os dados do 1º turno…</div></section>`;
    wirePresidentModeTabs();
  }else{
    host.innerHTML='<div class="card pad loading"><div class="empty">Carregando Presidente…</div></div>';
  }

  const r=await fetchResult('1','BR',force,1);recordPresident(r);
  if(active==='auto')active=r.meta?.md==='s'?'round2':'round1';
  if(active==='round2'){await renderSecondRoundPresident(host,r,force);return}
  const official=officialSelected(r,'1');
  host.innerHTML=`
  <div class="page-head president-head"><div><div class="eyebrow">Brasil · 1º turno</div><h1 class="page-title">Presidente da República</h1><div class="page-sub">Resultado do 1º turno preservado para consulta.</div></div>${presidentApurationPanel(r)}</div>
  ${presidentModeTabs('round1')}
  ${electionAlert(r,'1')}
  <div class="pres-grid section">
    <section class="card pad"><div class="section-head"><div><div class="eyebrow">Placar oficial</div><div class="section-title">Candidatos</div></div><div class="section-note">${r.candidatos.length} candidaturas</div></div><div class="candidate-list">${orderedCandidates(r).map((c,i)=>candidateRow(c,r,'1',i)).join('')}</div></section>
    <aside class="stack">
      <div class="card pad"><div class="section-head"><div><div class="eyebrow">Situação TSE</div><div class="section-title">${r.meta.md==='e'?'Eleição definida':r.meta.md==='s'?'Segundo turno definido':r.meta.tf==='s'?'Totalização final':'Acompanhamento'}</div></div></div><div class="status-board">${official.length?official.map(c=>`<span class="status-chip official">${esc(c.nome)} · ${esc(officialInfo(c,r,'1',0)?.label||'TSE')}</span>`).join(''):'<span class="status-chip">Nenhum eleito/2º turno oficial ainda</span>'}</div></div>
      <div class="card pad"><div class="eyebrow">Votos</div><div class="section-title">Composição</div>${donut(r)}<div class="stats-grid"><div class="stat-box"><span>Eleitorado</span><strong>${fmt(r.eleitorado)}</strong></div><div class="stat-box"><span>Comparecimento</span><strong>${fmt(r.comparecimento)}</strong></div><div class="stat-box"><span>Abstenção</span><strong>${fmt(r.abstencao)}</strong></div><div class="stat-box"><span>Válidos</span><strong>${fmt(r.validos)}</strong></div></div></div>
      <div class="card pad"><div class="eyebrow">Evolução local</div><div class="section-title">Percentuais ao longo das atualizações</div><div style="margin-top:9px">${evolution()}</div></div>
    </aside>
  </div>`;
  wirePresidentModeTabs();syncFavoriteButtons();wireFavorites(host);
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
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">${esc(UF_NAME[S.uf])}</div><h1 class="page-title">${esc(CARGO[cargo])}</h1><div class="page-sub">${S.uf} · ${fmt(r.secoesTotalizadas)} de ${fmt(r.secoesTotal)} seções/urnas totalizadas · ${pct(r.pctTotalizado)}</div></div><div class="source-pill">TSE · ${esc(r.meta.dataGeracao||'')} ${esc(r.meta.horaGeracao||'')}</div></div>${buildStateToolbar()}<div class="state-apuration-strip">${sectionsBadge(r)}</div>${cargo==='3'||cargo==='5'?renderMajorState(r,cargo):renderProportional(r,cargo)}`;
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
  return `<div class="seat-bar">${rows.map(x=>`<span title="${esc(x.sigla)} · ${x.seats}" style="width:${x.seats/total*100}%;background:${politicalFill(x.sigla)}"></span>`).join('')}</div><div class="seat-legend">${rows.slice(0,10).map(x=>`<span><i class="legend-dot" style="display:inline-block;background:${politicalFill(x.sigla)}"></i> ${esc(x.sigla)} ${x.seats}</span>`).join('')}</div>`;
}
function renderProportionalCandidateRanking(r,cargo,calc){
  const list=orderedCandidates(r);
  const projectedIds=new Set((calc?.eleitos||[]).map(e=>String(e.candidato?.id||'')));
  const isProjected=c=>projectedIds.has(String(c.id||''));
  const first=list.slice(0,80),rest=list.slice(80);
  const rows=first.map((c,i)=>candidateRow(c,r,cargo,i,{projected:isProjected(c)})).join('');
  const extra=rest.length?`<div class="candidate-list prop-candidate-more hidden">${rest.map((c,i)=>candidateRow(c,r,cargo,i+80,{projected:isProjected(c)})).join('')}</div>
    <button class="modern-link-btn prop-show-all" data-show-prop-all type="button">Mostrar todos os ${fmt(list.length)} candidatos <span>↓</span></button>`:'';
  return `<section class="card pad section prop-candidates-card">
    <div class="section-head"><div><div class="eyebrow">Votação nominal</div><div class="section-title">Candidatos e votos</div></div><div class="section-note">${fmt(list.length)} candidaturas · ordem atual do TSE</div></div>
    <div class="projection-legend">
      <span class="projection-legend-item official"><i></i><b>Eleito TSE</b><small>situação oficial</small></span>
      <span class="projection-legend-item projected"><i></i><b>Projetado eleito</b><small>cálculo atual do app</small></span>
      <span class="projection-legend-item neutral"><i></i><b>Demais candidatos</b><small>fora das vagas neste momento</small></span>
    </div>
    <div class="prop-candidate-note">Cada linha mostra <strong>votos nominais</strong>, percentual, partido e situação oficial. O verde claro é uma <strong>projeção dinâmica</strong> e pode mudar a cada atualização.</div>
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

function renderDeputyCutLine(calc,r,cargo){
  const last=calc?.linhaDeCorte?.ultimoEleito,first=calc?.linhaDeCorte?.primeirosDeFora?.[0];
  if(!last||!first)return `<section class="card cutline-card"><div class="section-head"><div><div class="eyebrow">Linha de corte</div><div class="section-title">Última vaga projetada</div></div></div><div class="empty">A linha de corte aparecerá quando o cálculo conseguir atribuir as vagas sem empate indefinido.</div></section>`;
  const groupOut=r.partidos.find(g=>String(g.id)===String(first.grupoId));
  const reason=last.motivo==='QP'?'eleito por QP':'vaga por média/sobra';
  const diff=calc.linhaDeCorte.diferencaVotos;
  return `<section class="card cutline-card">
    <div class="section-head"><div><div class="eyebrow">Linha de corte · ${esc(CARGO[String(cargo)])}</div><div class="section-title">Quem está dentro e quem está fora agora</div></div><div class="section-note">projeção do app · não oficial</div></div>
    <div class="cutline-grid">
      <div class="cutline-person in"><span class="cutline-kicker">Última vaga projetada</span>${avatar(last.candidato)}<div><strong>${esc(last.candidato.nome)}</strong><span>${esc(last.grupoSigla||last.candidato.partido)} · ${fmt(last.candidato.votos)} votos</span><b>${esc(reason)}</b></div></div>
      <div class="cutline-gap"><span>Diferença nominal</span><strong>${fmt(diff||0)}</strong><small>votos entre os dois candidatos</small></div>
      <div class="cutline-person out"><span class="cutline-kicker">Primeiro fora</span>${avatar(first)}<div><strong>${esc(first.nome)}</strong><span>${esc(groupOut?.sigla||first.partido)} · ${fmt(first.votos)} votos</span><b>fora das vagas neste momento</b></div></div>
    </div>
    <div class="cutline-note">A linha de corte é uma leitura do cálculo proporcional atual. QP, sobras, médias e votos dos grupos podem alterar quem ocupa a última vaga mesmo sem uma ultrapassagem simples em votos nominais.</div>
  </section>`;
}

function renderProportional(r,cargo){
  const calc=calcularProporcional(r);recordDeputyProjectionEvents(r,cargo,calc);const calcBy=new Map(calc.partidos.map(x=>[x.id,x])),officialElected=r.candidatos.filter(c=>c.eleitoTse||(/Eleito/i.test(c.situacaoOficial)&&!/Não eleito/i.test(c.situacaoOficial)));
  const rows=r.partidos.map(g=>{const c=calcBy.get(g.id);return{...g,app:c?.total||0,qp:c?.qp||0,sobra:c?.vagasSobra||0,pctQE:c?.pctQE||0}}).sort((a,b)=>(b.vagasOficiais||0)-(a.vagasOficiais||0)||b.app-a.app||b.votosValidos-a.votosValidos);
  const qeTse=r.qe||0,qeApp=calc.qe||0;
  return `
  <div class="prop-metrics">
    <div class="card prop-metric"><span>Vagas do cargo</span><strong>${fmt(r.vagas)}</strong><small>TSE · campo nv</small></div>
    <div class="card prop-metric"><span>QE oficial TSE</span><strong>${fmt(qeTse)}</strong><small>${qeTse?'publicado pelo TSE':'aguardando votos válidos'}</small></div>
    <div class="card prop-metric"><span>QE cálculo app</span><strong>${fmt(qeApp)}</strong><small>auditável com os dados atuais</small></div>
    <div class="card prop-metric"><span>Votos válidos</span><strong>${fmt(r.validos)}</strong><small>${pct(r.pctTotalizado)} apurado</small></div>
    <div class="card prop-metric"><span>Seções/urnas totalizadas</span><strong>${fmt(r.secoesTotalizadas)}</strong><small>de ${fmt(r.secoesTotal)} · ${pct(r.pctTotalizado)}</small></div>
  </div>
  <div class="thresholds"><div class="threshold"><small>10% do QE · mínimo individual do QP</small><strong>${fmt(Math.ceil(qeApp*.10))}</strong></div><div class="threshold"><small>20% do QE · candidato na 1ª sobra</small><strong>${fmt(Math.ceil(qeApp*.20))}</strong></div><div class="threshold"><small>80% do QE · grupo na 1ª sobra</small><strong>${fmt(Math.ceil(qeApp*.80))}</strong></div></div>
  ${renderDeputyCutLine(calc,r,cargo)}
  ${r.pctTotalizado===0?'<div class="alert waiting" style="margin-top:12px">As <strong>'+fmt(r.vagas)+' vagas</strong> já são conhecidas. QE, QP, sobras e distribuição de cadeiras permanecem em zero até o TSE publicar votos válidos.</div>':''}
  <div class="prop-grid">
    <section class="card pad"><div class="section-head"><div><div class="eyebrow">Cadeiras por partido/federação</div><div class="section-title">TSE agora × cálculo do app</div></div><div class="section-note">“TSE agora” usa exatamente o campo vag do EA20</div></div>
      ${officialSeatBar(r)}
      <div class="table-wrap desktop-seat-table"><table class="seat-table"><thead><tr><th>Grupo</th><th>Votos</th><th>QP</th><th>Sobras app</th><th>TSE agora</th><th>App</th></tr></thead><tbody>${rows.map(g=>`<tr><td><strong>${esc(g.sigla)}</strong><br><span class="muted">${esc(g.tipo==='federacao'?'federação':'partido')}</span></td><td>${fmt(g.votosValidos)}</td><td>${g.qp}</td><td>${g.sobra}</td><td class="seat-big">${g.vagasOficiais||0}</td><td class="seat-big">${g.app}</td></tr>`).join('')}</tbody></table></div>
      <div class="mobile-seat-cards">${rows.map(g=>`<article class="mobile-seat-card">
        <div class="mobile-seat-head"><div><strong>${esc(g.sigla)}</strong><span>${esc(g.tipo==='federacao'?'federação':'partido')}</span></div><div class="mobile-seat-main"><small>Cadeiras TSE</small><b>${g.vagasOficiais||0}</b></div></div>
        <div class="mobile-seat-stats">
          <span><small>Votos</small><b>${fmt(g.votosValidos)}</b></span>
          <span><small>QP</small><b>${g.qp}</b></span>
          <span><small>Sobras</small><b>${g.sobra}</b></span>
          <span><small>App</small><b>${g.app}</b></span>
        </div>
      </article>`).join('')}</div>
    </section>
    <aside class="stack">
      <div class="card pad"><div class="eyebrow">A conta</div><div class="section-title">Como as cadeiras foram calculadas</div><div class="steps" style="margin-top:12px">${calc.passos.map((x,i)=>`<div class="step"><div class="step-no">${i+1}</div><p>${esc(x)}</p></div>`).join('')}</div>${calc.warnings.length?'<div class="alert waiting" style="margin-top:10px">'+calc.warnings.map(esc).join('<br>')+'</div>':''}</div>
      <div class="card pad"><div class="eyebrow">Sobras</div><div class="section-title">Rodadas por maiores médias</div><div class="round-list">${calc.rodadas.length?calc.rodadas.slice(0,12).map(x=>`<div class="round"><div class="round-head"><span>Rodada ${x.rodada} · ${esc(x.fase)}</span><span>${x.empateIndefinido?'empate':''}</span></div><div class="round-winner">${x.vencedorSigla?esc(x.vencedorSigla)+' · '+esc(x.candidatoNome||''):'sem cadeira atribuída'}</div></div>`).join(''):'<div class="empty">As rodadas aparecerão quando houver votos válidos.</div>'}</div></div>
    </aside>
  </div>
  ${renderProportionalCandidateRanking(r,cargo,calc)}
  <div class="two-col section" style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
    <section class="card pad"><div class="section-head"><div><div class="eyebrow">Situação oficial TSE</div><div class="section-title">Eleitos e suplentes</div></div><div class="section-note">${officialElected.length} eleito(s) oficial(is)</div></div><div class="candidate-list">${r.candidatos.filter(c=>c.situacaoOficial||c.eleitoTse).slice(0,80).map((c,i)=>candidateRow(c,r,cargo,i)).join('')||'<div class="empty">O TSE ainda não atribuiu situação final aos candidatos.</div>'}</div></section>
    <section class="card pad"><div class="section-head"><div><div class="eyebrow">Projeção auditável</div><div class="section-title">Eleitos pelo cálculo atual</div></div><div class="section-note">${calc.eleitos.length} identidade(s) calculada(s)</div></div><div class="candidate-list">${calc.eleitos.slice(0,80).map((e,i)=>candidateRow(e.candidato,r,cargo,i,{projected:true})).join('')||'<div class="empty">Sem projeção enquanto não houver votos suficientes.</div>'}</div></section>
  </div>`;
}
function createHemicycle(groups,totalSeats=513){
  const seats=[];for(const g of groups)for(let i=0;i<g.seats;i++)seats.push({color:politicalColor(g.sigla),sigla:g.sigla});
  while(seats.length<totalSeats)seats.push({color:'var(--border)',sigla:'não atribuída'});seats.length=totalSeats;
  const rings=12,rads=Array.from({length:rings},(_,i)=>62+i*14),sum=rads.reduce((a,b)=>a+b,0),counts=rads.map(r=>Math.floor(totalSeats*r/sum));let diff=totalSeats-counts.reduce((a,b)=>a+b,0);for(let i=rings-1;diff>0;i=(i-1+rings)%rings,diff--)counts[i]++;
  let idx=0,circles='';for(let ri=0;ri<rings;ri++){const count=counts[ri],rad=rads[ri];for(let j=0;j<count;j++){const a=Math.PI+(Math.PI*(j+.5)/count),x=260+Math.cos(a)*rad,y=222+Math.sin(a)*rad,s=seats[idx++];circles+=`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3.1" fill="${s.color}"><title>${esc(s.sigla)}</title></circle>`}}
  return `<svg viewBox="0 0 520 240" role="img" aria-label="Hemiciclo com ${totalSeats} cadeiras">${circles}<text x="260" y="218" text-anchor="middle" fill="var(--text)" font-size="24" font-weight="900">${groups.reduce((s,g)=>s+g.seats,0)} / ${totalSeats}</text><text x="260" y="234" text-anchor="middle" fill="var(--muted)" font-size="9">cadeiras atribuídas pelo TSE agora</text></svg>`;
}
function bars(rows,key='seats',maxRows=14){
  const data=rows.slice().sort((a,b)=>(b[key]||0)-(a[key]||0)).slice(0,maxRows),max=Math.max(1,...data.map(x=>x[key]||0));
  return `<div class="chart-bars">${data.map(x=>`<div class="chart-row"><div class="chart-label">${esc(x.sigla)}</div><div class="chart-track"><span style="width:${(x[key]||0)/max*100}%;background:${politicalFill(x.sigla)}"></span></div><div class="chart-value">${fmt(x[key]||0)}</div></div>`).join('')}</div>`;
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
    <section class="card hemi-card"><div class="section-head"><div><div class="eyebrow">Câmara dos Deputados</div><div class="section-title">Hemiciclo · TSE agora</div></div><div class="section-note">${seats} de ${cam.seatsTotal||513} cadeiras atribuídas</div></div><div class="hemicycle-wrap">${createHemicycle(cam.officialSeats||[],cam.seatsTotal||513)}</div><div class="seat-legend">${(cam.officialSeats||[]).slice(0,14).map(x=>`<span><i class="legend-dot" style="display:inline-block;background:${politicalFill(x.sigla)}"></i> ${esc(x.sigla)} ${x.seats}</span>`).join('')}</div></section>
    <aside class="congress-side"><div class="card metric-card"><div class="metric-label">Cadeiras Câmara</div><div class="metric-value">${seats}<span style="font-size:14px;color:var(--muted)"> / ${cam.seatsTotal||513}</span></div><div class="metric-foot">campo vag agregado das 27 UFs</div></div><div class="card metric-card"><div class="metric-label">Senadores oficiais em 2026</div><div class="metric-value">${sen.officialCount||0}<span style="font-size:14px;color:var(--muted)"> / 54</span></div><div class="metric-foot">2 vagas por UF</div></div><div class="card metric-card"><div class="metric-label">Seções/urnas totalizadas</div><div class="metric-value" style="font-size:20px">${fmt(cam.sectionsDone||0)} <span style="font-size:12px;color:var(--muted)">/ ${fmt(cam.sectionsTotal||0)}</span></div><div class="metric-foot">${pct(cam.pctSections||cam.pctAverage||0)} no agregado nacional</div></div><div class="card pad"><div class="eyebrow">Cadeiras por grupo</div><div class="section-title">Distribuição atual</div><div style="margin-top:12px">${bars(cam.officialSeats||[])}</div></div></aside>
  </div>
  <section class="section"><div class="section-head"><div><div class="eyebrow">Senado Federal</div><div class="section-title">Duas vagas por UF</div></div><div class="section-note">“líder” só vira “eleito TSE” quando o arquivo oficial indicar</div></div><div class="senate-grid">${renderSenateGrid(sen)}</div></section>
  <section class="section"><div class="two-col" style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div class="card pad"><div class="eyebrow">Câmara</div><div class="section-title">Tabela de cadeiras</div><div class="table-wrap desktop-seat-table"><table class="seat-table"><thead><tr><th>Partido/Federação</th><th>Votos</th><th>Cadeiras</th></tr></thead><tbody>${(cam.officialSeats||[]).map(x=>`<tr><td><strong>${esc(x.sigla)}</strong></td><td>${fmt(x.votes)}</td><td class="seat-big">${x.seats}</td></tr>`).join('')}</tbody></table></div>
      <div class="mobile-seat-cards congress-mobile-seat-cards">${(cam.officialSeats||[]).map(x=>`<article class="mobile-seat-card compact">
        <div class="mobile-seat-head"><div><strong>${esc(x.sigla)}</strong><span>partido/federação</span></div><div class="mobile-seat-main"><small>Cadeiras</small><b>${x.seats}</b></div></div>
        <div class="mobile-seat-stats two"><span><small>Votos</small><b>${fmt(x.votes)}</b></span><span><small>Representação</small><b>${pct((x.seats||0)/(cam.seatsTotal||513)*100)}</b></span></div>
      </article>`).join('')}</div></div><div class="card pad"><div class="eyebrow">Senado</div><div class="section-title">Eleitos por partido</div><div style="margin-top:12px">${sen.officialCount?bars(sen.byParty||[]):'<div class="empty">O TSE ainda não atribuiu senadores eleitos.</div>'}</div></div></div></section>`;
}
function renderSenateGrid(sen){
  return (sen.ufs||[]).map(u=>{const list=u.official?.length?u.official:u.leaders||[];return `<div class="senate-uf"><strong>${u.uf} · ${pct(u.pct||0)}</strong>${list.slice(0,2).map(c=>`<div class="senate-name ${c.official?'official':''}">${c.official?'✓ ':''}${esc(c.nome)} · ${esc(c.partido)}</div>`).join('')||'<div class="senate-name">aguardando</div>'}</div>`}).join('');
}


function electedStatusBadge(kind,text){
  const cls=kind==='official'?'official-badge':kind==='projection'?'projection-badge':kind==='runoff'?'leader-badge':'supp-badge';
  return `<span class="${cls}">${esc(text)}</span>`;
}
function electedCandidateCard(c,{cargo='',uf='',kind='official',status='',reason=''}={}){
  const fav=candidateForFavorite({...c,uf:uf||c.uf,cargoCodigo:cargo||c.cargoCodigo},null,cargo||c.cargoCodigo);
  const reasonText=reason==='QP'?'QP':/média/.test(String(reason))?'sobra/média':'';
  const shownStatus=status||(kind==='official'?'ELEITO TSE':'PROJETADO ELEITO · cálculo atual');
  const visual=visualClassFromStatus(shownStatus,kind);
  const pColor=partyColor(c.partido||'');
  return `<div class="elected-candidate-card${visual}" style="--party-color:${pColor}" data-candidate-name="${esc(c.nome)}" data-candidate-party="${esc(c.partido||'')}" data-candidate-federation="${esc(c.federacao||'')}">
    ${avatar(c)}
    <div class="elected-candidate-main"><div class="result-context">${esc(CARGO[String(cargo||c.cargoCodigo)]||'Candidato')} · ${esc(uf||c.uf||'')}</div><div class="cand-name">${esc(c.nome)}</div><div class="cand-meta">${esc(c.numero)} · ${fmt(c.votos)} votos</div>
      <div class="elected-card-tags"><span class="elected-party-chip"><i></i>${esc(c.partido||'Partido')}</span>${c.federacao?`<span class="elected-federation-chip">${esc(c.federacao)}</span>`:''}</div>
      ${electedStatusBadge(kind,shownStatus)}${reasonText?`<span class="reason-badge">${esc(reasonText)}</span>`:''}
    </div>
    <div class="elected-candidate-side">${favoriteButton(fav)}<strong>${pct(c.pct||0)}</strong></div>
  </div>`;
}
function electedControls(){
  const ufOpts='<option value="BR" '+(S.electedUf==='BR'?'selected':'')+'>Brasil inteiro</option>'+UFS.map(([u,n])=>`<option value="${u}" ${S.electedUf===u?'selected':''}>${n} (${u})</option>`).join('');
  const cargos=[['all','Todos os cargos'],['1','Presidente'],['3','Governador'],['5','Senado'],['6','Dep. Federal'],[S.electedUf==='DF'?'8':'7',S.electedUf==='DF'?'Dep. Distrital':'Dep. Estadual']];
  return `<div class="elected-controls">
    <div class="elected-mode-tabs"><button class="seg ${S.electedMode==='official'?'active':''}" data-elected-mode="official">Oficial TSE</button><button class="seg ${S.electedMode==='projection'?'active':''}" data-elected-mode="projection">Projeção atual</button></div>
    <div class="elected-filter-row"><select id="electedUf" class="select">${ufOpts}</select><select id="electedCargo" class="select">${cargos.map(([v,l])=>`<option value="${v}" ${S.electedCargo===v?'selected':''}>${l}</option>`).join('')}</select></div>
  </div>`;
}
function electedSection(title,subtitle,html,count=0){
  return `<section class="card elected-section"><div class="section-head"><div><div class="eyebrow">${esc(subtitle)}</div><div class="section-title">${esc(title)}</div></div><div class="section-note">${fmt(count)} resultado(s)</div></div><div class="elected-list">${html||'<div class="empty">Nenhum resultado neste filtro.</div>'}</div></section>`;
}
function wireElectedControls(){
  $('[data-elected-mode]').forEach(b=>b.onclick=()=>{S.electedMode=b.dataset.electedMode;loadElected(false)});
  $('#electedUf')?.addEventListener('change',e=>{S.electedUf=e.target.value;S.electedCargo='all';S.electedName='';S.electedParty='all';loadElected(false)});
  $('#electedCargo')?.addEventListener('change',e=>{S.electedCargo=e.target.value;S.electedName='';S.electedParty='all';loadElected(false)});
}

function normalizeElectedSearch(v){
  return String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
}
function enhanceDeputyElectedView(){
  const cargo=String(S.electedCargo||'');
  if(!['6','7','8'].includes(cargo))return;
  const controls=$('#electedContent .elected-controls');
  const section=$('#electedContent .elected-section');
  const list=section?.querySelector('.elected-list');
  if(!controls||!section||!list)return;
  const cards=[...list.querySelectorAll('.elected-candidate-card')];
  if(!cards.length)return;

  const rows=cards.map(card=>{
    const party=card.dataset.candidateParty||'OUTROS';
    const federation=card.dataset.candidateFederation||'';
    return{
      card,
      name:card.dataset.candidateName||card.querySelector('.cand-name')?.textContent||'',
      party,
      federation,
      group:federation||party
    };
  });
  const parties=[...new Set(rows.map(x=>x.party).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
  const groups=[...new Set(rows.map(x=>x.group).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'pt-BR'));
  const federations=groups.filter(g=>!parties.includes(g));

  const validFilter=S.electedParty==='all'||
    (String(S.electedParty).startsWith('party|')&&parties.includes(String(S.electedParty).slice(6)))||
    (String(S.electedParty).startsWith('group|')&&groups.includes(String(S.electedParty).slice(6)));
  if(!validFilter)S.electedParty='all';

  const tools=document.createElement('div');
  tools.className='deputy-elected-tools';
  tools.innerHTML=`<label class="deputy-search-wrap"><span aria-hidden="true">⌕</span><input id="electedNameFilter" type="search" autocomplete="off" placeholder="Buscar deputado pelo nome" value="${esc(S.electedName||'')}" aria-label="Buscar deputado pelo nome"></label>
    <select id="electedPartyFilter" class="select" aria-label="Filtrar deputados por partido ou federação">
      <option value="all">Todos os partidos/federações</option>
      <optgroup label="Partidos">
        ${parties.map(p=>`<option value="party|${esc(p)}" ${S.electedParty===`party|${p}`?'selected':''}>${esc(p)}</option>`).join('')}
      </optgroup>
      ${federations.length?`<optgroup label="Federações / grupos">${federations.map(g=>`<option value="group|${esc(g)}" ${S.electedParty===`group|${g}`?'selected':''}>${esc(g)}</option>`).join('')}</optgroup>`:''}
    </select>
    <button id="clearDeputyFilters" class="ghost-btn deputy-clear-btn" type="button">Limpar</button>`;
  controls.appendChild(tools);

  const summary=document.createElement('section');
  summary.className='card deputy-party-card';
  section.parentNode.insertBefore(summary,section);

  const nameInput=tools.querySelector('#electedNameFilter');
  const partySelect=tools.querySelector('#electedPartyFilter');
  const clearBtn=tools.querySelector('#clearDeputyFilters');
  const empty=document.createElement('div');
  empty.className='empty deputy-filter-empty';
  empty.textContent='Nenhum deputado encontrado com estes filtros.';
  empty.hidden=true;
  list.appendChild(empty);

  const filterMatches=x=>{
    if(S.electedParty==='all')return true;
    const raw=String(S.electedParty);
    if(raw.startsWith('party|'))return x.party===raw.slice(6);
    if(raw.startsWith('group|'))return x.group===raw.slice(6);
    return true;
  };

  const apply=()=>{
    const q=normalizeElectedSearch(S.electedName);
    let visible=0;
    for(const x of rows){
      const okName=!q||normalizeElectedSearch(x.name).includes(q);
      const show=okName&&filterMatches(x);
      x.card.hidden=!show;
      if(show)visible++;
    }
    empty.hidden=visible!==0;
    const note=section.querySelector('.section-note');
    if(note)note.textContent=`${fmt(visible)} resultado(s)`;
    const total=$('#electedContent .elected-total strong');
    if(total)total.textContent=fmt(visible);
    clearBtn.disabled=!(S.electedName||S.electedParty!=='all');
    summary.querySelectorAll('[data-party-bar]').forEach(b=>{
      const mode=b.dataset.chartMode;
      const key=b.dataset.partyBar;
      const current=S.electedParty;
      b.classList.toggle('active',
        (mode==='party'&&current===`party|${key}`)||
        (mode==='group'&&current===`group|${key}`)
      );
    });
  };

  const renderChart=()=>{
    const chartMode=S.electedChartMode==='group'?'group':'party';
    const field=chartMode==='group'?'group':'party';
    const counts=new Map();
    for(const x of rows)counts.set(x[field],(counts.get(x[field])||0)+1);
    const distribution=[...counts.entries()].map(([label,seats])=>({label,seats})).sort((a,b)=>b.seats-a.seats||a.label.localeCompare(b.label,'pt-BR'));
    const max=Math.max(1,...distribution.map(x=>x.seats));
    const title=chartMode==='group'?'Cadeiras por partido/federação':'Cadeiras por partido';
    const sub=chartMode==='group'
      ?'Agrupa as bancadas pelo grupo proporcional informado pelo TSE.'
      :'Mostra quantos deputados de cada partido estão dentro das vagas neste recorte.';
    summary.innerHTML=`<div class="section-head deputy-party-head"><div><div class="eyebrow">Distribuição das vagas</div><div class="section-title">${title}</div><div class="deputy-party-sub">${sub}</div></div><div class="section-note">${fmt(rows.length)} vagas · ${fmt(distribution.length)} grupo(s)</div></div>
      <div class="deputy-chart-tabs" role="group" aria-label="Agrupar gráfico">
        <button type="button" class="seg ${chartMode==='party'?'active':''}" data-chart-mode="party">Partidos</button>
        <button type="button" class="seg ${chartMode==='group'?'active':''}" data-chart-mode="group">Partido/Federação</button>
      </div>
      <div class="deputy-party-chart">
        ${distribution.map((x,i)=>`<button type="button" class="deputy-party-row${i>=10?' is-extra':''}" style="--political-color:${politicalColor(x.label)}" data-party-bar="${esc(x.label)}" data-chart-mode="${chartMode}" aria-label="Filtrar por ${esc(x.label)}">
          <span class="deputy-party-rank">${i+1}</span>
          <strong title="${esc(x.label)}"><i class="party-color-dot" style="background:${politicalFill(x.label)}"></i><span>${esc(x.label)}</span></strong>
          <span class="deputy-party-track"><i style="width:${(x.seats/max*100).toFixed(2)}%;background:${politicalFill(x.label)}"></i></span>
          <b>${fmt(x.seats)}</b>
        </button>`).join('')}
      </div>
      ${distribution.length>10?'<button type="button" class="deputy-show-all" id="deputyShowAll">Ver todos</button>':''}
      <div class="deputy-party-note">Toque em uma barra para filtrar a lista abaixo. A busca por nome continua funcionando junto com o filtro.</div>`;

    summary.querySelectorAll('[data-chart-mode]').forEach(b=>{
      if(!b.classList.contains('deputy-party-row'))b.addEventListener('click',()=>{
        S.electedChartMode=b.dataset.chartMode;
        renderChart();
        apply();
      });
    });
    summary.querySelectorAll('[data-party-bar]').forEach(b=>b.addEventListener('click',()=>{
      const mode=b.dataset.chartMode;
      const value=b.dataset.partyBar;
      const next=mode==='group'?`group|${value}`:`party|${value}`;
      S.electedParty=S.electedParty===next?'all':next;
      partySelect.value=S.electedParty;
      apply();
      section.scrollIntoView({behavior:'smooth',block:'start'});
    }));
    summary.querySelector('#deputyShowAll')?.addEventListener('click',e=>{
      const expanded=summary.classList.toggle('show-all-parties');
      e.currentTarget.textContent=expanded?'Mostrar menos':'Ver todos';
    });
  };

  nameInput.addEventListener('input',e=>{S.electedName=e.target.value;apply()});
  partySelect.addEventListener('change',e=>{S.electedParty=e.target.value;apply()});
  clearBtn.addEventListener('click',()=>{
    S.electedName='';S.electedParty='all';nameInput.value='';partySelect.value='all';apply();nameInput.focus();
  });
  renderChart();
  apply();
}

async function loadElected(force=false){
  const host=$('#electedContent');if(!host)return;
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Painel consolidado</div><h1 class="page-title">Eleitos e projeções</h1><div class="page-sub">Oficial TSE separado da projeção proporcional do app.</div></div></div>${electedControls()}<div class="card pad loading"><div class="empty">Atualizando resultados…</div></div>`;
  wireElectedControls();
  const mode=S.electedMode,uf=S.electedUf,cargoFilter=S.electedCargo;
  const include=c=>cargoFilter==='all'||String(cargoFilter)===String(c);
  let sections=[],officialCount=0,projectionCount=0;

  if(uf==='BR'){
    const [pres,gov,agg]=await Promise.all([
      fetchResult('1','BR',force),
      S.governors&&!force?Promise.resolve(S.governors):governorSummaryClient(force),
      congressClient(force)
    ]);
    S.governors=gov;S.congress={camara:agg.cam,senado:agg.sen};

    if(include('1')){
      const marked=pres.candidatos.map((c,i)=>({c,info:officialInfo(c,pres,'1',i)})).filter(x=>x.info?.official);
      const list=mode==='official'?marked:(marked.length?marked:(pres.pctTotalizado>0?[{c:pres.candidatos[0],info:officialInfo(pres.candidatos[0],pres,'1',0)}]:[]));
      officialCount+=mode==='official'?list.length:0;projectionCount+=mode==='projection'&&!marked.length?list.length:0;
      sections.push(electedSection('Presidente','Brasil',list.map(x=>electedCandidateCard(x.c,{cargo:'1',uf:'BR',kind:x.info?.official?'official':'projection',status:x.info?.label||'LIDERANDO · não oficial'})).join(''),list.length));
    }
    if(include('3')){
      const rows=[];
      for(const x of gov.states||[]){
        const st=governorVisualState(x),c=st.candidate;if(!c)continue;
        if(mode==='official'&&st.elected){rows.push(electedCandidateCard(c,{cargo:'3',uf:x.uf,kind:'official',status:'ELEITO TSE'}));officialCount++}
        else if(mode==='projection'&&!st.elected&&x.pct>0){rows.push(electedCandidateCard(c,{cargo:'3',uf:x.uf,kind:st.runoff?'runoff':'projection',status:st.runoff?'2º TURNO TSE':'LIDERANDO · não oficial'}));projectionCount++}
      }
      sections.push(electedSection('Governadores','27 UFs',rows.join(''),rows.length));
    }
    if(include('5')){
      const rows=[];
      for(const u of agg.sen.ufs||[]){
        const list=mode==='official'?(u.official||[]):(u.official?.length?u.official:u.leaders||[]);
        for(const c of list){rows.push(electedCandidateCard(c,{cargo:'5',uf:u.uf,kind:c.official?'official':'projection',status:c.official?'ELEITO TSE':'NAS 2 VAGAS AGORA · não oficial'}));c.official?officialCount++:projectionCount++}
      }
      sections.push(electedSection('Senado Federal','54 vagas em disputa',rows.join(''),rows.length));
    }
    if(include('6')){
      const list=mode==='official'?(agg.cam.officialElected||[]):(agg.cam.projectedElected||[]);
      for(const c of list)c.projectionReason&&projectionCount++;
      officialCount+=mode==='official'?list.length:0;
      sections.push(electedSection('Deputados Federais','Brasil inteiro',list.map(c=>electedCandidateCard(c,{cargo:'6',uf:c.uf,kind:mode==='official'?'official':'projection',status:mode==='official'?(c.situacaoOficial||'ELEITO TSE'):'PROJETADO ELEITO · cálculo atual',reason:c.projectionReason})).join(''),list.length));
    }
    if(include('7')||include('8'))sections.push(electedSection('Deputados Estaduais/Distritais','Escolha uma UF',`<div class="empty">Para Estadual/Distrital, escolha uma UF no filtro acima. Assim o painel não precisa carregar as 27 assembleias de uma vez.</div>`,0));
  }else{
    const depCargo=uf==='DF'?'8':'7';
    const [gov,sen,fed,est]=await Promise.all([
      fetchResult('3',uf,force),fetchResult('5',uf,force),fetchResult('6',uf,force),fetchResult(depCargo,uf,force)
    ]);
    const races=[['3',gov],['5',sen],['6',fed],[depCargo,est]];
    for(const [cargo,r] of races){
      if(!include(cargo))continue;
      let list=[],cards='';
      if(cargo==='3'||cargo==='5'){
        const marked=r.candidatos.map((c,i)=>({c,info:officialInfo(c,r,cargo,i)})).filter(x=>x.info?.official);
        const needed=cargo==='5'?2:1;
        if(mode==='official')list=marked;
        else{
          list=marked.slice();
          if(r.pctTotalizado>0&&list.length<needed){
            for(let i=0;i<r.candidatos.length&&list.length<needed;i++){
              const c=r.candidatos[i];if(!list.some(x=>String(x.c.id)===String(c.id)))list.push({c,info:officialInfo(c,r,cargo,i)});
            }
          }
        }
        cards=list.map((x,i)=>electedCandidateCard(x.c,{cargo,uf,kind:x.info?.official?'official':'projection',status:x.info?.label||(cargo==='5'?'NAS 2 VAGAS AGORA · não oficial':'LIDERANDO · não oficial')})).join('');
        officialCount+=list.filter(x=>x.info?.official).length;projectionCount+=list.filter(x=>!x.info?.official).length;
      }else{
        const calc=calcularProporcional(r);
        if(mode==='official')list=r.candidatos.filter(officialCandidate).map(c=>({candidato:c,motivo:''}));
        else list=calc.eleitos||[];
        cards=list.map(e=>electedCandidateCard(e.candidato,{cargo,uf,kind:mode==='official'?'official':'projection',status:mode==='official'?(e.candidato.situacaoOficial||'ELEITO TSE'):'PROJETADO ELEITO · cálculo atual',reason:e.motivo})).join('');
        mode==='official'?officialCount+=list.length:projectionCount+=list.length;
      }
      sections.push(electedSection(CARGO[cargo],uf,cards,list.length));
    }
  }

  const total=mode==='official'?officialCount:projectionCount;
  host.innerHTML=`<div class="page-head"><div><div class="eyebrow">Painel consolidado</div><h1 class="page-title">Eleitos e projeções</h1><div class="page-sub">${mode==='official'?'Somente situações oficiais publicadas pelo TSE.':'Projeção dinâmica do app; não é resultado oficial.'}</div></div><div class="elected-total ${mode}"><strong>${fmt(total)}</strong><span>${mode==='official'?'oficiais neste filtro':'projetados neste filtro'}</span></div></div>${electedControls()}<div class="elected-sections">${sections.join('')}</div>`;
  wireElectedControls();enhanceDeputyElectedView();wireFavorites(host);syncFavoriteButtons();
}

const FAVORITES_KEY='ap26-favorites-v1';
const FAVORITE_HISTORY_KEY='ap26-favorite-history-v1';
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
function visualClassFromStatus(status,kind=''){
  const s=String(status||'').toLowerCase();
  const negative=/não eleito|nao eleito|suplente|fora das vagas/.test(s);
  const runoff=/2.?\s*turno|segundo turno/.test(s);
  const elected=!negative&&(/eleito tse|eleito · tse|^eleito\b/.test(s));
  const projected=/projetado eleito/.test(s)||(kind==='projection'&&!runoff&&!negative);
  return elected?' official-card-green':runoff?' official-card-orange':projected?' projected-card-green':'';
}
function favoritePageCard(c){
  registerCandidate(c);
  const status=c.liveStatus||c.status||c.st||c.situacaoOficial||'';
  const delta=Number(c.deltaVotes||0),move=Number(c.rankChange||0),rank=Number(c.rank||0);
  const statusCls=/ELEITO TSE|2º TURNO TSE/i.test(status)?'official-badge':/PROJETADO ELEITO/i.test(status)?'projection-badge':/Liderando/i.test(status)?'leader-badge':/Não eleito|Suplente|Fora/i.test(status)?'supp-badge':'';
  const visual=visualClassFromStatus(status,c.projected?'projection':'');
  return `<div class="favorite-page-card favorite-live-card${visual}">
    ${avatar(c)}
    <div class="favorite-main"><div class="result-context">${esc(c.cargo||CARGO[favoriteCargoCode(c)]||'Candidato')} · ${esc(c.uf||'')}</div>
      <div class="cand-name">${esc(c.nome)}</div>
      <div class="cand-meta">${esc(c.numero)} · ${esc(c.partido)} · ${fmt(c.votos)} votos</div>
      ${status?`<span class="${statusCls}">${esc(status)}</span>`:''}
      <div class="favorite-live-meta">
        <span><b>${rank?'#'+rank:'—'}</b> posição</span>
        <span class="${delta>0?'up':''}"><b>${delta>0?'+'+fmt(delta):'—'}</b> votos desde a última</span>
        <span class="${move>0?'up':move<0?'down':''}"><b>${move>0?'↑ '+move:move<0?'↓ '+Math.abs(move):'→'}</b> posição</span>
        <span><b>${pct(c.apuracaoPct||0)}</b> apurado</span>
      </div>
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
  const history=readJsonLocal(FAVORITE_HISTORY_KEY,{});
  const nextHistory={...history};
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
      const deputy=['6','7','8'].includes(String(g.cargo));
      const calc=deputy?calcularProporcional(r):null;
      const projectedIds=new Set((calc?.eleitos||[]).map(e=>String(e.candidato?.id||'')));
      for(const old of g.items){
        const id=String(old.sqcand||old.id||''),num=String(old.numero||'');
        const rankIndex=r.candidatos.findIndex(x=>String(x.id||x.sqcand||'')===id||(num&&String(x.numero||'')===num));
        const c=rankIndex>=0?r.candidatos[rankIndex]:null;
        if(c){
          const base=candidateForFavorite(c,r,g.cargo),key=favoriteKey(base),prev=history[key]||history[favoriteKey(old)]||{};
          const oi=officialInfo(c,r,g.cargo,rankIndex);
          const officialElected=!!oi?.official&&/eleit/i.test(String(oi.label||''))&&!/não|nao|suplente|2.? ?turno/i.test(String(oi.label||''));
          const projected=deputy&&projectedIds.has(String(c.id||''))&&!officialElected;
          let liveStatus='';
          if(officialElected)liveStatus='ELEITO TSE';
          else if(oi?.official&&/2.? ?turno/i.test(String(oi.label||'')))liveStatus='2º TURNO TSE';
          else if(projected)liveStatus='PROJETADO ELEITO · cálculo atual';
          else if(oi?.label)liveStatus=oi.label.replace(/ · TSE$/,'');
          else if(deputy)liveStatus='Fora das vagas projetadas';
          const fresh={...base,rank:rankIndex+1,deltaVotes:prev.votes===undefined?0:Number(c.votos||0)-Number(prev.votes||0),rankChange:prev.rank?Number(prev.rank)-(rankIndex+1):0,apuracaoPct:r.pctTotalizado,liveStatus,projected};
          const oldKey=favoriteKey(old);
          updated.delete(oldKey);updated.set(key,fresh);
          nextHistory[key]={votes:Number(c.votos||0),rank:rankIndex+1,at:Date.now()};
        }
      }
    }
  }
  saveFavorites([...updated.values()]);
  localStorage.setItem(FAVORITE_HISTORY_KEY,JSON.stringify(nextHistory));
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
    else if(view==='eleitos')await loadElected(force);
    else if(view==='favoritos')await loadFavorites(force);
    else if(view==='buscar')initSearch();
    else if(view==='como')loadHow();
  }catch(e){const id=view==='presidente'?'presidentContent':view==='estados'?'stateContent':view==='congresso'?'congressContent':view==='eleitos'?'electedContent':view==='buscar'?'searchContent':view==='favoritos'?'favoritesContent':view==='como'?'howContent':'agoraContent';$('#'+id).innerHTML=`<div class="card pad"><div class="alert danger">Não foi possível carregar esta tela agora. ${esc(e.message||'')} <button class="ghost-btn" id="retryBtn">tentar novamente</button></div></div>`;$('#retryBtn')?.addEventListener('click',()=>loadView(view,true))}
}
function showView(view){
  S.view=view;$$('.view').forEach(v=>v.classList.toggle('active',v.id==='view-'+view));$$('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));window.scrollTo(0,0);loadView(view,false);restartPoll();
}
function wireGo(){
  $$('[data-go]').forEach(b=>b.onclick=()=>showView(b.dataset.go));$$('[data-uf]').forEach(b=>b.onclick=()=>{S.uf=b.dataset.uf;S.cargo='3';showView('estados')});
}
function restartPoll(){clearInterval(S.poll);if(['agora','presidente','estados','congresso','eleitos','favoritos'].includes(S.view))S.poll=setInterval(async()=>{if(document.visibilityState==='visible'){if(Date.now()>=new Date('2026-10-20T00:00:00-03:00').getTime())await discoverCodes();loadView(S.view,true)}},30000)}
function setTheme(t){document.documentElement.dataset.theme=t;localStorage.setItem('ap26-theme',t);$('#themeBtn').textContent=t==='dark'?'☀':'☾'}
function initTheme(){const t=localStorage.getItem('ap26-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');setTheme(t)}
async function boot(){
  initTheme();
  $('#themeBtn').onclick=()=>setTheme(document.documentElement.dataset.theme==='dark'?'light':'dark');
  $('#refreshBtn').onclick=()=>loadView(S.view,true);
  $$('[data-view]').forEach(b=>b.onclick=()=>showView(b.dataset.view));
  $('.brand').onclick=()=>showView('agora');
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='visible')loadView(S.view,true)});
  const qs=new URLSearchParams(location.search);
  const requestedView=qs.get('view');
  const requestedMode=qs.get('mode');
  if(['auto','round1','round2','polls'].includes(requestedMode||''))S.presidentMode=requestedMode;
  updateFavoriteBadges();
  const initialView=['agora','presidente','estados','congresso','eleitos','favoritos','buscar','como'].includes(requestedView||'')?requestedView:'agora';
  showView(initialView);
  discoverCodes().then(()=>{
    if(document.visibilityState==='visible'&&S.view===initialView)loadView(S.view,false);
  }).catch(()=>{});
}
boot();

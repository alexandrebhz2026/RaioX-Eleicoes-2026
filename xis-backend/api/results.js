const TSE_BASE='https://resultados.tse.jus.br/oficial';
const CONFIG_URL=`${TSE_BASE}/comum/config/ele-c.json`;
const OFFICES={PRESIDENTE:'Presidente',GOVERNADOR:'Governador',SENADOR:'Senador',DEPUTADO_FEDERAL:'Deputado Federal',DEPUTADO_ESTADUAL:'Deputado Estadual',DEPUTADO_DISTRITAL:'Deputado Distrital'};

function clean(v,max=180){return String(v??'').replace(/[\u0000-\u001F\u007F]/g,' ').replace(/\s+/g,' ').trim().slice(0,max)}
function send(res,status,body,cache='public, s-maxage=15, stale-while-revalidate=20'){res.statusCode=status;res.setHeader('Content-Type','application/json; charset=utf-8');res.setHeader('Cache-Control',cache);res.end(JSON.stringify(body))}
function pad(v,n){return String(v||'').padStart(n,'0')}
function num(v){const n=Number(String(v??'').replace(',','.'));return Number.isFinite(n)?n:0}
function dateBRToKey(v){const m=String(v||'').match(/^(\d{2})\/(\d{2})\/(\d{4})$/);return m?`${m[3]}-${m[2]}-${m[1]}`:''}

function findElection(config,office,uf){
  const targetDate='04/10/2026';
  const pleitos=(Array.isArray(config?.pl)?config.pl:[]).filter(p=>p?.dt===targetDate);
  for(const pl of pleitos){
    for(const e of Array.isArray(pl?.e)?pl.e:[]){
      for(const abr of Array.isArray(e?.abr)?e.abr:[]){
        const abrUf=String(abr?.cd||'').toUpperCase();
        const wantedScope=office==='PRESIDENTE'?'BR':uf;
        if(abrUf!==wantedScope)continue;
        const cargo=(Array.isArray(abr?.cp)?abr.cp:[]).find(cp=>clean(cp?.ds,80).toUpperCase()===OFFICES[office].toUpperCase());
        if(cargo)return {pleito:pl,election:e,cargo,scope:wantedScope.toLowerCase()};
      }
    }
  }
  return null;
}

function normalizeCandidates(data){
  return (Array.isArray(data?.cand)?data.cand:[]).map(c=>({
    number:clean(c?.n||c?.nr||'',12),
    name:clean(c?.nm||c?.nmu||c?.nmUrna||'',100),
    party:clean(c?.cc||c?.sgp||c?.p||'',40),
    votes:num(c?.vap||c?.v||0),
    percent:num(c?.pvap||c?.pVap||c?.pv||0),
    status:clean(c?.st||c?.sit||'',60)
  })).filter(c=>c.name||c.number).sort((a,b)=>b.votes-a.votes||b.percent-a.percent).slice(0,120);
}

function normalizeTotals(data){
  const pctSections=num(data?.pst||data?.pSt||data?.ps||0);
  const totalSections=num(data?.s||data?.stot||0),sectionsDone=num(data?.st||data?.sTot||0);
  const validVotes=num(data?.vv||data?.vvc||0),votes=num(data?.v||data?.tv||0);
  return {percentSections:pctSections,totalSections,sectionsDone,validVotes,votes,blankVotes:num(data?.vb||0),nullVotes:num(data?.vn||0),abstentions:num(data?.a||0),electorate:num(data?.e||0)};
}

export default async function handler(req,res){
  if(req.method!=='GET')return send(res,405,{ok:false,error:'METHOD_NOT_ALLOWED'},'no-store');
  let office=clean(String(req.query?.office||'PRESIDENTE').toUpperCase().replace(/[^A-Z_]/g,''),30);if(!OFFICES[office])office='PRESIDENTE';
  let uf=office==='PRESIDENTE'?'BR':clean(String(req.query?.uf||'MG').toUpperCase().replace(/[^A-Z]/g,''),2);
  if(office==='DEPUTADO_DISTRITAL'&&uf!=='DF')return send(res,200,{ok:true,active:false,status:'not_applicable',office,uf,updatedAt:new Date().toISOString(),message:'Deputado Distrital existe apenas no Distrito Federal.',source:'TSE'});
  if(office==='DEPUTADO_ESTADUAL'&&uf==='DF')office='DEPUTADO_DISTRITAL';
  try{
    const cfgResp=await fetch(`${CONFIG_URL}?t=${Math.floor(Date.now()/15000)}`,{headers:{Accept:'application/json'}});
    const config=await cfgResp.json().catch(()=>null);
    if(!cfgResp.ok||!config)return send(res,200,{ok:true,active:false,status:'waiting_source',office,uf,updatedAt:new Date().toISOString(),message:'Aguardando disponibilidade da fonte oficial do TSE.',source:'TSE'});
    const found=findElection(config,office,uf);
    if(!found)return send(res,200,{ok:true,active:false,status:'not_started',office,uf,updatedAt:new Date().toISOString(),message:'Apuração ainda não iniciada. O RAIO-X ativará o acompanhamento quando o TSE publicar a eleição de 2026.',source:'TSE',configGeneratedAt:`${clean(config.dg,20)} ${clean(config.hg,20)}`});
    const cd=String(found.election.cd),cargo=pad(found.cargo.cd,4),e6=pad(cd,6),scope=found.scope;
    const resultUrl=`${TSE_BASE}/ele2026/${cd}/dados-simplificados/${scope}/${scope}-c${cargo}-e${e6}-r.json`;
    const resultResp=await fetch(`${resultUrl}?t=${Math.floor(Date.now()/15000)}`,{headers:{Accept:'application/json'}});
    if(!resultResp.ok)return send(res,200,{ok:true,active:false,status:'not_started',office,uf,updatedAt:new Date().toISOString(),message:'A eleição de 2026 já foi identificada, mas o TSE ainda não publicou a apuração deste cargo.',source:'TSE',resultUrl});
    const data=await resultResp.json().catch(()=>null);if(!data)throw new Error('INVALID_TSE_JSON');
    const totals=normalizeTotals(data),candidates=normalizeCandidates(data);
    const active=totals.percentSections>0||totals.sectionsDone>0||totals.votes>0||candidates.some(c=>c.votes>0);
    return send(res,200,{ok:true,active,status:active?'live':'not_started',office,uf,updatedAt:new Date().toISOString(),tseUpdatedAt:`${clean(data.dg,20)} ${clean(data.hg,20)}`.trim(),electionCode:cd,pleitoCode:String(found.pleito.cd||''),cargoCode:String(found.cargo.cd||''),cargo:clean(found.cargo.ds,80),scope:scope.toUpperCase(),totals,candidates,message:active?'Apuração oficial do TSE em andamento.':'O TSE já publicou a estrutura da eleição, mas ainda não há votos totalizados.',source:'TSE',resultUrl});
  }catch(e){return send(res,200,{ok:true,active:false,status:'waiting_source',office,uf,updatedAt:new Date().toISOString(),message:'Não foi possível consultar a fonte oficial agora. O app mantém o último resultado válido e tenta novamente.',source:'TSE',detail:clean(e?.message||e,120)});}
}

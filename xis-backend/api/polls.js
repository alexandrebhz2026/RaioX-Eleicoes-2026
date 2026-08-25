const MODEL='gpt-5.4-nano';
const ALLOWED_INSTITUTES=['Datafolha','Quaest'];

const PRESIDENT_FALLBACK=[
  {id:'df-br-2108',institute:'Datafolha',published:'21/08/2026',field:'18 a 20/08/2026',sample:2058,margin:2,registry:'BR-04496/2026',sourceUrl:'https://www1.folha.uol.com.br/poder/2026/08/datafolha-lula-marca-39-no-1o-turno-e-flavio-bolsonaro-tem-33.shtml',results:[['Lula','PT',39],['Flavio Bolsonaro','PL',33],['Ronaldo Caiado','PSD',5],['Renan Santos','Missao',4],['Romeu Zema','Novo',3],['Augusto Cury','Avante',2],['Branco/Nulo','',8],['Nao sabe','',3]]},
  {id:'quaest-br-1408',institute:'Quaest',published:'14/08/2026',field:'10 a 13/08/2026',sample:2004,margin:2,registry:'BR-06773/2026',sourceUrl:'https://quaest.com.br/relatorios/pesquisa-de-intencao-de-voto-para-presidente-1ot-rodada-1-14-08-2026/',results:[['Lula','PT',38],['Flavio Bolsonaro','PL',31],['Renan Santos','Missao',4],['Ronaldo Caiado','PSD',4],['Augusto Cury','Avante',2],['Romeu Zema','Novo',2],['Samara Martins','UP',1],['Branco/Nulo','',8],['Indecisos','',10]]}
];

const MG_GOVERNOR_FALLBACK=[
  {id:'df-mg-gov-2108',institute:'Datafolha',published:'21/08/2026',field:'18 a 20/08/2026',sample:1204,margin:3,registry:'MG-00446/2026',sourceUrl:'https://www1.folha.uol.com.br/poder/2026/08/datafolha-cleitinho-lidera-disputa-em-mg-com-32-patrus-e-kalil-tem-12-cada.shtml',results:[['Cleitinho Azevedo','Republicanos',32],['Patrus Ananias','PT',12],['Alexandre Kalil','PDT',12],['Mateus Simões','PSD',4],['Flávio Roscoe','PL',4],['Gabriel Azevedo','MDB',4],['Túlio Lopes','PCB',2],['Rafael Duda','PSTU',1],['Ben Mendes','Missão',1],['Indira Xavier','UP',1],['Henrique Áreas','PCO',0],['Branco/Nulo','',14],['Indecisos','',13]]},
  {id:'quaest-mg-gov-2807',institute:'Quaest',published:'28/07/2026',field:'22 a 26/07/2026',sample:1482,margin:3,registry:'MG-03490/2026',sourceUrl:'https://quaest.com.br/pesquisa-genial-quaest-eleicoes-em-minas-e-pernambuco/',results:[['Cleitinho Azevedo','Republicanos',35],['Alexandre Kalil','PDT',12],['Patrus Ananias','PT',10],['Mateus Simões','PSD',6],['Gabriel Azevedo','MDB',4],['Ben Mendes','Missão',2],['Flávio Roscoe','PL',2],['Maria da Consolação','PSOL',1],['Jarbas Soares Júnior','PSB',0],['Rafael Duda','PSTU',0],['Túlio Lopes','PCB',0],['Indecisos','',15],['Branco/Nulo/Não vai votar','',13]]}
];

function send(res,status,body,cache='public, s-maxage=900, stale-while-revalidate=3600'){
  res.statusCode=status;
  res.setHeader('Content-Type','application/json; charset=utf-8');
  res.setHeader('Cache-Control',cache);
  res.end(JSON.stringify(body));
}
function clean(v,max=300){return String(v??'').replace(/[\u0000-\u001F\u007F]/g,' ').replace(/\s+/g,' ').trim().slice(0,max)}
function textFromResponse(data){
  if(typeof data?.output_text==='string'&&data.output_text.trim())return data.output_text.trim();
  const parts=[];
  for(const item of Array.isArray(data?.output)?data.output:[])for(const c of Array.isArray(item?.content)?item.content:[])if((c?.type==='output_text'||c?.type==='text')&&c.text)parts.push(c.text);
  return parts.join('\n').trim();
}
function parseJson(text){
  const raw=String(text||'').trim().replace(/^```(?:json)?\s*/i,'').replace(/```$/,'').trim();
  const a=raw.indexOf('{'),b=raw.lastIndexOf('}');
  if(a<0||b<=a)throw new Error('NO_JSON');
  return JSON.parse(raw.slice(a,b+1));
}
function dateScore(v){
  const m=String(v||'').match(/(\d{2})\/(\d{2})\/(\d{4})/);
  return m?Number(`${m[3]}${m[2]}${m[1]}`):0;
}
function sourceAllowed(institute,url){
  const u=String(url||'').toLowerCase();
  if(!/^https:\/\//.test(u))return false;
  if(institute==='Datafolha')return u.includes('folha.uol.com.br')||u.includes('uol.com.br');
  if(institute==='Quaest')return u.includes('quaest.com.br')||u.includes('uol.com.br')||u.includes('g1.globo.com');
  return false;
}
function normalizePoll(p,office,uf){
  if(!p||!ALLOWED_INSTITUTES.includes(p.institute))return null;
  const results=(Array.isArray(p.results)?p.results:[]).map(r=>[clean(r?.[0],90),clean(r?.[1],30),Number(r?.[2])]).filter(r=>r[0]&&Number.isFinite(r[2])&&r[2]>=0&&r[2]<=100);
  const sourceUrl=sourceAllowed(p.institute,p.sourceUrl)?String(p.sourceUrl):'';
  if(results.length<2||!sourceUrl||!/^([A-Z]{2}|BR)-\d{5}\/2026$/.test(clean(p.registry,40)))return null;
  return {id:clean(p.id||`${p.institute}-${office}-${uf}-${p.published||Date.now()}`,120),institute:p.institute,office,uf,published:clean(p.published,20),field:clean(p.field,60),sample:Number(p.sample)||null,margin:Number(p.margin)||null,registry:clean(p.registry,40),sourceUrl,results};
}
function fallbackFor(office,uf){
  if(office==='PRESIDENTE')return PRESIDENT_FALLBACK.map(p=>({...p,office:'PRESIDENTE',uf:'BR'}));
  if(office==='GOVERNADOR'&&uf==='MG')return MG_GOVERNOR_FALLBACK.map(p=>({...p,office:'GOVERNADOR',uf:'MG'}));
  return [];
}
function mergePerInstitute(fresh,fallback){
  const out=[];
  for(const institute of ALLOWED_INSTITUTES){
    const live=fresh.find(p=>p.institute===institute),base=fallback.find(p=>p.institute===institute);
    if(live&&(!base||dateScore(live.published)>dateScore(base.published)))out.push(live);
    else if(base)out.push(base);
    else if(live)out.push(live);
  }
  return out;
}
async function searchLatest(office,uf){
  if(!process.env.OPENAI_API_KEY)throw new Error('OPENAI_NOT_CONFIGURED');
  const target=office==='GOVERNADOR'?`governador de ${uf}`:'Presidente da Republica';
  const today=new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',dateStyle:'short'}).format(new Date());
  const prompt=`Hoje e ${today}. Encontre a pesquisa eleitoral MAIS RECENTE publicada por cada um destes institutos: Datafolha e Quaest, para ${target}, Eleicoes 2026 no Brasil. Use busca na web. Para Datafolha use Folha/UOL; para Quaest priorize quaest.com.br e aceite UOL/G1 apenas como apoio. Confirme o registro na Justica Eleitoral. Nao misture cenarios nem segundo turno. O campo field deve ser SOMENTE o periodo de coleta. Retorne SOMENTE JSON {"polls":[{"id":"...","institute":"Datafolha|Quaest","published":"DD/MM/AAAA","field":"DD a DD/MM/AAAA","sample":2000,"margin":2,"registry":"BR-00000/2026","sourceUrl":"https://...","results":[["Nome","Partido",39]]}]}. Se nao conseguir confirmar fonte, registro e percentuais, omita a pesquisa. Nao invente dados.`;
  const response=await fetch('https://api.openai.com/v1/responses',{method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${process.env.OPENAI_API_KEY}`},body:JSON.stringify({model:MODEL,input:[{role:'system',content:'Voce e um extrator factual de pesquisas eleitorais brasileiras. Use somente fontes encontradas na web e devolva JSON estrito. Nunca recomende voto.'},{role:'user',content:prompt}],tools:[{type:'web_search'}],max_output_tokens:1800,store:false})});
  const data=await response.json().catch(()=>({}));
  if(!response.ok)throw new Error(clean(data?.error?.message||`HTTP_${response.status}`));
  const parsed=parseJson(textFromResponse(data));
  return (Array.isArray(parsed.polls)?parsed.polls:[]).map(p=>normalizePoll(p,office,uf)).filter(Boolean);
}

export default async function handler(req,res){
  if(req.method!=='GET')return send(res,405,{ok:false,error:'METHOD_NOT_ALLOWED'},'no-store');
  const office=String(req.query?.office||'PRESIDENTE').toUpperCase()==='GOVERNADOR'?'GOVERNADOR':'PRESIDENTE';
  const uf=office==='GOVERNADOR'?clean(String(req.query?.uf||'MG').toUpperCase().replace(/[^A-Z]/g,''),2):'BR';
  const fetchedAt=new Date().toISOString(),fallback=fallbackFor(office,uf);
  try{
    const freshPolls=await searchLatest(office,uf),polls=mergePerInstitute(freshPolls,fallback);
    const freshInstitutes=freshPolls.filter(p=>!fallback.find(f=>f.institute===p.institute)||dateScore(p.published)>dateScore(fallback.find(f=>f.institute===p.institute)?.published)).map(p=>p.institute);
    return send(res,200,{ok:true,fresh:freshInstitutes.length>0,office,uf,fetchedAt,polls,freshInstitutes,warning:polls.length?'':'Nenhuma pesquisa confiavel encontrada para este cargo/UF.'});
  }catch(e){
    return send(res,200,{ok:true,fresh:false,office,uf,fetchedAt,polls:fallback,freshInstitutes:[],warning:fallback.length?'Atualizacao online indisponivel; exibindo ultima carga valida.':'Nenhuma pesquisa confiavel encontrada para este cargo/UF.',detail:clean(e?.message||e,160)});
  }
}

const MODEL='gpt-5.4-nano';
const ALLOWED_INSTITUTES=['Datafolha','Quaest'];

const PRESIDENT_FALLBACK=[
  {id:'df-br-2108',institute:'Datafolha',published:'21/08/2026',field:'18 a 20/08/2026',sample:2058,margin:2,registry:'BR-04496/2026',sourceUrl:'https://www1.folha.uol.com.br/poder/2026/08/datafolha-lula-marca-39-no-1o-turno-e-flavio-bolsonaro-tem-33.shtml',results:[['Lula','PT',39],['Flavio Bolsonaro','PL',33],['Ronaldo Caiado','PSD',5],['Renan Santos','Missao',4],['Romeu Zema','Novo',3],['Augusto Cury','Avante',2],['Branco/Nulo','',8],['Nao sabe','',3]]},
  {id:'quaest-br-1408',institute:'Quaest',published:'14/08/2026',field:'10 a 13/08/2026',sample:2004,margin:2,registry:'BR-06773/2026',sourceUrl:'https://quaest.com.br/relatorios/pesquisa-de-intencao-de-voto-para-presidente-1ot-rodada-1-14-08-2026/',results:[['Lula','PT',38],['Flavio Bolsonaro','PL',31],['Renan Santos','Missao',4],['Ronaldo Caiado','PSD',4],['Augusto Cury','Avante',2],['Romeu Zema','Novo',2],['Samara Martins','UP',1],['Branco/Nulo','',8],['Indecisos','',10]]}
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
function normalizePoll(p,office,uf){
  if(!p||!ALLOWED_INSTITUTES.includes(p.institute))return null;
  const results=(Array.isArray(p.results)?p.results:[]).map(r=>[clean(r?.[0],90),clean(r?.[1],30),Number(r?.[2])]).filter(r=>r[0]&&Number.isFinite(r[2])&&r[2]>=0&&r[2]<=100);
  if(results.length<2)return null;
  return {
    id:clean(p.id||`${p.institute}-${office}-${uf}-${p.published||Date.now()}`,120),
    institute:p.institute,office,uf,
    published:clean(p.published,20),field:clean(p.field,60),sample:Number(p.sample)||null,margin:Number(p.margin)||null,
    registry:clean(p.registry,40),sourceUrl:/^https:\/\//i.test(String(p.sourceUrl||''))?String(p.sourceUrl):'',results
  };
}
function fallbackFor(office,uf){
  return office==='PRESIDENTE'?PRESIDENT_FALLBACK.map(p=>({...p,office:'PRESIDENTE',uf:'BR'})):[];
}
function mergePerInstitute(fresh,fallback){
  const out=[];
  for(const institute of ALLOWED_INSTITUTES){
    const current=fresh.find(p=>p.institute===institute)||fallback.find(p=>p.institute===institute);
    if(current)out.push(current);
  }
  return out;
}
async function searchLatest(office,uf){
  if(!process.env.OPENAI_API_KEY)throw new Error('OPENAI_NOT_CONFIGURED');
  const target=office==='GOVERNADOR'?`governador de ${uf}`:'Presidente da Republica';
  const today=new Intl.DateTimeFormat('pt-BR',{timeZone:'America/Sao_Paulo',dateStyle:'short'}).format(new Date());
  const prompt=`Hoje e ${today}. Encontre a pesquisa eleitoral MAIS RECENTE publicada por cada um destes institutos: Datafolha e Quaest, para ${target}, Eleicoes 2026 no Brasil. Use busca na web. Priorize pagina oficial do instituto, Folha/UOL para Datafolha e pagina oficial da Quaest. Confirme o numero de registro na Justica Eleitoral quando estiver disponivel. Nao misture cenarios nem segundo turno. O campo field deve ser SOMENTE o periodo de coleta no formato DD a DD/MM/AAAA ou DD/MM a DD/MM/AAAA. Retorne SOMENTE JSON no formato {"polls":[{"id":"...","institute":"Datafolha|Quaest","published":"DD/MM/AAAA","field":"18 a 20/08/2026","sample":2000,"margin":2,"registry":"BR-00000/2026","sourceUrl":"https://...","results":[["Nome","Partido",39]]}]}. Se nao houver pesquisa confiavel de um instituto para este cargo/UF, omita esse instituto. Nao invente percentuais, registro, datas ou amostra.`;
  const response=await fetch('https://api.openai.com/v1/responses',{
    method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${process.env.OPENAI_API_KEY}`},
    body:JSON.stringify({model:MODEL,input:[{role:'system',content:'Voce e um extrator factual de pesquisas eleitorais brasileiras. Use somente fontes encontradas na web e devolva JSON estrito. Nunca recomende voto.'},{role:'user',content:prompt}],tools:[{type:'web_search'}],max_output_tokens:1800,store:false})
  });
  const data=await response.json().catch(()=>({}));
  if(!response.ok)throw new Error(clean(data?.error?.message||`HTTP_${response.status}`));
  const parsed=parseJson(textFromResponse(data));
  return (Array.isArray(parsed.polls)?parsed.polls:[]).map(p=>normalizePoll(p,office,uf)).filter(Boolean);
}

export default async function handler(req,res){
  if(req.method!=='GET')return send(res,405,{ok:false,error:'METHOD_NOT_ALLOWED'},'no-store');
  const office=String(req.query?.office||'PRESIDENTE').toUpperCase()==='GOVERNADOR'?'GOVERNADOR':'PRESIDENTE';
  const uf=office==='GOVERNADOR'?clean(String(req.query?.uf||'MG').toUpperCase().replace(/[^A-Z]/g,''),2):'BR';
  const fetchedAt=new Date().toISOString();
  const fallback=fallbackFor(office,uf);
  try{
    const freshPolls=await searchLatest(office,uf);
    const polls=mergePerInstitute(freshPolls,fallback);
    const freshInstitutes=freshPolls.map(p=>p.institute);
    return send(res,200,{ok:true,fresh:freshPolls.length>0,office,uf,fetchedAt,polls,freshInstitutes,warning:freshPolls.length?'':'Nenhuma pesquisa nova confiavel encontrada; exibindo ultima carga valida.'});
  }catch(e){
    return send(res,200,{ok:true,fresh:false,office,uf,fetchedAt,polls:fallback,freshInstitutes:[],warning:'Atualizacao online indisponivel; exibindo ultima carga valida.',detail:clean(e?.message||e,160)});
  }
}

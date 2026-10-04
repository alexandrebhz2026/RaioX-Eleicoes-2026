const TSE = 'https://resultados.tse.jus.br';
const FALLBACK = { federal: '6257', estadual: '6259' };
const UF_ORDER = ['mg','sp','rj','ba','pr','rs','pe','ce','pa','sc','go','ma','pb','rn','es','al','pi','mt','ms','df','se','ro','to','ac','ap','rr','am'];
const CARGO_LABEL = { '1':'Presidente','3':'Governador','5':'Senador','6':'Deputado Federal','7':'Deputado Estadual','8':'Deputado Distrital' };
const fileCache = globalThis.__apuracaoSearchCache || (globalThis.__apuracaoSearchCache = new Map());
let codesCache = globalThis.__apuracaoCodesCache || null;

function norm(v='') {
  return String(v).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,' ').trim();
}
function num(v) { return Number(String(v ?? '0').replace(/\./g,'').replace(',','.')) || 0; }
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }

async function getCodes() {
  if (codesCache && Date.now() - codesCache.at < 600000) return codesCache.value;
  let value = { ...FALLBACK };
  try {
    const r = await fetch(TSE + '/oficial/comum/config/ele-c.json', { headers:{ accept:'application/json' } });
    if (r.ok) {
      const j = await r.json();
      for (const p of j.pl || []) {
        if (p.c !== 'ele2026') continue;
        for (const e of p.e || []) {
          const cargos = new Set((e.abr || []).flatMap(a => (a.cp || []).map(c => String(c.cd))));
          if (cargos.has('1')) value.federal = String(e.cd);
          if (cargos.has('3') || cargos.has('5') || cargos.has('6') || cargos.has('7') || cargos.has('8')) value.estadual = String(e.cd);
        }
      }
    }
  } catch {}
  codesCache = { at: Date.now(), value };
  globalThis.__apuracaoCodesCache = codesCache;
  return value;
}

function urlFor(ele,cargo,uf){
  const abr = cargo === '1' ? 'br' : uf;
  return `${TSE}/oficial/ele2026/${ele}/dados/${abr}/${abr}-c${cargo.padStart(4,'0')}-e${String(ele).padStart(6,'0')}-u.json`;
}

async function fetchJson(url){
  const hit = fileCache.get(url);
  if (hit && Date.now() - hit.at < 60000) return hit.data;
  try {
    const r = await fetch(url,{headers:{accept:'application/json'}});
    if (!r.ok) return null;
    const data = await r.json();
    fileCache.set(url,{at:Date.now(),data});
    if (fileCache.size > 180) fileCache.delete(fileCache.keys().next().value);
    return data;
  } catch { return null; }
}

function extract(data, ele, uf, cargo, qNorm, tokens){
  const rootCargo = data?.carg?.[0];
  if (!rootCargo) return [];
  const results = [];
  for (const agr of rootCargo.agr || []) {
    for (const par of agr.par || []) {
      for (const cand of par.cand || []) {
        const display = cand.nmu || cand.nm || '';
        const full = cand.nm || display;
        const party = par.sg || agr.com || '';
        const number = String(cand.n || '');
        const hay = norm([display,full,party,number].join(' '));
        const allTokens = tokens.every(t => hay.includes(t));
        if (!allTokens) continue;
        const d = norm(display), f = norm(full), p = norm(party);
        let score = 50;
        if (number === qNorm) score = 0;
        else if (d === qNorm || f === qNorm) score = 1;
        else if (d.startsWith(qNorm) || f.startsWith(qNorm)) score = 2;
        else if (d.includes(qNorm) || f.includes(qNorm)) score = 3;
        else if (p === qNorm) score = 5;
        else score = 10;
        results.push({
          score,
          sqcand: String(cand.sqcand || ''),
          numero: number,
          nome: display,
          nomeCompleto: full,
          partido: party,
          uf: uf.toUpperCase(),
          cargo: CARGO_LABEL[cargo] || cargo,
          cargoCodigo: cargo,
          votos: Number(cand.vap || 0),
          percentual: num(cand.pvap),
          status: cand.st || '',
          eleito: cand.e === 's',
          foto: `/api/tse?path=${encodeURIComponent(`/oficial/ele2026/${ele}/fotos/${uf}/${cand.sqcand}.jpeg`)}`
        });
      }
    }
  }
  return results;
}

export default async function handler(req,res){
  if (req.method !== 'GET') return res.status(405).json({error:'Method not allowed'});
  const rawQ = Array.isArray(req.query.q) ? req.query.q[0] : (req.query.q || '');
  const q = norm(rawQ);
  if (q.length < 3) return res.status(400).json({error:'Digite pelo menos 3 caracteres.'});
  const ufFilterRaw = Array.isArray(req.query.uf) ? req.query.uf[0] : (req.query.uf || '');
  const ufFilter = norm(ufFilterRaw);
  const cargoFilterRaw = Array.isArray(req.query.cargo) ? req.query.cargo[0] : (req.query.cargo || '');
  const cargoFilter = String(cargoFilterRaw || '');
  const tokens = q.split(' ').filter(Boolean);
  const numeric = /^\d+$/.test(q);
  const codes = await getCodes();
  let results = [];
  let scanned = 0;
  let partial = false;

  if ((!cargoFilter || cargoFilter === '1') && (!ufFilter || ufFilter === 'br')) {
    const d = await fetchJson(urlFor(codes.federal,'1','br'));
    scanned++;
    if (d) results.push(...extract(d,codes.federal,'br','1',q,tokens));
  }

  let cargos;
  if (cargoFilter && cargoFilter !== '1') cargos = [cargoFilter];
  else if (numeric && q.length === 4) cargos = ['6'];
  else if (numeric && q.length === 5) cargos = ['7','8'];
  else cargos = ['3','5','6','7','8'];

  const ufs = ufFilter && ufFilter !== 'br' ? [ufFilter] : UF_ORDER;
  const validUfs = ufs.filter(u => UF_ORDER.includes(u));

  for (let i=0; i<validUfs.length; i+=3) {
    const batch = validUfs.slice(i,i+3);
    const batchResults = await Promise.all(batch.map(async uf => {
      const cs = cargos.filter(c => !(c === '8' && uf !== 'df') && !(c === '7' && uf === 'df'));
      const files = await Promise.all(cs.map(async cargo => {
        const data = await fetchJson(urlFor(codes.estadual,cargo,uf));
        scanned++;
        return data ? extract(data,codes.estadual,uf,cargo,q,tokens) : [];
      }));
      return files.flat();
    }));
    results.push(...batchResults.flat());
    if (results.length >= 80) break;
    if (i + 3 < validUfs.length) await sleep(120);
  }

  results.sort((a,b) => a.score-b.score || b.votos-a.votos || a.nome.localeCompare(b.nome,'pt-BR'));
  results = results.slice(0,80).map(({score,...r})=>r);

  res.setHeader('Cache-Control','public, s-maxage=60, stale-while-revalidate=300');
  res.setHeader('Access-Control-Allow-Origin','*');
  return res.status(200).json({
    query: rawQ,
    count: results.length,
    scanned,
    partial,
    updatedAt: new Date().toISOString(),
    results
  });
}
module.exports = async function handler(req, res) {
  try {
    const url = new URL(req.url, 'https://local.invalid');
    const cargo = String(url.searchParams.get('cargo') || '').toLowerCase();
    const numero = String(url.searchParams.get('numero') || '').replace(/\D/g, '');
    const allowed = new Set(['federal','senador','governador','presidente']);
    if (!allowed.has(cargo) || !numero) {
      res.statusCode = 400;
      res.setHeader('content-type','application/json; charset=utf-8');
      res.end(JSON.stringify({ok:false,error:'Parametros invalidos'}));
      return;
    }
    const upstream = new URL('https://colinha-ana-paula-siqueira.vercel.app/api/candidato');
    upstream.searchParams.set('cargo', cargo);
    upstream.searchParams.set('numero', numero);
    const response = await fetch(upstream, { headers: { 'accept': 'application/json' }, cache: 'no-store' });
    const body = await response.text();
    res.statusCode = response.status;
    res.setHeader('content-type', response.headers.get('content-type') || 'application/json; charset=utf-8');
    res.setHeader('cache-control','no-store, max-age=0');
    res.end(body);
  } catch (error) {
    res.statusCode = 502;
    res.setHeader('content-type','application/json; charset=utf-8');
    res.end(JSON.stringify({ok:false,error:'Falha temporaria na consulta'}));
  }
};
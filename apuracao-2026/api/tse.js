export default async function handler(req, res) {
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.setHeader('Allow', 'GET, HEAD');
    return res.status(405).send('Method Not Allowed');
  }

  const raw = Array.isArray(req.query.path) ? req.query.path[0] : req.query.path;
  if (!raw || typeof raw !== 'string') return res.status(400).send('Missing path');

  let path;
  try { path = decodeURIComponent(raw); } catch { path = raw; }
  if (!path.startsWith('/oficial/') || path.includes('..')) return res.status(403).send('Forbidden');

  const allowed = /^\/oficial\/(comum\/config\/ele-c\.json|ele2026\/\d{3,6}\/(dados|fotos)\/[a-z]{2}\/[A-Za-z0-9_.-]+\.(json|jpeg|jpg))$/;
  if (!allowed.test(path)) return res.status(403).send('Forbidden');

  try {
    const upstream = await fetch('https://resultados.tse.jus.br' + path, {
      headers: { 'User-Agent': 'Apuracao-2026/1.0', 'Accept': path.endsWith('.json') ? 'application/json' : 'image/jpeg' }
    });
    const body = Buffer.from(await upstream.arrayBuffer());
    const isJson = path.endsWith('.json');
    res.status(upstream.status);
    res.setHeader('Content-Type', isJson ? 'application/json; charset=utf-8' : (upstream.headers.get('content-type') || 'image/jpeg'));
    res.setHeader('Cache-Control', isJson ? 'public, s-maxage=15, stale-while-revalidate=30' : 'public, s-maxage=86400');
    res.setHeader('Access-Control-Allow-Origin', '*');
    return res.send(body);
  } catch (err) {
    return res.status(502).json({ error: 'TSE indisponivel temporariamente' });
  }
}
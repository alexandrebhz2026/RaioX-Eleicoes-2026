const http = require('http');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT || 3000;
const indexPath = path.join(__dirname, 'index.html');
const indexHtml = fs.readFileSync(indexPath);

function json(res, status, body) {
  res.statusCode = status;
  res.setHeader('content-type', 'application/json; charset=utf-8');
  res.setHeader('cache-control', 'no-store, max-age=0');
  res.end(JSON.stringify(body));
}

async function proxyPhoto(url, res) {
  const sq = String(url.searchParams.get('sq') || '').replace(/\D/g, '');
  const uf = String(url.searchParams.get('uf') || 'MG').toUpperCase().replace(/[^A-Z]/g, '');
  if (!sq || sq.length > 30 || !/^[A-Z]{2}$/.test(uf)) {
    return json(res, 400, { ok: false, error: 'Parametros invalidos' });
  }

  const sources = [
    'https://divulgacandcontas.tse.jus.br/divulga/rest/arquivo/img/20322002026/' + encodeURIComponent(sq) + '/' + encodeURIComponent(uf)
  ];

  for (const source of sources) {
    try {
      const response = await fetch(source, {
        headers: {
          accept: 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
          'user-agent': 'Mozilla/5.0'
        },
        cache: 'no-store'
      });
      if (!response.ok) continue;
      const body = Buffer.from(await response.arrayBuffer());
      if (!body.length) continue;

      res.statusCode = 200;
      res.setHeader('content-type', response.headers.get('content-type') || 'image/png');
      res.setHeader('cache-control', 'public, max-age=3600, stale-while-revalidate=86400');
      res.setHeader('access-control-allow-origin', '*');
      res.setHeader('x-content-type-options', 'nosniff');
      return res.end(body);
    } catch (_) {}
  }

  return json(res, 502, { ok: false, error: 'Foto indisponivel' });
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');

    if (url.pathname === '/health') {
      return json(res, 200, { ok: true });
    }

    if (url.pathname === '/api/foto') {
      return await proxyPhoto(url, res);
    }

    if (url.pathname === '/api/candidato') {
      const cargo = String(url.searchParams.get('cargo') || '').toLowerCase();
      const numero = String(url.searchParams.get('numero') || '').replace(/\D/g, '');
      const allowed = new Set(['federal','senador','governador','presidente']);
      if (!allowed.has(cargo) || !numero) {
        return json(res, 400, { ok: false, error: 'Parametros invalidos' });
      }

      const upstream = new URL('https://colinha-ana-paula-siqueira.vercel.app/api/candidato');
      upstream.searchParams.set('cargo', cargo);
      upstream.searchParams.set('numero', numero);
      const response = await fetch(upstream, {
        headers: { accept: 'application/json' },
        cache: 'no-store'
      });
      const body = await response.text();
      res.statusCode = response.status;
      res.setHeader('content-type', response.headers.get('content-type') || 'application/json; charset=utf-8');
      res.setHeader('cache-control', 'no-store, max-age=0');
      res.setHeader('access-control-allow-origin', '*');
      return res.end(body);
    }

    if (url.pathname === '/' || url.pathname === '/index.html') {
      res.statusCode = 200;
      res.setHeader('content-type', 'text/html; charset=utf-8');
      res.setHeader('cache-control', 'no-store, max-age=0');
      return res.end(indexHtml);
    }

    res.statusCode = 404;
    res.setHeader('content-type', 'text/plain; charset=utf-8');
    res.end('Not found');
  } catch (error) {
    console.error(error);
    json(res, 500, { ok: false, error: 'Falha interna' });
  }
});

server.listen(port, '0.0.0.0', () => {
  console.log('Colinha Ana Paula listening on port', port);
});

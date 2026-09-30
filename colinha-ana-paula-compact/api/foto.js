module.exports = async function handler(req, res) {
  try {
    const url = new URL(req.url, 'https://local.invalid');
    const sq = String(url.searchParams.get('sq') || '').replace(/\D/g, '');
    const uf = String(url.searchParams.get('uf') || 'MG').toUpperCase().replace(/[^A-Z]/g, '');

    if (!sq || sq.length > 30 || !/^[A-Z]{2}$/.test(uf)) {
      res.statusCode = 400;
      res.setHeader('content-type', 'application/json; charset=utf-8');
      res.end(JSON.stringify({ ok: false, error: 'Parametros invalidos' }));
      return;
    }

    const sources = [
      'https://meuvoto.org.br/og/' + encodeURIComponent(sq) + '.png?v=20260916',
      'https://divulgacandcontas.tse.jus.br/divulga/rest/arquivo/img/20322002026/' + encodeURIComponent(sq) + '/' + encodeURIComponent(uf)
    ];

    let lastStatus = 502;
    for (const source of sources) {
      try {
        const response = await fetch(source, {
          headers: {
            accept: 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0'
          },
          cache: 'no-store'
        });

        if (!response.ok) {
          lastStatus = response.status || 502;
          continue;
        }

        const body = Buffer.from(await response.arrayBuffer());
        if (!body.length) continue;

        res.statusCode = 200;
        res.setHeader('content-type', response.headers.get('content-type') || 'image/png');
        res.setHeader('cache-control', 'public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800');
        res.setHeader('access-control-allow-origin', '*');
        res.setHeader('x-content-type-options', 'nosniff');
        res.end(body);
        return;
      } catch (_) {}
    }

    res.statusCode = lastStatus === 404 ? 404 : 502;
    res.setHeader('content-type', 'application/json; charset=utf-8');
    res.setHeader('cache-control', 'no-store');
    res.end(JSON.stringify({ ok: false, error: 'Foto indisponivel' }));
  } catch (error) {
    res.statusCode = 502;
    res.setHeader('content-type', 'application/json; charset=utf-8');
    res.setHeader('cache-control', 'no-store');
    res.end(JSON.stringify({ ok: false, error: 'Falha temporaria na foto' }));
  }
};

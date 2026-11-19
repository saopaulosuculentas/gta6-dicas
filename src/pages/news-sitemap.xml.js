// Mapa de notícias do Google News: só as dicas descobertas nas últimas 48 horas,
// contadas a partir do momento do build (o Google ignora o que for mais velho que 2 dias).
// Sem dica nova nesse intervalo, sai um urlset vazio, que continua válido.
import { SITE } from '../../site.config.mjs';
import { todasDicas, linkDica, langDe } from '../lib/util';

const JANELA_MS = 48 * 60 * 60 * 1000;

const xml = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');

// ISO 8601 com fuso (UTC, "Z"), sem os milissegundos
const iso = (d) => d.toISOString().replace(/\.\d{3}Z$/, 'Z');

export async function GET(context) {
  const agora = Date.now();
  const dicas = [...(await todasDicas('pt')), ...(await todasDicas('en'))]
    .filter((d) => !d.id.startsWith('exemplos/'))
    .filter((d) => {
      const t = d.data.descoberto_em.getTime();
      return t <= agora && agora - t <= JANELA_MS;
    })
    .sort((a, b) => b.data.descoberto_em.getTime() - a.data.descoberto_em.getTime());

  const itens = dicas
    .map((d) => {
      const loc = new URL(linkDica(d), context.site).href;
      return `  <url>
    <loc>${xml(loc)}</loc>
    <news:news>
      <news:publication>
        <news:name>${xml(SITE.nome)}</news:name>
        <news:language>${langDe(d)}</news:language>
      </news:publication>
      <news:publication_date>${iso(d.data.descoberto_em)}</news:publication_date>
      <news:title>${xml(d.data.titulo)}</news:title>
    </news:news>
  </url>`;
    })
    .join('\n');

  const corpo = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
${itens ? itens + '\n' : ''}</urlset>
`;
  return new Response(corpo, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}

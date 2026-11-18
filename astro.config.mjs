import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readdirSync, readFileSync } from 'node:fs';
import { SITE, temDominio } from './site.config.mjs';

// Data da última atualização de cada dica, para o mapa do site (lastmod).
// O Google usa essa data para saber quais páginas mudaram e voltar a ler primeiro.
const pastaDicas = new URL('./src/content/dicas/', import.meta.url);
const atualizacoes = {};
const categoriaDe = {};
for (const arq of readdirSync(pastaDicas)) {
  if (!arq.endsWith('.md')) continue;
  const texto = readFileSync(new URL(arq, pastaDicas), 'utf8');
  const data = texto.match(/^atualizado_em:\s*"?([^"\n]+)"?/m)?.[1];
  const cat = texto.match(/^categoria:\s*(\S+)/m)?.[1];
  const slug = arq.replace(/\.md$/, '');
  if (data) atualizacoes[slug] = new Date(data);
  if (cat) categoriaDe[slug] = cat;
}
const maisRecente = (lista) => (lista.length ? new Date(Math.max(...lista.map((d) => d.getTime()))) : undefined);
const geral = maisRecente(Object.values(atualizacoes));
const porCategoria = {};
for (const [slug, data] of Object.entries(atualizacoes)) {
  (porCategoria[categoriaDe[slug]] ??= []).push(data);
}

export default defineConfig({
  site: temDominio ? SITE.dominio : SITE.provisorio.site,
  base: temDominio ? '/' : SITE.provisorio.base,
  trailingSlash: 'always',
  integrations: [
    sitemap({
      filter: (url) => !url.includes('/dica/exemplo'),
      serialize(item) {
        const caminho = new URL(item.url).pathname.replace(SITE.provisorio.base, '');
        const dica = caminho.match(/\/dica\/([^/]+)\//)?.[1];
        const categoria = caminho.match(/^\/([^/]+)\/$/)?.[1];
        if (dica && atualizacoes[dica]) {
          item.lastmod = atualizacoes[dica].toISOString();
          item.priority = 0.8;
          item.changefreq = 'daily';
        } else if (categoria && porCategoria[categoria]) {
          item.lastmod = maisRecente(porCategoria[categoria]).toISOString();
          item.priority = 0.9;
          item.changefreq = 'hourly';
        } else if (caminho === '/' || caminho === '') {
          if (geral) item.lastmod = geral.toISOString();
          item.priority = 1.0;
          item.changefreq = 'hourly';
        } else if (caminho === '/novidades/') {
          if (geral) item.lastmod = geral.toISOString();
          item.changefreq = 'hourly';
        }
        return item;
      },
    }),
  ],
  server: { port: 4326 },
});

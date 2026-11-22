// Monta o arquivo que a busca lê, um por língua, a cada publicação.
import { render } from 'astro:content';
import { u, todasDicas, linkDica, slugDe, type Dica } from './util';
import populares from '../../dados/mais-buscados.json';
import { nomeCategoria, type Categoria, type Lang } from './i18n';
import type { Item } from './busca';

const semMarcacao = (s: string) =>
  s
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/<[^>]+>/g, ' ')
    .replace(/^\s*(?:>|[-*+]|\d+\.)\s+/, '')
    .replace(/^\s*\|\s*|\s*\|\s*$/g, '')
    .replace(/\s*\|\s*/g, ' · ')
    .replace(/\*\*|__|`|~~/g, '')
    .replace(/(^|\W)[*_](\S[^*_]*)[*_](?=\W|$)/g, '$1$2')
    .replace(/\s+/g, ' ')
    .trim();

/** Divide o texto pelos subtítulos, com a mesma âncora que a página usa. */
async function partes(dica: Dica): Promise<Item['p']> {
  const { headings } = await render(dica);
  const d = dica.data;
  const saida: Item['p'] = [{ l: [] }];
  let n = 0;
  for (const bruta of (dica.body ?? '').split(/\r?\n/)) {
    if (/^\s{0,3}#{1,6}\s/.test(bruta)) {
      const titulo = headings[n++];
      saida.push({ a: titulo?.slug, h: titulo?.text, l: [] });
    } else if (bruta.trim() && !/^[\s|:-]+$/.test(bruta)) {
      saida[saida.length - 1].l.push(semMarcacao(bruta));
    }
  }
  const extras = [
    d.efeito,
    d.codigo?.telefone,
    d.codigo?.texto,
    ...d.perguntas.map((q) => `${q.p} ${q.r}`),
    ...d.imagens.map((i) => i.legenda),
  ].filter((x): x is string => Boolean(x));
  if (extras.length) saida.push({ l: extras });
  return saida.filter((p) => p.h || p.l.length);
}

export async function indiceBusca(lang: Lang): Promise<Response> {
  const respostas = Object.entries(populares[lang].respostas as Record<string, string>);
  const itens: Item[] = await Promise.all(
    (await todasDicas(lang)).map(async (dica) => {
      const d = dica.data;
      const fixas = respostas.filter(([, slug]) => slug === slugDe(dica)).map(([termo]) => termo);
      return {
        t: d.titulo,
        r: d.resumo,
        c: nomeCategoria(d.categoria as Categoria, lang),
        u: linkDica(dica),
        i: d.imagens[0] && u(`/img/${d.imagens[0].arquivo}`),
        ok: d.status === 'confirmado',
        b: fixas.length ? fixas : undefined,
        p: await partes(dica),
      };
    }),
  );
  return new Response(JSON.stringify(itens), { headers: { 'Content-Type': 'application/json; charset=utf-8' } });
}

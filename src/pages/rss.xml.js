import rss from '@astrojs/rss';
import { SITE } from '../../site.config.mjs';
import { todasDicas, linkDica } from '../lib/util';

export async function GET(context) {
  const dicas = await todasDicas();
  return rss({
    title: SITE.nome,
    description: SITE.descricao,
    site: context.site,
    items: dicas.slice(0, 50).map((d) => ({
      title: d.data.titulo,
      description: d.data.resumo,
      pubDate: d.data.atualizado_em,
      link: linkDica(d),
    })),
    customData: '<language>pt-BR</language>',
  });
}

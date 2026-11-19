import rss from '@astrojs/rss';
import { SITE } from '../../../site.config.mjs';
import { todasDicas, linkDica } from '../../lib/util';

export async function GET(context) {
  const dicas = await todasDicas('en');
  return rss({
    title: `${SITE.nome} (English)`,
    description: 'GTA 6 cheats, easter eggs, secrets and money tips for PS5 and Xbox, checked against gameplay videos before going live.',
    site: context.site,
    items: dicas.slice(0, 50).map((d) => ({
      title: d.data.titulo,
      description: d.data.resumo,
      pubDate: d.data.atualizado_em,
      link: linkDica(d),
    })),
    customData: '<language>en</language>',
  });
}

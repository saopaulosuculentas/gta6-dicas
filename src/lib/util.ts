import { getCollection, type CollectionEntry } from 'astro:content';
import estado from '../../dados/estado.json';
import { prefixo, pastaDica, type Lang } from './i18n';

export type Dica = CollectionEntry<'dicas'> | CollectionEntry<'dicasEn'>;

const base = import.meta.env.BASE_URL.replace(/\/$/, '');
/** Monta um link interno respeitando o endereço provisório (/gta6-dicas) ou o domínio próprio (/). */
export const u = (caminho: string) => `${base}${caminho.startsWith('/') ? caminho : '/' + caminho}`;

const fuso = 'America/Sao_Paulo';
const formatos = {
  pt: {
    dataHora: new Intl.DateTimeFormat('pt-BR', { timeZone: fuso, day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }),
    dataLonga: new Intl.DateTimeFormat('pt-BR', { timeZone: fuso, day: 'numeric', month: 'long', year: 'numeric' }),
    hora: new Intl.DateTimeFormat('pt-BR', { timeZone: fuso, hour: '2-digit', minute: '2-digit' }),
  },
  en: {
    dataHora: new Intl.DateTimeFormat('en-US', { timeZone: fuso, month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }),
    dataLonga: new Intl.DateTimeFormat('en-US', { timeZone: fuso, day: 'numeric', month: 'long', year: 'numeric' }),
    hora: new Intl.DateTimeFormat('en-US', { timeZone: fuso, hour: 'numeric', minute: '2-digit' }),
  },
};

/** 18/11 às 21:04 · Nov 18, 9:04 PM (horário de Brasília) */
export const dataHora = (d: Date, lang: Lang = 'pt') =>
  lang === 'en' ? `${formatos.en.dataHora.format(d)} BRT` : formatos.pt.dataHora.format(d).replace(',', ' às');
/** 18 de novembro de 2026 · November 18, 2026 */
export const dataLonga = (d: Date, lang: Lang = 'pt') => formatos[lang].dataLonga.format(d);
export const hora = (d: Date, lang: Lang = 'pt') => formatos[lang].hora.format(d);
/** Dia e mês curtos para a lista do plantão: 18/11 · Nov 18 */
export const diaCurto = (d: Date, lang: Lang = 'pt') =>
  lang === 'en'
    ? new Intl.DateTimeFormat('en-US', { timeZone: fuso, month: 'short', day: 'numeric' }).format(d)
    : formatos.pt.dataHora.format(d).slice(0, 5);

export async function todasDicas(lang: Lang = 'pt'): Promise<Dica[]> {
  const dicas: Dica[] = lang === 'en' ? await getCollection('dicasEn') : await getCollection('dicas');
  return dicas.sort((a, b) => b.data.atualizado_em.getTime() - a.data.atualizado_em.getTime());
}

export const canais = (d: Dica) => [...new Set(d.data.fontes.map((f) => f.canal.trim()))];

/** "1:02:03" ou "12:34" em segundos */
export function segundos(minuto?: string): number {
  if (!minuto) return 0;
  return minuto.split(':').reduce((t, p) => t * 60 + Number(p), 0);
}

export function idYoutube(url: string): string | null {
  const m = url.match(/(?:v=|youtu\.be\/|\/live\/|\/shorts\/|\/embed\/)([\w-]{11})/);
  return m ? m[1] : null;
}

/** Link do vídeo já no minuto da dica */
export function linkNoMinuto(url: string, minuto?: string): string {
  const id = idYoutube(url);
  const s = segundos(minuto);
  if (!id) return url;
  return `https://www.youtube.com/watch?v=${id}${s ? `&t=${s}s` : ''}`;
}

export const ultimaRodada = estado.ultima_rodada ? new Date(estado.ultima_rodada) : null;
export const videosLidos: number = estado.videos_lidos ?? 0;

/** Idioma de uma dica: as em inglês vêm da coleção dicasEn. */
export const langDe = (d: Dica): Lang => (d.collection === 'dicasEn' ? 'en' : 'pt');
/** Endereço da dica (as de exemplo ficam numa subpasta, que não entra no endereço). */
export const slugDe = (d: Dica) => d.id.replace(/^exemplos\//, '');
export const linkDica = (d: Dica) => u(`${prefixo(langDe(d))}/${pastaDica(langDe(d))}/${slugDe(d)}/`);
/** Endereço de uma dica pelo nome do arquivo, na língua pedida. */
export const linkSlug = (slug: string, lang: Lang) => u(`${prefixo(lang)}/${pastaDica(lang)}/${slug}/`);
/** Idioma do endereço atual. */
export const langDaUrl = (caminho: string): Lang => (caminho.startsWith(u('/en/')) || caminho === u('/en') ? 'en' : 'pt');

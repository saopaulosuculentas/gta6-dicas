import { getCollection, type CollectionEntry } from 'astro:content';
import estado from '../../dados/estado.json';

export type Dica = CollectionEntry<'dicas'>;

const base = import.meta.env.BASE_URL.replace(/\/$/, '');
/** Monta um link interno respeitando o endereço provisório (/gta6-dicas) ou o domínio próprio (/). */
export const u = (caminho: string) => `${base}${caminho.startsWith('/') ? caminho : '/' + caminho}`;

const fuso = 'America/Sao_Paulo';
const fDataHora = new Intl.DateTimeFormat('pt-BR', { timeZone: fuso, day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
const fDataLonga = new Intl.DateTimeFormat('pt-BR', { timeZone: fuso, day: 'numeric', month: 'long', year: 'numeric' });
const fHora = new Intl.DateTimeFormat('pt-BR', { timeZone: fuso, hour: '2-digit', minute: '2-digit' });

/** 18/11, 21:04 */
export const dataHora = (d: Date) => fDataHora.format(d).replace(',', ' às');
/** 18 de novembro de 2026 */
export const dataLonga = (d: Date) => fDataLonga.format(d);
export const hora = (d: Date) => fHora.format(d);

export async function todasDicas(): Promise<Dica[]> {
  const dicas = await getCollection('dicas');
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

/** Endereço da dica (as de exemplo ficam numa subpasta, que não entra no endereço). */
export const slugDe = (d: Dica) => d.id.replace(/^exemplos\//, '');
export const linkDica = (d: Dica) => u(`/dica/${slugDe(d)}/`);

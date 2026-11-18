import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Botões aceitos em cada console. O agente só pode usar estes nomes.
export const BOTOES_PS5 = ['cima', 'baixo', 'esquerda', 'direita', 'x', 'circulo', 'quadrado', 'triangulo', 'l1', 'l2', 'r1', 'r2', 'l3', 'r3'] as const;
export const BOTOES_XBOX = ['cima', 'baixo', 'esquerda', 'direita', 'a', 'b', 'x', 'y', 'lb', 'lt', 'rb', 'rt', 'ls', 'rs'] as const;

const fonte = z.object({
  // youtube = vídeo ou live; oficial = Rockstar (site, suporte, canal oficial); site = imprensa
  tipo: z.enum(['youtube', 'oficial', 'site']).default('youtube'),
  canal: z.string().min(2),
  url: z.string().url(),
  titulo: z.string().optional(),
  // minuto do vídeo em que a dica aparece: m:ss ou h:mm:ss
  minuto: z.string().regex(/^(\d{1,2}:)?\d{1,2}:\d{2}$/).optional(),
  data: z.coerce.date(),
});

const dicas = defineCollection({
  // As dicas da pasta exemplos/ só aparecem no modo de teste (npm run dev). Nunca vão ao ar.
  loader: glob({ pattern: import.meta.env.DEV ? '**/*.md' : ['**/*.md', '!exemplos/**'], base: './src/content/dicas' }),
  schema: z
    .object({
      titulo: z.string().min(10).max(95),
      resumo: z.string().min(40).max(220),
      categoria: z.enum(['codigos', 'easter-eggs', 'segredos-e-locais', 'dinheiro', 'dicas']),
      status: z.enum(['confirmado', 'em-verificacao']),
      plataformas: z.array(z.enum(['ps5', 'xbox'])).min(1).default(['ps5', 'xbox']),
      codigo: z
        .object({
          ps5: z.array(z.enum(BOTOES_PS5)).min(2).optional(),
          xbox: z.array(z.enum(BOTOES_XBOX)).min(2).optional(),
          telefone: z.string().optional(),
          texto: z.string().optional(),
        })
        .optional(),
      efeito: z.string().max(140).optional(),
      fontes: z.array(fonte).min(1),
      descoberto_em: z.coerce.date(),
      atualizado_em: z.coerce.date(),
      historico: z.array(z.object({ data: z.coerce.date(), nota: z.string() })).default([]),
      destaque: z.boolean().default(false),
    })
    .refine(
      (d) => {
        if (d.status !== 'confirmado') return true;
        const oficial = d.fontes.some((f) => f.tipo === 'oficial');
        const canais = new Set(d.fontes.map((f) => f.canal.trim().toLowerCase()));
        return oficial || canais.size >= 2;
      },
      { message: 'status "confirmado" exige 2 canais diferentes nas fontes (ou 1 fonte oficial)' },
    )
    .refine((d) => d.categoria !== 'codigos' || d.codigo, {
      message: 'dica da categoria "codigos" precisa do campo "codigo"',
    }),
});

export const collections = { dicas };

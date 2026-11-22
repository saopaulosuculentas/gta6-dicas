// Motor da busca. Roda no navegador de quem visita: o que a pessoa digita não sai do aparelho.

export type Item = {
  t: string; // título
  r: string; // resumo
  c: string; // seção
  u: string; // endereço
  i?: string; // imagem pequena
  ok: boolean; // confirmada
  b?: string[]; // buscas em que esta página é a resposta certa
  p: { a?: string; h?: string; l: string[] }[]; // partes do texto: âncora, subtítulo e linhas
};

/** Uma página achada e, quando ajuda, o trecho exato em que está a resposta. */
export type Achado = { item: Item; trecho?: { texto: string; titulo?: string; ancora?: string } };
export type Resultado = {
  achados: Achado[];
  parcial: boolean; // nenhuma página tinha todas as palavras
  correcao?: string; // pergunta com a grafia corrigida
  marcar: string[]; // palavras para destacar
};

export const normalizar = (s: string) =>
  s
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/['’]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();

const lista = (s: string) => new Set(s.split(' '));

// Palavras que aparecem em quase toda pergunta e não ajudam a achar a página
const IGNORAR = {
  pt: lista('gta gta6 vi 6 o a os as um uma de do da dos das no na nos nas em e ou para pra por com que qual quais quero queria preciso me eu como onde fica ficam tem ta esta achar encontrar acho pego pegar localizacao jogo'),
  en: lista('gta gta6 vi 6 the a an of in on at to for with and or is are i me my do does can how where wheres what which find get location game want need'),
};

// Outros jeitos de escrever a mesma coisa
const GRUPOS = [
  'dinheiro grana money cash',
  'codigo macete cheat trapaca',
  'arma armamento weapon gun',
  'fuzil rifle',
  'escopeta espingarda shotgun',
  'carro veiculo car vehicle',
  'moto motocicleta motorcycle',
  'barco lancha boat',
  'aviao plane',
  'segredo secreto escondido secret hidden',
  'cofre safe',
  'senha password',
  'policia procurado police wanted',
  'final ending',
  'lendaria unica rara legendary unique rare',
  'colecionavel collectible',
  'missao mission',
  'ruido barulho noise',
  'registrar registro register registration',
  'pescar pesca fish fishing',
].map((g) => g.split(' '));

/** Deixa singular e plural iguais: armas = arma, missoes = missao, colecionaveis = colecionavel. */
export function raiz(p: string): string {
  if (p.length < 4) return p;
  if (p.endsWith('oes')) return p.slice(0, -3) + 'ao';
  if (p.endsWith('veis')) return p.slice(0, -4) + 'vel';
  if (p.endsWith('ais')) return p.slice(0, -3) + 'al';
  return p.endsWith('s') && !p.endsWith('ss') ? p.slice(0, -1) : p;
}

/** Quantas letras separam duas palavras (troca de vizinhas conta 1). Para cedo quando passa do limite. */
function distancia(a: string, b: string, limite: number): number {
  if (Math.abs(a.length - b.length) > limite) return limite + 1;
  let antes: number[] = [];
  let linha = Array.from({ length: b.length + 1 }, (_, i) => i);
  for (let i = 1; i <= a.length; i++) {
    const nova = [i];
    for (let j = 1; j <= b.length; j++) {
      let v = Math.min(linha[j] + 1, nova[j - 1] + 1, linha[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) v = Math.min(v, antes[j - 2] + 1);
      nova.push(v);
    }
    if (Math.min(...nova) > limite) return limite + 1;
    antes = linha;
    linha = nova;
  }
  return linha[b.length];
}

/** A mesma pergunta escrita de jeitos diferentes vira a mesma assinatura: "códigos e macetes" = "macete". */
function assinatura(palavras: string[]): string {
  const iguais = palavras.map((p) => {
    const r = raiz(p);
    return GRUPOS.find((g) => g.some((x) => raiz(x) === r))?.[0] ?? r;
  });
  return [...new Set(iguais)].sort().join(' ');
}

const palavrasDe = (s: string) => new Set(normalizar(s).split(' ').map(raiz));

/** Corta a linha em volta da primeira palavra achada. */
function recortar(linha: string, bate: (p: string) => boolean): string {
  const LIMITE = 170;
  if (linha.length <= LIMITE) return linha;
  let pos = 0;
  for (const m of linha.matchAll(/[\p{L}\p{N}]+/gu)) {
    if (bate(raiz(normalizar(m[0])))) {
      pos = m.index;
      break;
    }
  }
  let ini = Math.max(0, Math.min(pos - 50, linha.length - LIMITE));
  if (ini) ini = linha.indexOf(' ', ini) + 1;
  let fim = Math.min(linha.length, ini + LIMITE);
  if (fim < linha.length) fim = Math.max(ini + 1, linha.lastIndexOf(' ', fim));
  return `${ini ? '…' : ''}${linha.slice(ini, fim).trim()}${fim < linha.length ? '…' : ''}`;
}

export function criarBusca(itens: Item[], lang: 'pt' | 'en') {
  const paginas = itens.map((item) => ({
    item,
    titulo: normalizar(item.t),
    fixas: (item.b ?? []).map((b) => assinatura(normalizar(b).split(' ').filter((p) => !IGNORAR[lang].has(p)))),
    campos: [
      { peso: 12, palavras: palavrasDe(item.t) },
      { peso: 5, palavras: palavrasDe(item.r) },
      { peso: 4, palavras: palavrasDe(item.c) },
      { peso: 3, palavras: palavrasDe(item.p.map((p) => p.h ?? '').join(' ')) },
      { peso: 1, palavras: palavrasDe(item.p.flatMap((p) => p.l).join(' ')) },
    ],
  }));

  const frequencia = new Map<string, number>();
  for (const p of paginas) for (const c of p.campos) for (const w of c.palavras) frequencia.set(w, (frequencia.get(w) ?? 0) + c.peso);
  const vocabulario = [...frequencia.keys()];

  /** Devolve a palavra corrigida como ela aparece no site, com acento. */
  function comAcento(r: string): string {
    for (const item of itens) {
      for (const texto of [item.t, item.r, ...item.p.flatMap((p) => [p.h ?? '', ...p.l])]) {
        const achada = texto.match(/[\p{L}\p{N}]+/gu)?.find((w) => raiz(normalizar(w)) === r);
        if (achada) return achada.toLowerCase();
      }
    }
    return r;
  }

  /** Acha a grafia mais parecida quando a palavra não existe no site. */
  function corrigir(termo: string): string | undefined {
    if (termo.length < 4 || /\d/.test(termo) || GRUPOS.some((g) => g.some((p) => raiz(p) === termo))) return;
    if (vocabulario.some((w) => w.startsWith(termo))) return;
    let melhor: string | undefined;
    let menor = termo.length >= 6 ? 2 : 1;
    // entre duas parecidas, fica a que não perde letra (parot = parrot, não part) e depois a mais usada no site
    const nota = (w: string) => (w.length >= termo.length ? 1e6 : 0) + (w[0] === termo[0] ? 1e6 : 0) + frequencia.get(w)!;
    for (const w of vocabulario) {
      const d = distancia(termo, w, menor);
      if (d < menor || (d === menor && (!melhor || nota(w) > nota(melhor)))) {
        melhor = w;
        menor = d;
      }
    }
    return melhor;
  }

  return function procurar(pergunta: string): Resultado {
    const vazio = { achados: [], parcial: false, marcar: [] };
    const limpa = normalizar(pergunta.slice(0, 80));
    if (limpa.length < 2) return vazio;

    const digitadas = limpa.split(' ');
    const uteis = digitadas.filter((p) => !IGNORAR[lang].has(p));
    const usadas = [...new Set(uteis.length ? uteis : digitadas)];
    const trocas = new Map<string, string>();
    const corrigidas: string[] = [];
    const termos = usadas.map((palavra) => {
      let termo = raiz(palavra);
      const certa = corrigir(termo);
      if (certa) {
        trocas.set(palavra, comAcento(certa));
        termo = certa;
      }
      corrigidas.push(termo);
      const iguais = GRUPOS.find((g) => g.some((p) => raiz(p) === termo))?.map(raiz).filter((p) => p !== termo) ?? [];
      return { termo, iguais };
    });

    const pedida = assinatura(corrigidas);
    const pontuadas = paginas.map((pagina) => {
      let pontos = 0;
      let cobertos = 0;
      let noTopo = 0; // quantos termos já aparecem no título ou no resumo
      for (const { termo, iguais } of termos) {
        let melhor = 0;
        pagina.campos.forEach(({ peso, palavras }, n) => {
          let valor = 0;
          if (palavras.has(termo)) valor = peso;
          else if (iguais.some((p) => palavras.has(p))) valor = peso * 0.75;
          else if (termo.length >= 3) {
            for (const w of palavras) {
              if (w.startsWith(termo)) {
                valor = peso * 0.6;
                break;
              }
            }
          }
          if (!valor) return;
          if (n < 2 && !melhor) noTopo++;
          // aparecer em vários lugares da página conta um pouco mais
          melhor = melhor ? melhor + valor * 0.2 : valor;
        });
        if (melhor) cobertos++;
        pontos += melhor;
      }
      if (cobertos) {
        if (pagina.titulo.includes(limpa)) pontos += 10;
        if (pagina.item.ok) pontos += 0.5;
      }
      if (pagina.fixas.includes(pedida)) {
        pontos += 1000;
        cobertos = noTopo = termos.length;
      }
      return { pagina, pontos, cobertos, noTopo };
    });

    const maior = pontuadas.reduce((n, p) => Math.max(n, p.cobertos), 0);
    if (!maior) return vazio;

    const aceita = termos.map(({ termo, iguais }) => (p: string) => p === termo || iguais.includes(p) || (termo.length >= 3 && p.startsWith(termo)));
    const bate = (p: string) => aceita.some((f) => f(p));

    const achados: Achado[] = pontuadas
      .filter((p) => p.cobertos === maior)
      .sort((a, b) => b.pontos - a.pontos)
      .map(({ pagina, noTopo }, n) => {
        const item = pagina.item;
        // o trecho só interessa quando a resposta está no meio do texto (e só nos primeiros, para não pesar)
        if (noTopo >= maior || n >= 24) return { item };
        let melhor: { nota: number; linha: string; parte: Item['p'][number] } | undefined;
        for (const parte of item.p) {
          const doTitulo = palavrasDe(parte.h ?? '');
          for (const linha of parte.l) {
            const daLinha = [...palavrasDe(linha)];
            let nota = 0;
            for (const f of aceita) {
              if (daLinha.some(f)) nota += 2;
              else if ([...doTitulo].some(f)) nota += 1;
            }
            if (nota && (!melhor || nota > melhor.nota)) melhor = { nota, linha, parte };
          }
        }
        return melhor ? { item, trecho: { texto: recortar(melhor.linha, bate), titulo: melhor.parte.h, ancora: melhor.parte.a } } : { item };
      });

    return {
      achados,
      parcial: maior < termos.length,
      correcao: trocas.size ? digitadas.map((p) => trocas.get(p) ?? p).join(' ') : undefined,
      marcar: termos.flatMap(({ termo, iguais }) => [termo, ...iguais]),
    };
  };
}

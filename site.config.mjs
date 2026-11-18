// Tudo que muda quando o domínio ou o AdSense chegarem fica AQUI.
export const SITE = {
  nome: 'Macetes GTA 6',
  slogan: 'Códigos, easter eggs e segredos do GTA 6, conferidos antes de ir ao ar',
  descricao:
    'Códigos, macetes, easter eggs, segredos e dicas de dinheiro do GTA 6 em português. Cada dica traz a fonte e um selo: confirmado ou em verificação.',

  // Domínio próprio. Vazio = site no endereço provisório.
  // Exemplo: 'https://macetesgta6.com.br'
  dominio: 'https://macetesgta6.com.br',

  // true = o Google pode indexar o site. Quando o domínio próprio for ligado,
  // o GitHub Pages redireciona sozinho o endereço provisório para ele.
  indexar: true,

  // Códigos de verificação (só o conteúdo da meta tag) do Google Search Console e do Bing Webmaster.
  googleVerificacao: '',
  bingVerificacao: '',

  // Endereço do canal de cortes no YouTube (aparece no rodapé e nas dicas com corte).
  canalCortes: 'https://www.youtube.com/@vice_cortes_gtavi_clips',

  // Endereço provisório (GitHub Pages) usado enquanto "dominio" estiver vazio.
  provisorio: { site: 'https://saopaulosuculentas.github.io', base: '/gta6-dicas' },

  // ID do Google AdSense. Vazio = nenhum anúncio é carregado.
  // Exemplo: 'ca-pub-1234567890123456'
  adsenseId: '',

  // Números dos blocos de anúncio criados no painel do AdSense (opcional).
  // Vazio = formato automático. Exemplo: { faixa: '1234567890', retangulo: '2345678901' }
  adsBlocos: {},

  // Links de afiliado (ganho além do AdSense). Vazio = bloco não aparece.
  // Exemplo: { nome: 'Controle DualSense', nota: 'O controle padrão do PS5', url: 'https://...' }
  afiliados: [],

  // E-mail público de contato (aparece em /contato/). Use um e-mail do domínio, não o pessoal.
  emailContato: '',

  lancamento: '2026-11-19',
};

export const temDominio = Boolean(SITE.dominio);
export const INDEXAR = SITE.indexar;

export const CATEGORIAS = {
  codigos: {
    nome: 'Códigos',
    titulo: 'Códigos e macetes do GTA 6 (PS5 e Xbox)',
    descricao: 'Lista de códigos e macetes do GTA 6 para PS5 e Xbox Series: sequência de botões, o que cada um faz e se já foi confirmado.',
    chamada: 'Sequências de botões, o que cada uma faz e em qual console funciona.',
  },
  'easter-eggs': {
    nome: 'Easter eggs',
    titulo: 'Easter eggs do GTA 6: lista com local e vídeo',
    descricao: 'Todos os easter eggs do GTA 6 já encontrados: referências, piadas escondidas e mistérios, com o local exato e o vídeo de quem achou.',
    chamada: 'Referências, piadas escondidas e mistérios de Leonida.',
  },
  'segredos-e-locais': {
    nome: 'Segredos e locais',
    titulo: 'Segredos e locais escondidos do GTA 6',
    descricao: 'Armas raras, veículos escondidos, colecionáveis e lugares secretos do mapa do GTA 6.',
    chamada: 'Armas raras, veículos escondidos e cantos do mapa que pouca gente viu.',
  },
  dinheiro: {
    nome: 'Dinheiro',
    titulo: 'Como ganhar dinheiro rápido no GTA 6',
    descricao: 'Jeitos de ganhar dinheiro rápido no modo história do GTA 6, mostrados funcionando e com a fonte de cada um.',
    chamada: 'Jeitos de encher a carteira no modo história.',
  },
  dicas: {
    nome: 'Dicas',
    titulo: 'Dicas de GTA 6',
    descricao: 'Dicas práticas de GTA 6: controles, fuga da polícia, missões e ajustes que facilitam o jogo.',
    chamada: 'O que facilita a vida: controles, fuga da polícia, missões.',
  },
  guias: {
    nome: 'Guias',
    titulo: 'Guias do GTA 6: respostas diretas',
    descricao: 'Respostas diretas sobre o GTA 6: horário de lançamento, consoles, preço, tamanho do download, mapa, personagens e o que é verdade sobre os códigos.',
    chamada: 'Respostas diretas: lançamento, consoles, preço, mapa e personagens.',
  },
};

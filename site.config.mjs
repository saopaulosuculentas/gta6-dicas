// Tudo que muda quando o domínio ou o AdSense chegarem fica AQUI.
export const SITE = {
  nome: 'Macetes GTA 6',
  slogan: 'Códigos, easter eggs e segredos do GTA 6, conferidos antes de ir ao ar',
  descricao:
    'Códigos, macetes, easter eggs, segredos e dicas de dinheiro do GTA 6 em português. Cada dica traz a fonte e um selo: confirmado ou em verificação.',

  // Domínio próprio. Vazio = site no endereço provisório e escondido do Google (noindex).
  // Exemplo: 'https://macetesgta6.com.br'
  dominio: '',

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
// Só deixa o Google indexar quando o domínio próprio estiver ligado.
export const INDEXAR = temDominio;

export const CATEGORIAS = {
  codigos: {
    nome: 'Códigos',
    titulo: 'Códigos e macetes do GTA 6',
    descricao: 'Todos os códigos do GTA 6 para PS5 e Xbox Series, com a sequência de botões e o que cada um faz.',
    chamada: 'Sequências de botões, o que cada uma faz e em qual console funciona.',
  },
  'easter-eggs': {
    nome: 'Easter eggs',
    titulo: 'Easter eggs do GTA 6',
    descricao: 'Referências, piadas escondidas e mistérios do GTA 6, com o local exato e o vídeo de quem achou.',
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
    titulo: 'Como ganhar dinheiro no GTA 6',
    descricao: 'Formas de ganhar dinheiro rápido no modo história do GTA 6, testadas e com fonte.',
    chamada: 'Jeitos de encher a carteira no modo história.',
  },
  dicas: {
    nome: 'Dicas',
    titulo: 'Dicas de GTA 6',
    descricao: 'Dicas práticas de GTA 6: controles, fuga da polícia, missões e ajustes que facilitam o jogo.',
    chamada: 'O que facilita a vida: controles, fuga da polícia, missões.',
  },
};

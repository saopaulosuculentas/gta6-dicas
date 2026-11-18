# Macetes GTA 6

Site de códigos, easter eggs, segredos e dicas do GTA 6 em português.

- `site.config.mjs`: nome do site, domínio, ID do AdSense, links de afiliado.
- `src/content/dicas/`: uma dica por arquivo. A pasta `exemplos/` só aparece no modo de teste.
- `agente/ROTINA.md`: o roteiro que o agente segue para achar, conferir e publicar dicas.
- `dados/diario.md`: o que cada rodada do agente fez.

Ver o site no computador: `npm run dev` e abrir http://localhost:4326/gta6-dicas/

Publicar: `powershell -ExecutionPolicy Bypass -File publicar.ps1 "o que mudou"`

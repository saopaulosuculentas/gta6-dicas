// Gera a imagem que aparece quando o site é compartilhado (WhatsApp, X, Discord): public/og.png
// Uso: node agente/og.mjs   (só precisa rodar de novo se o nome do site mudar)
import sharp from 'sharp';

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<defs>
<linearGradient id="s" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#ffb347"/><stop offset=".3" stop-color="#ff6a4d"/><stop offset=".62" stop-color="#ff4fa3"/><stop offset="1" stop-color="#9a4dff"/></linearGradient>
<radialGradient id="a" cx="88%" cy="-5%" r="70%"><stop offset="0" stop-color="#ff4fa3" stop-opacity=".55"/><stop offset="1" stop-color="#ff4fa3" stop-opacity="0"/></radialGradient>
<radialGradient id="b" cx="35%" cy="-20%" r="75%"><stop offset="0" stop-color="#9a4dff" stop-opacity=".5"/><stop offset="1" stop-color="#9a4dff" stop-opacity="0"/></radialGradient>
<radialGradient id="c" cx="-5%" cy="100%" r="60%"><stop offset="0" stop-color="#ffb347" stop-opacity=".35"/><stop offset="1" stop-color="#ffb347" stop-opacity="0"/></radialGradient>
</defs>
<rect width="1200" height="630" fill="#0d0916"/><rect width="1200" height="630" fill="url(#a)"/><rect width="1200" height="630" fill="url(#b)"/><rect width="1200" height="630" fill="url(#c)"/>
<rect width="1200" height="14" fill="url(#s)"/>
<text x="80" y="150" font-family="Arial Narrow, Arial, sans-serif" font-weight="700" font-size="34" letter-spacing="8" fill="#ffb347">GTA 6 EM PORTUGUÊS</text>
<text x="80" y="290" font-family="Impact, Arial Narrow, sans-serif" font-size="128" fill="#f4efe6">CÓDIGOS, MACETES</text>
<text x="80" y="420" font-family="Impact, Arial Narrow, sans-serif" font-size="128" fill="url(#s)">E SEGREDOS</text>
<text x="80" y="505" font-family="Arial, sans-serif" font-size="36" fill="#d9d2e3">Cada dica com a fonte e o selo: confirmado ou em verificação.</text>
<rect x="80" y="545" width="300" height="52" rx="8" fill="url(#s)"/>
<text x="230" y="582" text-anchor="middle" font-family="Impact, Arial Narrow, sans-serif" font-size="34" fill="#0d0916">MACETES GTA 6</text>
</svg>`;

await sharp(Buffer.from(svg)).png().toFile('public/og.png');
console.log('public/og.png gerada');

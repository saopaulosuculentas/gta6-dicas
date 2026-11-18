// Arquivo que o Google AdSense exige. Só tem conteúdo quando o adsenseId estiver preenchido em site.config.mjs.
import { SITE } from '../../site.config.mjs';

export function GET() {
  const pub = SITE.adsenseId.replace('ca-', '');
  const corpo = pub ? `google.com, ${pub}, DIRECT, f08c47fec0942fa0\n` : '';
  return new Response(corpo, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}

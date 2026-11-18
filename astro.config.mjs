import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { SITE, temDominio } from './site.config.mjs';

export default defineConfig({
  site: temDominio ? SITE.dominio : SITE.provisorio.site,
  base: temDominio ? '/' : SITE.provisorio.base,
  trailingSlash: 'always',
  integrations: [sitemap()],
  server: { port: 4326 },
});

"""Avisa os buscadores que usam IndexNow (Bing, Yandex, Seznam, Naver e outros) sobre páginas novas ou atualizadas.

Roda sozinho no fim do publicar.ps1. Manda só o que mudou nas últimas 24 horas, mais a capa e as seções.
O Google não usa IndexNow; para ele vale o mapa do site (sitemap) com as datas de atualização.

Uso:  python agente/indexnow.py
"""
import datetime
import json
import re
import urllib.request

import yaml

from comum import BRT, DICAS, RAIZ, utf8

CHAVE = "d7b993ead37d2a176722060213d5f832"


def endereco_base():
    cfg = (RAIZ / "site.config.mjs").read_text(encoding="utf-8")
    dominio = re.search(r"^\s*dominio:\s*'([^']*)'", cfg, re.M)
    if dominio and dominio.group(1):
        return dominio.group(1).rstrip("/")
    site = re.search(r"site:\s*'([^']+)'", cfg).group(1)
    base = re.search(r"base:\s*'([^']+)'", cfg).group(1)
    return site.rstrip("/") + base.rstrip("/")


def main():
    utf8()
    base = endereco_base()
    limite = datetime.datetime.now(BRT) - datetime.timedelta(hours=24)
    urls, categorias = [f"{base}/", f"{base}/novidades/"], set()
    for arq in DICAS.glob("*.md"):
        cab = yaml.safe_load(arq.read_text(encoding="utf-8").split("---", 2)[1])
        data = cab.get("atualizado_em")
        data = data if isinstance(data, datetime.datetime) else datetime.datetime.fromisoformat(str(data))
        if data.tzinfo is None:
            data = data.replace(tzinfo=BRT)
        if data >= limite:
            urls.append(f"{base}/dica/{arq.stem}/")
            categorias.add(cab.get("categoria"))
    urls += [f"{base}/{c}/" for c in sorted(categorias)]
    host = re.sub(r"^https?://", "", base).split("/")[0]
    corpo = {"host": host, "key": CHAVE, "keyLocation": f"{base}/{CHAVE}.txt", "urlList": urls}
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(corpo).encode("utf-8"),
                                 headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"IndexNow: {len(urls)} endereços avisados (resposta {r.status})")
    except Exception as e:
        print(f"IndexNow: não consegui avisar agora ({e}); o mapa do site continua valendo")


if __name__ == "__main__":
    main()

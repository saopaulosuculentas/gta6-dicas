"""Levanta o que as pessoas digitam no Google sobre GTA 6 (sugestões do autocompletar, em português do Brasil).

Cada sugestão é uma pergunta real com intenção de busca. O agente usa a lista para decidir quais páginas criar
primeiro e para escrever títulos com as palavras que as pessoas usam.

Uso:  python agente/buscas.py           (rodar 1 vez por dia; leva menos de 1 minuto)
Sai:  dados/buscas.md   (lista agrupada, com a página do site que já responde, quando existe)
"""
import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import yaml

from comum import DADOS, DICAS, agora, utf8

RAIZES = [
    "gta 6", "gta 6 codigo", "gta 6 codigos", "gta 6 macete", "gta 6 cheat", "gta 6 como", "gta 6 onde",
    "gta 6 qual", "gta 6 quanto", "gta 6 quando", "gta 6 tem", "gta 6 dá para", "gta 6 da pra", "gta 6 pode",
    "gta 6 dinheiro", "gta 6 easter egg", "gta 6 segredo", "gta 6 segredos", "gta 6 local", "gta 6 carro",
    "gta 6 arma", "gta 6 missão", "gta 6 missao", "gta 6 dica", "gta 6 dicas", "gta 6 mapa", "gta 6 policia",
    "gta 6 foco", "gta 6 casa", "gta 6 personagem", "gta 6 jason", "gta 6 lucia", "gta 6 trofeu", "gta 6 platina",
    "gta 6 ps5", "gta 6 xbox", "gta 6 pc", "gta 6 ps4", "gta 6 online", "gta 6 preço", "gta 6 tamanho",
    "como ganhar dinheiro gta 6", "como fazer gta 6", "como desbloquear gta 6", "codigo gta 6 ps5",
    "codigo gta 6 xbox", "macete gta 6", "onde fica gta 6", "como achar gta 6",
]
LETRAS = "abcdefghijlmnopqrstuv"

GRUPOS = [
    ("Códigos e macetes", r"c[oó]dig|cheat|macete|trapa|manha"),
    ("Dinheiro", r"dinheiro|grana|money|rico|\$"),
    ("Easter eggs e segredos", r"easter|segredo|secret|mist[eé]rio|p[eé] grande|alien|fantasma|ovni"),
    ("Locais e mapa", r"onde|local|mapa|fica|achar|encontrar"),
    ("Carros, armas e itens", r"carro|moto|ve[ií]culo|arma|barco|avi[aã]o|helic"),
    ("Missões, troféus e progresso", r"miss[aã]o|miss[oõ]es|trof[eé]u|platina|conquista|zerar|final|cap[ií]tulo"),
    ("Como fazer", r"^como |como "),
    ("Plataforma, preço e lançamento", r"ps5|ps4|xbox|pc|pre[cç]o|valor|lan[cç]a|data|hor[aá]rio|tamanho|gb|dublad|legenda|online"),
]


def sugerir(termo):
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "hl": "pt-BR", "gl": "br", "q": termo})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pesquisa de pautas)"})
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                dados = json.loads(r.read().decode("utf-8", errors="replace"))
            return [s for s in dados[1] if isinstance(s, str)]
        except Exception:
            time.sleep(1.5 * (tentativa + 1))
    return []


def sem_acento(t):
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def paginas():
    """Título, título SEO e perguntas de cada dica publicada, para ver o que já está respondido."""
    lista = []
    for arq in DICAS.glob("*.md"):
        texto = arq.read_text(encoding="utf-8")
        try:
            cab = yaml.safe_load(texto.split("---", 2)[1])
        except Exception:
            continue
        palavras = " ".join([cab.get("titulo", ""), cab.get("titulo_seo", "") or "", " ".join(p.get("p", "") for p in cab.get("perguntas") or [])])
        lista.append((arq.stem, set(re.findall(r"[a-z0-9]{3,}", sem_acento(palavras))) - {"gta"}))
    return lista


def melhor_pagina(busca, lista):
    alvo = set(re.findall(r"[a-z0-9]{3,}", sem_acento(busca))) - {"gta"}
    if not alvo:
        return None
    melhor, nota = None, 0.0
    for slug, palavras in lista:
        comum = len(alvo & palavras) / len(alvo)
        if comum > nota:
            melhor, nota = slug, comum
    return melhor if nota >= 0.6 else None


def main():
    utf8()
    termos = list(RAIZES) + [f"gta 6 {l}" for l in LETRAS] + [f"gta 6 como {l}" for l in "acdefgmprstv"]
    with ThreadPoolExecutor(6) as ex:
        resultados = list(ex.map(sugerir, termos))
    vistos, buscas = set(), []
    for lista in resultados:
        for s in lista:
            k = sem_acento(s).strip()
            if k in vistos or not re.search(r"gta ?(6|vi)\b", k):
                continue
            vistos.add(k)
            buscas.append(s.strip())
    if not buscas:
        print("o Google não devolveu sugestões agora; tente de novo mais tarde")
        return
    pags = paginas()
    grupos = {nome: [] for nome, _ in GRUPOS}
    grupos["Outras"] = []
    for b in sorted(buscas, key=lambda x: (len(x), x)):
        for nome, padrao in GRUPOS:
            if re.search(padrao, sem_acento(b)):
                grupos[nome].append(b)
                break
        else:
            grupos["Outras"].append(b)
    sem_pagina = 0
    linhas = [
        "# Buscas reais sobre GTA 6 (Google, português do Brasil)",
        "",
        f"Gerado em {agora():%d/%m/%Y %H:%M} por `agente/buscas.py` a partir das sugestões do autocompletar do Google.",
        "Cada linha é algo que as pessoas digitam. `✔ nome-da-dica` = o site já tem página que responde. `✘` = falta página.",
        "O agente usa esta lista para escolher o que publicar primeiro e para escrever títulos com as palavras das pessoas.",
        "Só vira página o que tiver fonte de confiança. Busca sem resposta conhecida fica esperando.",
        "",
    ]
    for nome, lista in grupos.items():
        if not lista:
            continue
        linhas += [f"## {nome} ({len(lista)})", ""]
        for b in lista:
            p = melhor_pagina(b, pags)
            if p:
                linhas.append(f"- ✔ {b} → `{p}`")
            else:
                sem_pagina += 1
                linhas.append(f"- ✘ {b}")
        linhas.append("")
    (DADOS / "buscas.md").write_text("\n".join(linhas), encoding="utf-8")
    print(f"{len(buscas)} buscas reais levantadas; {len(buscas) - sem_pagina} já têm página, {sem_pagina} ainda não → dados/buscas.md")


if __name__ == "__main__":
    main()

"""Minera o que já deu audiência no GTA V para decidir quais páginas-lista o site deve ter no GTA 6.

Busca no YouTube por assunto, ordena por visualizações e guarda os vídeos com mais de 1 milhão.
Uso:  python agente/pautas.py        (rodar de vez em quando; não faz parte da rodada de 3 em 3 horas)
Sai:  dados/pautas.md
"""
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from comum import DADOS, agora, hms, utf8, ytdlp

MAIS_VISTOS = "CAMSAhAB"  # filtro do YouTube: ordenar por visualizações + só vídeos
MINIMO = 1_000_000
FORA = ("mod", "rp", "roleplay", "online", "fivem", "san andreas", "vice city", "gta 4", "gta iv", "minecraft", "banban", "gta 6", "gta vi")

# assunto → (buscas no GTA V, página-lista equivalente no site, categoria do site)
ASSUNTOS = {
    "Locais secretos": (["gta 5 locais secretos", "gta 5 secret locations"], "Todos os locais secretos do GTA 6 (com mapa descrito e vídeo)", "segredos-e-locais"),
    "Easter eggs e mistérios": (["gta 5 easter eggs", "gta 5 mistérios"], "Todos os easter eggs do GTA 6, do mais fácil ao mais escondido", "easter-eggs"),
    "Carros raros": (["gta 5 carros raros localização", "gta 5 rare cars locations story mode"], "Onde achar cada carro raro do GTA 6 no modo história", "segredos-e-locais"),
    "Armas raras": (["gta 5 armas secretas localização", "gta 5 secret weapons locations"], "Onde pegar cada arma rara do GTA 6", "segredos-e-locais"),
    "Dinheiro": (["gta 5 dinheiro infinito modo história", "gta 5 money story mode"], "Os jeitos mais rápidos de ganhar dinheiro no GTA 6 (modo história)", "dinheiro"),
    "Códigos": (["gta 5 códigos", "gta 5 cheat codes"], "Todos os códigos do GTA 6 para PS5 e Xbox", "codigos"),
    "Detalhes e coisas que você não sabia": (["gta 5 coisas que você não sabia", "gta 5 things you didn't know"], "Detalhes do GTA 6 que quase ninguém percebeu", "dicas"),
    "Missões secretas": (["gta 5 missões secretas", "gta 5 secret missions"], "Missões e encontros secretos do GTA 6 e como ativar cada um", "segredos-e-locais"),
}


def buscar(termo):
    q = urllib.parse.quote_plus(termo)
    cod, saida, _ = ytdlp(["--flat-playlist", "-J", "--playlist-end", "30", f"https://www.youtube.com/results?search_query={q}&sp={MAIS_VISTOS}"], timeout=120)
    try:
        return [e for e in json.loads(saida).get("entries") or [] if e and e.get("id")]
    except (json.JSONDecodeError, AttributeError):
        return []


def serve(e):
    t = f" {(e.get('title') or '').lower()} "
    return (e.get("view_count") or 0) >= MINIMO and ("gta 5" in t or "gta v" in t or "gtav" in t) and not any(f" {f}" in t for f in FORA)


def main():
    utf8()
    termos = [(assunto, t) for assunto, (buscas, _, _) in ASSUNTOS.items() for t in buscas]
    with ThreadPoolExecutor(6) as ex:
        resultados = list(ex.map(lambda p: buscar(p[1]), termos))
    por_assunto = {}
    for (assunto, _), entradas in zip(termos, resultados):
        for e in entradas:
            if serve(e):
                por_assunto.setdefault(assunto, {})[e["id"]] = e

    linhas = [
        "# Pautas: o que já deu audiência no GTA V",
        "",
        f"Gerado em {agora():%d/%m/%Y %H:%M} por `agente/pautas.py`. Vídeos de GTA V com mais de 1 milhão de visualizações, por assunto.",
        "A ideia é ter no site a página equivalente para o GTA 6, mais completa que o vídeo original, assim que houver dicas reais suficientes (5 ou mais do assunto).",
        "",
    ]
    for assunto, (_, pagina, categoria) in ASSUNTOS.items():
        videos = sorted(por_assunto.get(assunto, {}).values(), key=lambda e: -(e.get("view_count") or 0))[:8]
        linhas += [f"## {assunto}", "", f"**Página do site:** {pagina}  ", f"**Categoria:** `{categoria}`  ", "**Situação:** aguardando dicas reais", ""]
        if not videos:
            linhas += ["Nenhum vídeo acima de 1 milhão nesta busca.", ""]
            continue
        linhas += ["| Views | Duração | Canal | Promessa do título |", "|---:|---:|---|---|"]
        for e in videos:
            titulo = (e.get("title") or "").replace("|", "/")
            linhas.append(f"| {(e.get('view_count') or 0) / 1e6:.1f} mi | {hms(e.get('duration') or 0)} | {e.get('channel') or ''} | {titulo} |")
        linhas.append("")
    (DADOS / "pautas.md").write_text("\n".join(linhas), encoding="utf-8")
    total = sum(len(v) for v in por_assunto.values())
    print(f"pautas prontas: {total} vídeos validados em {len(por_assunto)} assuntos → dados/pautas.md")


if __name__ == "__main__":
    main()

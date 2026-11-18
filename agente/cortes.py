"""Lista os envios do NOSSO canal de cortes e guarda em dados/cortes.json (a capa do site mostra os mais novos).

O endereço do canal vem de site.config.mjs (campo canalCortes).
Uso:  python agente/cortes.py
"""
import json
import re

from comum import DADOS, RAIZ, gravar_json, ler_json, utf8, ytdlp


def main():
    utf8()
    config = (RAIZ / "site.config.mjs").read_text(encoding="utf-8")
    m = re.search(r"canalCortes:\s*'([^']+)'", config)
    if not m:
        print("canalCortes vazio em site.config.mjs: nada a fazer")
        return
    canal = m.group(1).rstrip("/")
    antigos = {c["id"]: c for c in ler_json(DADOS / "cortes.json", [])}
    achados = []
    for aba, tipo in (("shorts", "curto"), ("videos", "longo")):
        cod, saida, _ = ytdlp(["--flat-playlist", "-J", "--playlist-end", "12", f"{canal}/{aba}"], timeout=90)
        try:
            entradas = (json.loads(saida) or {}).get("entries") or []
        except json.JSONDecodeError:
            entradas = []
        for e in entradas:
            if e and e.get("id"):
                achados.append({"id": e["id"], "titulo": (e.get("title") or "").strip(), "tipo": tipo})
    if not achados:
        print("não consegui listar o canal agora; mantive a lista anterior")
        return
    novos = [c for c in achados if c["id"] not in antigos]
    gravar_json(DADOS / "cortes.json", achados[:12])
    print(f"NOSSO CANAL: {len(achados)} cortes ({len(novos)} novo(s))")
    for c in achados[:12]:
        marca = "NOVO " if c["id"] not in antigos else "     "
        print(f"  {marca}{c['tipo']:<5} https://www.youtube.com/watch?v={c['id']}  {c['titulo']}")


if __name__ == "__main__":
    main()

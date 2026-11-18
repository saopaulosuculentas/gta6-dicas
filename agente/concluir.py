"""Marca um vídeo como lido, depois que o agente tirou dele o que havia para tirar.

Uso:  python agente/concluir.py ID_DO_VIDEO "o que saiu dele"
      python agente/concluir.py dQw4w9WgXcQ "2 dicas novas, 1 confirmação"
      python agente/concluir.py dQw4w9WgXcQ "nada aproveitável: só boato"
"""
import sys

from comum import TRECHOS, VISTOS, agora_iso, gravar_json, ler_json, utf8


def main():
    utf8()
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    vid, nota = sys.argv[1], " ".join(sys.argv[2:])
    arq = TRECHOS / f"{vid}.txt"
    feitos = TRECHOS / "feitos"
    feitos.mkdir(parents=True, exist_ok=True)
    if arq.exists():
        arq.replace(feitos / arq.name)
    vistos = ler_json(VISTOS, {})
    v = vistos.get(vid, {})
    v.update({"resultado": "lido", "nota": nota, "lido_em": agora_iso()})
    vistos[vid] = v
    gravar_json(VISTOS, vistos)
    print(f"ok: {vid} marcado como lido ({nota}). Faltam {len(list(TRECHOS.glob('*.txt')))} arquivo(s) em agente/trechos/")


if __name__ == "__main__":
    main()

"""Mostra, em poucas linhas, tudo que já está publicado. O agente lê isto antes de escrever, para não repetir dica.

Uso:  python agente/indice.py
"""
import yaml

from comum import DICAS, utf8


def ler(arq):
    texto = arq.read_text(encoding="utf-8")
    if not texto.startswith("---"):
        return None, texto
    _, cab, corpo = texto.split("---", 2)
    return yaml.safe_load(cab), corpo


def main():
    utf8()
    arquivos = sorted(p for p in DICAS.glob("*.md"))
    print(f"DICAS PUBLICADAS: {len(arquivos)}\n")
    for arq in arquivos:
        d, _ = ler(arq)
        if not d:
            continue
        canais = sorted({f["canal"] for f in d.get("fontes", [])})
        cod = d.get("codigo") or {}
        seq = " ".join(cod.get("ps5") or []) or cod.get("telefone") or cod.get("texto") or ""
        print(f"- {arq.stem}  [{d['categoria']}] [{d['status']}]  fontes: {', '.join(canais)}")
        print(f"    {d['titulo']}")
        if seq:
            print(f"    código PS5: {seq}")


if __name__ == "__main__":
    main()

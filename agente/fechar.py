"""Fecha a rodada: atualiza a "última checagem" que aparece no site e anota no diário.

Uso:  python agente/fechar.py "resumo da rodada em uma frase"
"""
import sys

from comum import DADOS, DICAS, ESTADO, VISTOS, agora, gravar_json, ler_json, utf8


def main():
    utf8()
    resumo = " ".join(sys.argv[1:]).strip() or "rodada sem novidade"
    vistos = ler_json(VISTOS, {})
    estado = ler_json(ESTADO, {})
    quando = agora()
    estado["ultima_rodada"] = quando.isoformat()
    estado["videos_lidos"] = sum(1 for x in vistos.values() if x.get("resultado") in ("trechos", "sem-sinal", "lido"))
    gravar_json(ESTADO, estado)
    diario = DADOS / "diario.md"
    if not diario.exists():
        diario.write_text("# Diário do agente\n\nUma linha por rodada: quando rodou e o que mudou no site.\n\n", encoding="utf-8")
    n = len(list(DICAS.glob("*.md")))
    with diario.open("a", encoding="utf-8") as f:
        f.write(f"- **{quando:%d/%m/%Y %H:%M}** · {n} dicas no ar · {estado['videos_lidos']} vídeos lidos · {resumo}\n")
    print(f"rodada fechada às {quando:%H:%M}: {resumo}")


if __name__ == "__main__":
    main()

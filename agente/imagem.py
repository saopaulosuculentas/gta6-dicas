"""Transforma um quadro conferido em imagem do site (webp leve, 1200x675), recortando o rosto ou a marca do criador.

Fluxo: 1) python agente/quadros.py ID MINUTO     (tira os quadros e olhe as imagens)
       2) escolha um quadro SÓ COM O JOGO e rode:
          python agente/imagem.py agente/quadros/ID/4-12_03.jpg NOME-DA-DICA nome-curto [--corte X,Y,L,A]
Sai:   public/img/NOME-DA-DICA/nome-curto.webp  -> na dica:  imagens: [{ arquivo: "NOME-DA-DICA/nome-curto.webp", ... }]

--corte  recorte em pixels do quadro de 1280x720 (x, y, largura, altura). Use para tirar a câmera do streamer,
         a marca d'água ou o chat. O resultado é ajustado para 16:9 pelo centro.
Regras: só imagem do jogo (sem rosto, sem logo, sem nome do canal na imagem), no máximo 3 por dica, sempre com crédito.
"""
import argparse
import re
import subprocess
from pathlib import Path

from comum import RAIZ, utf8


def main():
    utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("quadro", help="caminho do .jpg tirado com quadros.py")
    ap.add_argument("dica", help="nome do arquivo da dica (sem .md), vira a pasta da imagem")
    ap.add_argument("nome", help="nome curto da imagem, só letras minúsculas, números e hífen")
    ap.add_argument("--corte", help="X,Y,LARGURA,ALTURA em pixels do quadro 1280x720")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+", a.dica) or not re.fullmatch(r"[a-z0-9-]+", a.nome):
        raise SystemExit("ERRO: dica e nome só podem ter letras minúsculas, números e hífen.")
    origem = Path(a.quadro)
    if not origem.exists():
        raise SystemExit(f"ERRO: não achei {origem}")
    filtros = []
    if a.corte:
        x, y, w, h = [int(v) for v in a.corte.split(",")]
        filtros.append(f"crop={w}:{h}:{x}:{y}")
    filtros += ["scale=1200:675:force_original_aspect_ratio=increase", "crop=1200:675"]
    pasta = RAIZ / "public" / "img" / a.dica
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{a.nome}.webp"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(origem), "-vf", ",".join(filtros),
                    "-c:v", "libwebp", "-quality", "72", "-compression_level", "6", str(destino)], check=True)
    kb = destino.stat().st_size // 1024
    print(f"PRONTO: {destino} ({kb} KB)")
    print(f'  na dica:  - {{ arquivo: "{a.dica}/{a.nome}.webp", legenda: "...", canal: "...", url: "...", minuto: "m:ss" }}')


if __name__ == "__main__":
    main()

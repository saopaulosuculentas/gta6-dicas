"""Tira quadros de um ponto do vídeo, para conferir o que aparece na tela (sequência de botões, ponto no mapa).

Uso:  python agente/quadros.py ID_DO_VIDEO MINUTO [--dur 12] [--n 6]
      python agente/quadros.py dQw4w9WgXcQ 4:12
      python agente/quadros.py "https://www.youtube.com/watch?v=-p9V4ivrBnI" 4:12   (id que começa com "-": passe o link)
Sai:  agente/quadros/<id>/<minuto>_NN.jpg  (as imagens são só para conferência; nunca vão para o site)
"""
import argparse
import re
import subprocess

from comum import QUADROS, TRABALHO, hms, segundos, utf8, ytdlp


def main():
    utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("minuto", help="m:ss ou h:mm:ss")
    ap.add_argument("--dur", type=int, default=12, help="quantos segundos olhar a partir do minuto")
    ap.add_argument("--n", type=int, default=6, help="quantos quadros tirar")
    a = ap.parse_args()
    # aceita o link inteiro no lugar do id (necessário quando o id começa com "-")
    m = re.search(r"(?:v=|youtu\.be/|/live/|/shorts/)([\w-]{11})", a.id)
    if m:
        a.id = m.group(1)

    ini = max(0, segundos(a.minuto) - 2)
    fim = ini + a.dur + 2
    pasta = TRABALHO / a.id
    pasta.mkdir(parents=True, exist_ok=True)
    nome = f"q_{ini}"
    for velho in pasta.glob(f"{nome}.*"):
        velho.unlink()
    cod, _, erro = ytdlp(["-f", "bv*[height<=720][ext=mp4]/bv*[height<=720]/b[height<=720]/b", "--no-playlist", "-q",
                          "--download-sections", f"*{ini}-{fim}", "--force-keyframes-at-cuts",
                          "-o", str(pasta / f"{nome}.%(ext)s"), f"https://www.youtube.com/watch?v={a.id}"], timeout=600)
    video = next(iter(pasta.glob(f"{nome}.*")), None)
    if cod != 0 or not video:
        raise SystemExit(f"NÃO DEU PARA BAIXAR ESSE TRECHO: {erro.strip()[-300:]}")
    saida = QUADROS / a.id
    saida.mkdir(parents=True, exist_ok=True)
    rotulo = hms(ini + 2).replace(":", "-")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-vf", f"fps={a.n}/{a.dur + 4},scale=1280:-2",
                    "-q:v", "3", str(saida / f"{rotulo}_%02d.jpg")], check=True)
    video.unlink()
    print(f"QUADROS de {hms(ini)} a {hms(fim)}:")
    for p in sorted(saida.glob(f"{rotulo}_*.jpg")):
        print(f"  {p}")


if __name__ == "__main__":
    main()

"""Passo 1: acha vídeos e lives novos de GTA 6 que podem ter código, easter egg, segredo ou dica.

Uso:  python agente/coletar.py [--max 10] [--horas 48]
Sai:  agente/fila.json  (os melhores candidatos, do mais promissor para o menos)
"""
import argparse
import json
import math
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from comum import AGENTE, FILA, VISTOS, gravar_json, hms, ler_json, utf8, ytdlp

HOJE = "EgQIAhAB"  # filtro do YouTube: enviado hoje + só vídeos


def lista(url, limite):
    cod, saida, _ = ytdlp(["--flat-playlist", "-J", "--playlist-end", str(limite), url], timeout=90)
    if cod != 0 or not saida.strip():
        return []
    try:
        return [e for e in json.loads(saida).get("entries") or [] if e and e.get("id")]
    except json.JSONDecodeError:
        return []


def buscar(termo):
    q = urllib.parse.quote_plus(termo)
    return lista(f"https://www.youtube.com/results?search_query={q}&sp={HOJE}", 15)


def detalhe(video_id):
    cod, saida, erro = ytdlp(["-J", "--no-playlist", f"https://www.youtube.com/watch?v={video_id}"], timeout=90)
    if cod != 0:
        return None
    try:
        return json.loads(saida)
    except json.JSONDecodeError:
        return None


def pontos_do_titulo(titulo, termos):
    t = f" {titulo.lower()} "
    return sum(peso for palavra, peso in termos["sinais"].items() if palavra in t)


def main():
    utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=10, help="quantos vídeos entram na fila")
    ap.add_argument("--horas", type=int, default=48, help="idade máxima do vídeo")
    ap.add_argument("--min-views", type=int, default=300, help="mínimo de views para canal que não é de confiança")
    a = ap.parse_args()

    termos = ler_json(AGENTE / "termos.json")
    canais = ler_json(AGENTE / "canais.json", {}).get("canais", [])
    vistos = ler_json(VISTOS, {})
    confianca = {c["nome"].lower(): c["confianca"] for c in canais}

    print(f"[1/3] Procurando vídeos de hoje ({len(termos['buscas'])} buscas, {len(canais)} canais de confiança)…", flush=True)
    achados = {}
    with ThreadPoolExecutor(6) as ex:
        for entradas in ex.map(buscar, termos["buscas"]):
            for e in entradas:
                achados.setdefault(e["id"], e)
        urls = [c["url"].rstrip("/") + aba for c in canais for aba in ("/videos", "/streams")]
        for url, entradas in zip(urls, ex.map(lambda u: lista(u, 6), urls)):
            for e in entradas:
                e["_do_canal"] = True
                achados.setdefault(e["id"], e)

    candidatos = []
    for vid, e in achados.items():
        if vid in vistos:
            continue
        titulo = e.get("title") or ""
        t = f" {titulo.lower()} "
        if not e.get("_do_canal") and not any(o in t for o in termos["obrigatorio"]):
            continue
        if any(b in t for b in termos["bloqueio"]):
            continue
        dur = e.get("duration") or 0
        if dur and dur < 45:
            continue
        sinais = pontos_do_titulo(titulo, termos)
        if sinais == 0 and not e.get("_do_canal"):
            continue
        pre = sinais * 2 + math.log10((e.get("view_count") or 0) + 10)
        candidatos.append((pre, vid, e, sinais))
    candidatos.sort(key=lambda c: -c[0])
    candidatos = candidatos[: a.max * 3]
    print(f"      {len(achados)} vídeos achados, {len(candidatos)} parecem úteis e ainda não foram lidos", flush=True)

    print("[2/3] Conferindo data, duração e legenda de cada um…", flush=True)
    agora = time.time()
    fila = []
    with ThreadPoolExecutor(6) as ex:
        for (pre, vid, e, sinais), meta in zip(candidatos, ex.map(lambda c: detalhe(c[1]), candidatos)):
            if not meta:
                continue
            if meta.get("live_status") in ("is_live", "is_upcoming", "post_live"):
                continue  # ainda ao vivo ou processando: fica para a próxima rodada
            quando = meta.get("release_timestamp") or meta.get("timestamp")
            if not quando:
                continue
            idade_h = max(0.5, (agora - quando) / 3600)
            if idade_h > a.horas:
                continue
            views = meta.get("view_count") or 0
            canal = meta.get("channel") or meta.get("uploader") or ""
            conf = confianca.get(canal.lower(), "normal")
            # canal desconhecido com quase ninguém assistindo costuma ser isca: espera ganhar audiência
            if conf == "normal" and views < a.min_views:
                continue
            nota = min(sinais, 10) + math.log10(views / idade_h + 10) * 6 + {"oficial": 50, "alta": 8}.get(conf, 0)
            autos = [k for k in (meta.get("automatic_captions") or {}) if k.endswith("-orig")]
            fila.append({
                "id": vid,
                "titulo": meta.get("title"),
                "canal": canal,
                "canal_url": meta.get("channel_url"),
                "confianca": conf,
                "url": f"https://www.youtube.com/watch?v={vid}",
                "duracao": meta.get("duration") or 0,
                "views": views,
                "publicado": quando,
                "idade_h": round(idade_h, 1),
                "foi_live": bool(meta.get("was_live")),
                "idioma": (meta.get("language") or "").split("-")[0] or None,
                "legendas": sorted(meta.get("subtitles") or {}),
                "legendas_auto": autos,
                "nota": round(nota, 1),
            })
    fila.sort(key=lambda v: -v["nota"])
    fila = fila[: a.max]
    gravar_json(FILA, fila)

    print(f"[3/3] Fila pronta: {len(fila)} vídeos → agente/fila.json\n", flush=True)
    for v in fila:
        print(f"  {v['nota']:>5}  {hms(v['duracao']):>8}  {v['views']:>8} views  {v['idade_h']:>5} h  {v['canal'][:24]:<24}  {v['titulo'][:70]}")
    if not fila:
        print("  (nenhum vídeo novo que valha ler nesta rodada)")


if __name__ == "__main__":
    main()

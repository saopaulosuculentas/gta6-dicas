"""Peças usadas por todos os scripts do agente."""
import datetime
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AGENTE = RAIZ / "agente"
DADOS = RAIZ / "dados"
TRABALHO = AGENTE / "trabalho"      # downloads temporários (fora do git)
TRECHOS = AGENTE / "trechos"        # o que o agente lê
QUADROS = AGENTE / "quadros"        # imagens tiradas dos vídeos (fora do git, nunca vão para o site)
DICAS = RAIZ / "src" / "content" / "dicas"
VISTOS = DADOS / "vistos.json"
ESTADO = DADOS / "estado.json"
FILA = AGENTE / "fila.json"
BRT = datetime.timezone(datetime.timedelta(hours=-3))


def utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def ler_json(caminho, padrao=None):
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return padrao


def gravar_json(caminho, dados):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(caminho)


def ytdlp(args, timeout=180):
    """Roda o yt-dlp e devolve (código, saída, erro)."""
    cmd = [sys.executable, "-m", "yt_dlp", "--no-warnings", *args]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "tempo esgotado"


def hms(seg):
    seg = int(seg)
    h, m, s = seg // 3600, seg % 3600 // 60, seg % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def segundos(texto):
    return sum(int(p) * 60 ** i for i, p in enumerate(reversed(str(texto).split(":"))))


def agora():
    return datetime.datetime.now(BRT).replace(microsecond=0)


def agora_iso():
    return agora().isoformat()

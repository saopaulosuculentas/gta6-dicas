"""Confere as dicas antes de publicar (português e inglês). Se aparecer ERRO, não publique: conserte e rode de novo.

Uso:  python agente/validar.py
"""
import datetime
import re
import sys
import unicodedata

import yaml

from comum import BRT, DICAS, RAIZ, utf8

DICAS_EN = RAIZ / "src" / "content" / "dicas-en"
IMG = RAIZ / "public" / "img"

CATEGORIAS = {"codigos", "easter-eggs", "segredos-e-locais", "dinheiro", "dicas", "guias"}
PS5 = {"cima", "baixo", "esquerda", "direita", "x", "circulo", "quadrado", "triangulo", "l1", "l2", "r1", "r2", "l3", "r3"}
XBOX = {"cima", "baixo", "esquerda", "direita", "a", "b", "x", "y", "lb", "lt", "rb", "rt", "ls", "rs"}
PROIBIDO = re.compile(r"mod menu|trainer|gerador de dinheiro|money generator|hack\b|crack|conta modded|modded account|free download|"
                      r"vende-?se conta|aimbot|cheat engine|download gr[áa]tis", re.I)
ONLINE = re.compile(r"gta online|modo online|multiplayer", re.I)


def chave(texto):
    t = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return " ".join(sorted(set(re.findall(r"[a-z0-9]{4,}", t))))


def data(v):
    if isinstance(v, datetime.datetime):
        return v if v.tzinfo else v.replace(tzinfo=BRT)
    return datetime.datetime.fromisoformat(str(v))


def main():
    utf8()
    erros, avisos, vistos_titulo, vistos_codigo = [], [], {}, {}
    agora = datetime.datetime.now(BRT) + datetime.timedelta(minutes=10)
    arquivos = sorted(DICAS.glob("*.md")) + sorted(DICAS_EN.glob("*.md"))
    slugs_pt = {a.stem for a in DICAS.glob("*.md")}
    for arq in arquivos:
        ingles = arq.parent == DICAS_EN
        nome = ("en/" if ingles else "") + arq.name
        texto = arq.read_text(encoding="utf-8")
        if not texto.startswith("---") or texto.count("---") < 2:
            erros.append(f"{nome}: falta o cabeçalho entre ---")
            continue
        _, cab, corpo = texto.split("---", 2)
        try:
            d = yaml.safe_load(cab)
        except yaml.YAMLError as e:
            erros.append(f"{nome}: cabeçalho quebrado ({e})")
            continue
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*\.md", arq.name):
            erros.append(f"{nome}: nome de arquivo só com letras minúsculas sem acento, números e hífen")
        for campo in ("titulo", "resumo", "categoria", "status", "fontes", "descoberto_em", "atualizado_em"):
            if not d.get(campo):
                erros.append(f"{nome}: falta '{campo}'")
        if d.get("categoria") not in CATEGORIAS:
            erros.append(f"{nome}: categoria '{d.get('categoria')}' não existe")
        fontes = d.get("fontes") or []
        canais = {str(f.get("canal", "")).strip().lower() for f in fontes}
        oficial = any(f.get("tipo") == "oficial" for f in fontes)
        if d.get("status") == "confirmado" and not (oficial or len(canais) >= 2):
            erros.append(f"{nome}: 'confirmado' exige 2 canais diferentes (ou 1 fonte oficial); tem {len(canais)}")
        if d.get("status") == "em-verificacao" and len(canais) >= 2:
            avisos.append(f"{nome}: já tem {len(canais)} canais, pode virar 'confirmado'")
        for f in fontes:
            if not re.match(r"https://", str(f.get("url", ""))):
                erros.append(f"{nome}: fonte sem link https")
            if f.get("tipo", "youtube") == "youtube" and not re.search(r"(v=|youtu\.be/|/live/|/shorts/)[\w-]{11}", str(f.get("url", ""))):
                erros.append(f"{nome}: link do YouTube sem o id do vídeo ({f.get('url')})")
            if f.get("tipo", "youtube") == "youtube" and not f.get("minuto"):
                avisos.append(f"{nome}: fonte '{f.get('canal')}' sem o minuto do vídeo")
        cod = d.get("codigo") or {}
        if d.get("categoria") == "codigos" and not cod:
            erros.append(f"{nome}: dica de código sem o campo 'codigo'")
        for console, validos in (("ps5", PS5), ("xbox", XBOX)):
            ruins = [b for b in cod.get(console) or [] if b not in validos]
            if ruins:
                erros.append(f"{nome}: botão que não existe no {console}: {ruins}")
        if cod.get("ps5") and cod.get("xbox") and len(cod["ps5"]) != len(cod["xbox"]):
            erros.append(f"{nome}: a sequência do PS5 e a do Xbox têm tamanhos diferentes")
        for campo in ("descoberto_em", "atualizado_em"):
            try:
                if d.get(campo) and data(d[campo]) > agora:
                    erros.append(f"{nome}: '{campo}' está no futuro")
            except ValueError:
                erros.append(f"{nome}: '{campo}' com data inválida")
        tudo = f"{d.get('titulo', '')} {d.get('resumo', '')} {corpo}"
        if PROIBIDO.search(tudo):
            erros.append(f"{nome}: fala de hack, trainer, gerador ou conta modificada (proibido pelo AdSense)")
        if ONLINE.search(tudo):
            avisos.append(f"{nome}: cita o modo online; confira se não ensina vantagem indevida")
        if len(corpo.strip()) < 500:
            avisos.append(f"{nome}: texto curto ({len(corpo.strip())} letras); o Google recusa página rasa, mire em 900+")
        for im in d.get("imagens") or []:
            arq_img = str(im.get("arquivo", ""))
            if not (IMG / arq_img).exists():
                erros.append(f"{nome}: imagem não encontrada em public/img/{arq_img}")
            if not im.get("canal") or not im.get("url"):
                erros.append(f"{nome}: imagem sem crédito (canal e url do vídeo)")
        if len(d.get("imagens") or []) > 3:
            erros.append(f"{nome}: mais de 3 imagens")
        if ingles:
            if d.get("pt") and d["pt"] not in slugs_pt:
                erros.append(f"{nome}: 'pt' aponta para '{d['pt']}', que não existe em src/content/dicas/")
            if re.search(r"\b(não|você|também|código|então)\b", corpo):
                avisos.append(f"{nome}: parece ter texto em português numa dica em inglês")
        if len(str(d.get("titulo_seo", ""))) > 62:
            erros.append(f"{nome}: 'titulo_seo' com mais de 62 letras")
        if "[exemplo]" in str(d.get("titulo", "")).lower():
            erros.append(f"{nome}: dica de exemplo fora da pasta exemplos/")
        k = ("en:" if ingles else "") + chave(str(d.get("titulo", "")))
        if k in vistos_titulo:
            erros.append(f"{nome}: título quase igual ao de {vistos_titulo[k]}")
        vistos_titulo[k] = nome
        if cod.get("ps5"):
            s = ("en:" if ingles else "") + " ".join(cod["ps5"])
            if s in vistos_codigo:
                erros.append(f"{nome}: mesma sequência de botões de {vistos_codigo[s]} (é a mesma dica?)")
            vistos_codigo[s] = nome

    for a in avisos:
        print(f"AVISO  {a}")
    for e in erros:
        print(f"ERRO   {e}")
    print(f"\n{len(arquivos)} dica(s) conferida(s): {len(erros)} erro(s), {len(avisos)} aviso(s)")
    if erros:
        print("NÃO PUBLIQUE. Conserte os erros e rode de novo.")
        sys.exit(1)
    print("TUDO CERTO PARA PUBLICAR.")


if __name__ == "__main__":
    main()

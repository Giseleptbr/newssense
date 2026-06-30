"""
Enriquece noticias coletadas sem resumo (ex: vindas de coleta_paginas.py)
buscando a meta description e a data de publicacao direto do <head> de
cada pagina de materia.

IMPORTANTE (direitos autorais): le apenas as tags <meta name="description">
e <meta property="article:published_time"> -- nao baixa nem armazena o
corpo do artigo. Mesmo limite de seguranca dos outros coletores.

Uso:
    python src/enriquecer_resumo.py
"""

import csv
import os
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NewsSenseBot/0.1; pesquisa academica)"}
RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "noticias.csv")


def extrair_metadados(url: str) -> dict:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
    except requests.exceptions.RequestException as e:
        print(f"  -> erro de conexao, pulando: {e.__class__.__name__}")
        return {}

    if resp.status_code != 200:
        print(f"  -> status {resp.status_code}, pulando.")
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    resultado = {}

    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        resultado["resumo_rss"] = desc["content"].strip()

    data = soup.find("meta", attrs={"property": "article:published_time"})
    if data and data.get("content"):
        resultado["data_publicacao"] = data["content"].strip()

    return resultado


def enriquecer():
    with open(RAW_PATH, newline="", encoding="utf-8") as f:
        noticias = list(csv.DictReader(f))
        fieldnames = csv.DictReader(open(RAW_PATH, encoding="utf-8")).fieldnames

    pendentes = [n for n in noticias if not n.get("resumo_rss", "").strip()]
    print(f"{len(pendentes)} noticias sem resumo para enriquecer.")

    atualizadas = 0
    for i, n in enumerate(pendentes, 1):
        print(f"[{i}/{len(pendentes)}] {n['titulo'][:60]}...")
        meta = {}
        for tentativa in range(2):  # 1 retry simples antes de desistir
            meta = extrair_metadados(n["link"])
            if meta:
                break
            time.sleep(2.0)

        if meta.get("resumo_rss"):
            n["resumo_rss"] = meta["resumo_rss"]
            atualizadas += 1
        if meta.get("data_publicacao"):
            n["data_publicacao"] = meta["data_publicacao"]

        # salva progressivamente, para nao perder trabalho se travar no meio
        with open(RAW_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(noticias)

        time.sleep(1.0)  # educado com o servidor

    print(f"\n{atualizadas}/{len(pendentes)} noticias enriquecidas com sucesso. CSV atualizado em {RAW_PATH}")


if __name__ == "__main__":
    enriquecer()

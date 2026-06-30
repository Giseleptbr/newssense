"""
Coleta incremental de noticias financeiras via RSS.

Uso:
    python src/coleta_rss.py

Armazena os itens novos em data/raw/noticias.csv (append, sem duplicar por link).
"""

import csv
import os
from datetime import datetime

import feedparser

FEEDS = {
    "infomoney_geral": "https://www.infomoney.com.br/feed/",
    "infomoney_mercados": "https://www.infomoney.com.br/mercados/feed/",
    "infomoney_onde_investir": "https://www.infomoney.com.br/onde-investir/feed/",
    "infomoney_economia": "https://www.infomoney.com.br/economia/feed/",
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "noticias.csv")
FIELDNAMES = ["fonte", "categoria", "titulo", "resumo_rss", "link", "data_publicacao", "coletado_em"]


def carregar_links_existentes(path: str) -> set:
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["link"] for row in reader}


def coletar() -> int:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    links_existentes = carregar_links_existentes(OUTPUT_PATH)
    novos = []

    for fonte, url in FEEDS.items():
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            link = entry.get("link", "")
            if not link or link in links_existentes:
                continue
            novos.append({
                "fonte": fonte,
                "categoria": fonte.split("_", 1)[1] if "_" in fonte else "geral",
                "titulo": entry.get("title", "").strip(),
                "resumo_rss": entry.get("summary", "").strip(),
                "link": link,
                "data_publicacao": entry.get("published", ""),
                "coletado_em": datetime.now().isoformat(timespec="seconds"),
            })
            links_existentes.add(link)

    if not novos:
        print("Nenhuma noticia nova encontrada.")
        return 0

    arquivo_existe = os.path.exists(OUTPUT_PATH)
    with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not arquivo_existe:
            writer.writeheader()
        writer.writerows(novos)

    print(f"{len(novos)} noticias novas adicionadas em {OUTPUT_PATH}")
    return len(novos)


if __name__ == "__main__":
    coletar()

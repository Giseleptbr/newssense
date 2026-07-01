"""
Coleta incremental de noticias financeiras via RSS.

Uso:
    python src/coleta_rss.py

Armazena os itens novos em data/raw/noticias.csv (append, sem duplicar por link).
Notícias fora do escopo financeiro (esportes, entretenimento, segurança pública etc.)
são filtradas automaticamente antes de entrar no dataset.
"""

import csv
import os
import re
from datetime import datetime

import feedparser

TAG_RE = re.compile(r"<[^>]+>")
RODAPE_RE = re.compile(r"The post .* appeared first on .*\.", re.DOTALL)

# Termos que indicam conteúdo fora do escopo financeiro BR
# Aplicado ao título da notícia (case-insensitive)
FORA_DE_ESCOPO = re.compile(
    r"\b("
    r"copa|futebol|seleção|gols?|placar|estádio|jogador|treina|escalação|campeão|semifinal|final da copa|"
    r"gramado|haaland|neymar|mbappé|messi|ronaldo|"
    r"oscar|emmy|grammy|festival|celebridade|ator|atriz|série|filme|novela|"
    r"lotérica|bilhete premiado|sorteio da mega|"
    r"terremoto|furacão|enchente|incêndio|tragédia natural|"
    r"investigação policial|pf investiga|operação policial|tráfico|homicídio|"
    r"onde assistir|como assistir|transmissão ao vivo"
    r")\b",
    re.IGNORECASE,
)


def limpar_resumo(html: str) -> str:
    """Remove tags HTML e o rodape padrao de feeds WordPress."""
    texto = RODAPE_RE.sub("", html)
    texto = TAG_RE.sub(" ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def fora_de_escopo(titulo: str) -> bool:
    """Retorna True se o titulo indica conteudo nao-financeiro."""
    return bool(FORA_DE_ESCOPO.search(titulo))

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
    filtradas = 0

    for fonte, url in FEEDS.items():
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            link = entry.get("link", "")
            if not link or link in links_existentes:
                continue
            titulo = entry.get("title", "").strip()
            if fora_de_escopo(titulo):
                filtradas += 1
                links_existentes.add(link)  # marca como visto pra nao reprocessar
                continue
            novos.append({
                "fonte": fonte,
                "categoria": fonte.split("_", 1)[1] if "_" in fonte else "geral",
                "titulo": titulo,
                "resumo_rss": limpar_resumo(entry.get("summary", "")),
                "link": link,
                "data_publicacao": entry.get("published", ""),
                "coletado_em": datetime.now().isoformat(timespec="seconds"),
            })
            links_existentes.add(link)

    if filtradas:
        print(f"{filtradas} noticias filtradas por estar fora do escopo financeiro.")
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
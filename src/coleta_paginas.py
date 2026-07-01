"""
Coleta complementar via paginas de categoria do InfoMoney (nao via RSS).

Diferente do RSS, paginas de categoria do WordPress costumam suportar
paginacao (/categoria/page/2/, /page/3/, ...), o que permite acessar
noticias um pouco mais antigas do que o RSS oferece (que so traz os
itens mais recentes).

IMPORTANTE (direitos autorais): coleta apenas titulo, link e timestamp
relativo (ex: "2 horas atras") -- nao baixa nem armazena o corpo da
materia. Mesmo limite de seguranca ja aplicado ao coletor de RSS.

Uso:
    python src/coleta_paginas.py
    python src/coleta_paginas.py --paginas 5    # varre da pagina 1 a 5

Se a paginacao nao existir ou retornar 404, o site nao suporta esse
padrao de URL e o script para sozinho (nao quebra, soh avisa).
"""

import argparse
import csv
import os
import time

import requests
from bs4 import BeautifulSoup
from coleta_rss import fora_de_escopo

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NewsSenseBot/0.1; pesquisa academica)"}

CATEGORIAS = {
    "mercados": "https://www.infomoney.com.br/mercados/",
    "onde_investir": "https://www.infomoney.com.br/onde-investir/",
    "economia": "https://www.infomoney.com.br/economia/",
}

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "noticias.csv")
FIELDNAMES = ["fonte", "categoria", "titulo", "resumo_rss", "link", "data_publicacao", "coletado_em"]


def carregar_links_existentes(path: str) -> set:
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {row["link"] for row in csv.DictReader(f)}


def montar_url_pagina(base_url: str, pagina: int) -> str:
    if pagina == 1:
        return base_url
    return base_url.rstrip("/") + f"/page/{pagina}/"


def extrair_itens(html: str, categoria: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    itens = []
    # Titulos de materia no InfoMoney aparecem em <h2> com link <a> dentro
    for h2 in soup.find_all("h2"):
        a = h2.find("a", href=True)
        if not a:
            continue
        titulo = a.get_text(strip=True)
        link = a["href"]
        if not titulo or "infomoney.com.br" not in link:
            continue
        itens.append({"titulo": titulo, "link": link, "categoria": categoria})
    return itens


def coletar(max_paginas: int = 1):
    from datetime import datetime

    links_existentes = carregar_links_existentes(OUTPUT_PATH)
    novos = []

    for categoria, base_url in CATEGORIAS.items():
        for pagina in range(1, max_paginas + 1):
            url = montar_url_pagina(base_url, pagina)
            resp = requests.get(url, headers=HEADERS, timeout=15)

            if resp.status_code == 404:
                print(f"[{categoria}] pagina {pagina}: 404 -- paginacao nao suportada, parando esta categoria.")
                break
            if resp.status_code != 200:
                print(f"[{categoria}] pagina {pagina}: status {resp.status_code}, pulando.")
                continue

            itens = extrair_itens(resp.text, categoria)
            if not itens:
                print(f"[{categoria}] pagina {pagina}: nenhum item encontrado, parando esta categoria.")
                break

            novos_nesta_pagina = 0
            for item in itens:
                if item["link"] in links_existentes:
                    continue
                if fora_de_escopo(item["titulo"]):
                    links_existentes.add(item["link"])
                    continue
                novos.append({
                    "fonte": f"infomoney_{categoria}_scraping",
                    "categoria": categoria,
                    "titulo": item["titulo"],
                    "resumo_rss": "",  # paginas de categoria nao trazem resumo, soh titulo
                    "link": item["link"],
                    "data_publicacao": "",  # nao disponivel de forma estruturada nesta fonte
                    "coletado_em": datetime.now().isoformat(timespec="seconds"),
                })
                links_existentes.add(item["link"])
                novos_nesta_pagina += 1

            print(f"[{categoria}] pagina {pagina}: {len(itens)} itens na pagina, {novos_nesta_pagina} novos.")
            time.sleep(1.5)  # educado com o servidor, evita sobrecarregar

    if not novos:
        print("\nNenhuma noticia nova encontrada no total.")
        return 0

    arquivo_existe = os.path.exists(OUTPUT_PATH)
    with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not arquivo_existe:
            writer.writeheader()
        writer.writerows(novos)

    print(f"\n{len(novos)} noticias novas adicionadas em {OUTPUT_PATH}")
    return len(novos)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--paginas", type=int, default=1, help="numero de paginas a varrer por categoria")
    args = parser.parse_args()
    coletar(max_paginas=args.paginas)

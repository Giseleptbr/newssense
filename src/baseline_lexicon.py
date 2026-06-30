"""
Baseline de sentimento via lexicon (OpLexicon v3.0).

Classifica cada noticia (titulo + resumo) somando a polaridade das palavras
encontradas no lexicon. Sem nenhum ajuste de dominio financeiro -- e exatamente
por isso que serve de baseline de comparacao para o modelo principal (Secao 3.3
da proposta).

Uso:
    python src/baseline_lexicon.py
"""

import csv
import os
import re
import unicodedata

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "noticias.csv")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "rotulos.csv")
LEXICON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "lexicon_oplexicon.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "baseline_lexicon_resultado.csv")

TOKEN_RE = re.compile(r"[a-zà-ú]+", re.IGNORECASE)


def normalizar(texto: str) -> str:
    """Remove acentos e baixa a caixa, para casar com o lexicon."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def carregar_lexicon() -> dict:
    lex = {}
    with open(LEXICON_PATH, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 3:
                continue
            termo, _tipo, polaridade = row[0], row[1], row[2]
            try:
                lex[normalizar(termo)] = int(polaridade)
            except ValueError:
                continue
    return lex


def classificar(texto: str, lexicon: dict) -> str:
    tokens = TOKEN_RE.findall(normalizar(texto))
    score = sum(lexicon.get(tok, 0) for tok in tokens)
    if score > 0:
        return "positivo"
    if score < 0:
        return "negativo"
    return "neutro"


def carregar_rotulos() -> dict:
    """Retorna {link: sentimento_manual}."""
    if not os.path.exists(LABELS_PATH):
        return {}
    with open(LABELS_PATH, newline="", encoding="utf-8") as f:
        return {row["link"]: row["sentimento"] for row in csv.DictReader(f)}


def avaliar():
    lexicon = carregar_lexicon()
    rotulos = carregar_rotulos()
    print(f"Lexicon carregado: {len(lexicon)} termos.")
    print(f"Rotulos manuais disponiveis: {len(rotulos)}.")

    with open(RAW_PATH, newline="", encoding="utf-8") as f:
        noticias = list(csv.DictReader(f))

    resultados = []
    acertos = 0
    avaliados = 0

    for n in noticias:
        texto = f"{n['titulo']} {n['resumo_rss']}"
        pred = classificar(texto, lexicon)
        manual = rotulos.get(n["link"])
        if manual:
            avaliados += 1
            if manual == pred:
                acertos += 1
        resultados.append({
            "titulo": n["titulo"],
            "predicao_lexicon": pred,
            "rotulo_manual": manual or "",
        })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "predicao_lexicon", "rotulo_manual"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nResultado salvo em {OUTPUT_PATH}")
    if avaliados > 0:
        acc = acertos / avaliados
        print(f"Accuracy do baseline (vs. rotulo manual): {acc:.2%} ({acertos}/{avaliados})")
    else:
        print("Nenhuma noticia com rotulo manual ainda para comparar.")


if __name__ == "__main__":
    avaliar()

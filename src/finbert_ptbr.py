"""
Classificador de sentimento via FinBERT-PT-BR (lucas-leme/FinBERT-PT-BR).

Modelo treinado especificamente em 1.4 milhao de textos de noticias
financeiras em portugues -- o mais adequado ao dominio do projeto.

Classes: POSITIVE (0), NEGATIVE (1), NEUTRAL (2)

Uso:
    python src/finbert_ptbr.py

Primeira execucao baixa o modelo (~400MB). Subsequentes usam cache local.
"""

import csv
import os

from transformers import AutoTokenizer, BertForSequenceClassification, pipeline

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "noticias.csv")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "rotulos.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "finbert_ptbr_resultado.csv")

MODELO = "lucas-leme/FinBERT-PT-BR"

MAPA_LABEL = {
    "POSITIVE": "positivo",
    "NEGATIVE": "negativo",
    "NEUTRAL": "neutro",
    "LABEL_0": "positivo",
    "LABEL_1": "negativo",
    "LABEL_2": "neutro",
}


def carregar_rotulos() -> dict:
    if not os.path.exists(LABELS_PATH):
        return {}
    with open(LABELS_PATH, newline="", encoding="utf-8") as f:
        return {row["link"]: row["sentimento"] for row in csv.DictReader(f)}


def avaliar():
    print(f"Carregando modelo {MODELO}...")
    tokenizer = AutoTokenizer.from_pretrained(MODELO)
    model = BertForSequenceClassification.from_pretrained(MODELO)
    classificador = pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
    )

    rotulos = carregar_rotulos()
    print(f"Rotulos manuais disponiveis: {len(rotulos)}.")

    with open(RAW_PATH, newline="", encoding="utf-8") as f:
        noticias = list(csv.DictReader(f))

    resultados = []
    acertos = 0
    avaliados = 0

    for n in noticias:
        texto = f"{n['titulo']} {n['resumo_rss']}"[:512]
        saida = classificador(texto)[0]
        pred = MAPA_LABEL.get(saida["label"].upper(), saida["label"])
        confianca = saida["score"]

        manual = rotulos.get(n["link"])
        if manual:
            avaliados += 1
            if manual == pred:
                acertos += 1

        resultados.append({
            "titulo": n["titulo"],
            "predicao_finbert": pred,
            "confianca": f"{confianca:.3f}",
            "rotulo_manual": manual or "",
        })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "predicao_finbert", "confianca", "rotulo_manual"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nResultado salvo em {OUTPUT_PATH}")
    if avaliados > 0:
        acc = acertos / avaliados
        print(f"Accuracy FinBERT-PT-BR (vs. rotulo manual): {acc:.2%} ({acertos}/{avaliados})")
    else:
        print("Nenhuma noticia com rotulo manual ainda para comparar.")


if __name__ == "__main__":
    avaliar()

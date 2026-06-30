"""
Classificador de sentimento via modelo pre-treinado multilingue (zero-shot,
sem fine-tuning). Compara contra o baseline de lexicon e contra os rotulos
manuais.

Modelo: cardiffnlp/twitter-xlm-roberta-base-sentiment
- Treinado em tweets multilingues (incluindo portugues), 3 classes:
  negative / neutral / positive.
- Nao foi ajustado especificamente para dominio financeiro -- e por isso
  ainda nao e o "modelo principal" da proposta, mas serve como segunda
  referencia de comparacao mais forte que o lexicon puro.

Uso:
    python src/zero_shot_sentimento.py

Primeira execucao baixa o modelo (~1.1 GB) -- pode demorar alguns minutos.
"""

import csv
import os

from transformers import pipeline

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "noticias.csv")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "rotulos.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "zero_shot_resultado.csv")

MODELO = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

MAPA_LABEL = {
    "negative": "negativo",
    "neutral": "neutro",
    "positive": "positivo",
}


def carregar_rotulos() -> dict:
    if not os.path.exists(LABELS_PATH):
        return {}
    with open(LABELS_PATH, newline="", encoding="utf-8") as f:
        return {row["link"]: row["sentimento"] for row in csv.DictReader(f)}


def avaliar():
    print(f"Carregando modelo {MODELO}...")
    classificador = pipeline("sentiment-analysis", model=MODELO, tokenizer=MODELO)

    rotulos = carregar_rotulos()
    print(f"Rotulos manuais disponiveis: {len(rotulos)}.")

    with open(RAW_PATH, newline="", encoding="utf-8") as f:
        noticias = list(csv.DictReader(f))

    resultados = []
    acertos = 0
    avaliados = 0

    for n in noticias:
        texto = f"{n['titulo']} {n['resumo_rss']}"[:512]  # limite de tokens do modelo
        saida = classificador(texto)[0]
        pred = MAPA_LABEL.get(saida["label"].lower(), saida["label"])
        confianca = saida["score"]

        manual = rotulos.get(n["link"])
        if manual:
            avaliados += 1
            if manual == pred:
                acertos += 1

        resultados.append({
            "titulo": n["titulo"],
            "predicao_zero_shot": pred,
            "confianca": f"{confianca:.3f}",
            "rotulo_manual": manual or "",
        })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "predicao_zero_shot", "confianca", "rotulo_manual"])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"\nResultado salvo em {OUTPUT_PATH}")
    if avaliados > 0:
        acc = acertos / avaliados
        print(f"Accuracy zero-shot (vs. rotulo manual): {acc:.2%} ({acertos}/{avaliados})")
    else:
        print("Nenhuma noticia com rotulo manual ainda para comparar.")


if __name__ == "__main__":
    avaliar()

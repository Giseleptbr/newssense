"""
Ensemble: combina predicoes do baseline (OpLexicon), FinBERT-PT-BR e
zero-shot multilingue.

Estrategias testadas:
1. Maioria (3 modelos): se 2 ou mais concordam, usa esse voto
2. Lexicon-priority: quando Lexicon e FinBERT divergem, usa Lexicon
3. FinBERT-priority: quando divergem, usa FinBERT (confianca mais alta)

Requer que os tres scripts de modelo ja tenham sido rodados.

Uso:
    python src/ensemble.py
"""

import csv
import os
from collections import Counter

LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "rotulos.csv")
LEXICON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "baseline_lexicon_resultado.csv")
FINBERT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "finbert_ptbr_resultado.csv")
ZEROSHOT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "zero_shot_resultado.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "ensemble_resultado.csv")


def carregar_csv(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {r["titulo"]: r for r in csv.DictReader(f)}


def maioria(votos: list) -> str:
    contagem = Counter(votos)
    return contagem.most_common(1)[0][0]


def avaliar():
    rotulos_raw = {}
    if os.path.exists(LABELS_PATH):
        with open(LABELS_PATH, newline="", encoding="utf-8") as f:
            rotulos_raw = {r["titulo"]: r["sentimento"] for r in csv.DictReader(f)}

    lexicon = carregar_csv(LEXICON_PATH)
    finbert = carregar_csv(FINBERT_PATH)
    zeroshot = carregar_csv(ZEROSHOT_PATH)

    titulos = list(lexicon.keys())
    resultados = []

    contadores = {
        "maioria_3": 0,
        "lexicon_priority": 0,
        "finbert_priority": 0,
    }
    avaliados = 0

    for titulo in titulos:
        lex_pred = lexicon.get(titulo, {}).get("predicao_lexicon", "neutro")
        fin_pred = finbert.get(titulo, {}).get("predicao_finbert", "neutro")
        zs_pred = zeroshot.get(titulo, {}).get("predicao_zero_shot", "neutro")

        pred_maioria = maioria([lex_pred, fin_pred, zs_pred])
        pred_lex_priority = lex_pred if lex_pred != fin_pred else fin_pred
        pred_fin_priority = fin_pred if lex_pred != fin_pred else lex_pred

        manual = rotulos_raw.get(titulo, "")
        if manual:
            avaliados += 1
            if pred_maioria == manual:
                contadores["maioria_3"] += 1
            if pred_lex_priority == manual:
                contadores["lexicon_priority"] += 1
            if pred_fin_priority == manual:
                contadores["finbert_priority"] += 1

        resultados.append({
            "titulo": titulo,
            "predicao_lexicon": lex_pred,
            "predicao_finbert": fin_pred,
            "predicao_zeroshot": zs_pred,
            "ensemble_maioria": pred_maioria,
            "ensemble_lex_priority": pred_lex_priority,
            "ensemble_fin_priority": pred_fin_priority,
            "rotulo_manual": manual,
        })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "titulo", "predicao_lexicon", "predicao_finbert", "predicao_zeroshot",
            "ensemble_maioria", "ensemble_lex_priority", "ensemble_fin_priority",
            "rotulo_manual"
        ])
        writer.writeheader()
        writer.writerows(resultados)

    print(f"Ensemble calculado para {len(titulos)} noticias.")
    print(f"Resultado salvo em {OUTPUT_PATH}")

    if avaliados > 0:
        n = avaliados
        ac_lex = sum(1 for r in resultados if r["rotulo_manual"] and r["predicao_lexicon"] == r["rotulo_manual"])
        ac_fin = sum(1 for r in resultados if r["rotulo_manual"] and r["predicao_finbert"] == r["rotulo_manual"])
        ac_zs = sum(1 for r in resultados if r["rotulo_manual"] and r["predicao_zeroshot"] == r["rotulo_manual"])

        print(f"\n{'Modelo':<30} {'Accuracy':>10} {'Acertos':>10}")
        print("-" * 52)
        print(f"{'Lexicon (baseline)':<30} {ac_lex/n:>10.2%} {ac_lex:>7}/{n}")
        print(f"{'FinBERT-PT-BR':<30} {ac_fin/n:>10.2%} {ac_fin:>7}/{n}")
        print(f"{'Zero-shot multilingue':<30} {ac_zs/n:>10.2%} {ac_zs:>7}/{n}")
        print("-" * 52)
        for nome, chave in [
            ("Ensemble maioria (3 modelos)", "maioria_3"),
            ("Ensemble lex-priority", "lexicon_priority"),
            ("Ensemble fin-priority", "finbert_priority"),
        ]:
            acc = contadores[chave] / n
            print(f"{'> ' + nome:<30} {acc:>10.2%} {contadores[chave]:>7}/{n}")


if __name__ == "__main__":
    avaliar()

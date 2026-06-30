"""
Ferramenta de rotulagem manual de sentimento.

Mostra cada noticia ainda nao rotulada (titulo + resumo) e pede que voce
classifique manualmente: positivo (p), negativo (n) ou neutro (z).
Pode interromper a qualquer momento (Ctrl+C) e retomar depois de onde parou.

Uso:
    python src/rotular.py
"""

import csv
import os

RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "noticias.csv")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "rotulos.csv")

MAPA = {"p": "positivo", "n": "negativo", "z": "neutro"}


def carregar_rotulados() -> set:
    if not os.path.exists(LABELS_PATH):
        return set()
    with open(LABELS_PATH, newline="", encoding="utf-8") as f:
        return {row["link"] for row in csv.DictReader(f)}


def rotular():
    os.makedirs(os.path.dirname(LABELS_PATH), exist_ok=True)
    ja_rotulados = carregar_rotulados()

    with open(RAW_PATH, newline="", encoding="utf-8") as f:
        noticias = list(csv.DictReader(f))

    pendentes = [n for n in noticias if n["link"] not in ja_rotulados]
    if not pendentes:
        print("Nada pendente. Todas as noticias coletadas ja foram rotuladas.")
        return

    print(f"{len(pendentes)} noticias pendentes de rotulagem. {len(ja_rotulados)} ja rotuladas.")
    print("Comandos: [p] positivo  [n] negativo  [z] neutro  [s] pular  [q] sair\n")

    arquivo_existe = os.path.exists(LABELS_PATH)
    with open(LABELS_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["link", "titulo", "sentimento"])
        if not arquivo_existe:
            writer.writeheader()

        for i, noticia in enumerate(pendentes, 1):
            print(f"--- [{i}/{len(pendentes)}] {noticia['categoria']} ---")
            print(noticia["titulo"])
            print(noticia["resumo_rss"][:300])
            resposta = input("Sentimento [p/n/z/s/q]: ").strip().lower()

            if resposta == "q":
                print("Encerrando. Progresso salvo.")
                break
            if resposta == "s":
                print()
                continue
            if resposta not in MAPA:
                print("Comando invalido, pulando esta noticia.\n")
                continue

            writer.writerow({
                "link": noticia["link"],
                "titulo": noticia["titulo"],
                "sentimento": MAPA[resposta],
            })
            f.flush()
            print(f"-> Salvo como {MAPA[resposta]}.\n")


if __name__ == "__main__":
    rotular()

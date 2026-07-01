"""
Fine-tuning do FinBERT-PT-BR (lucas-leme/FinBERT-PT-BR) com os rotulos
manuais coletados neste projeto.

O fine-tuning alinha o modelo ao criterio de rotulagem especifico do
NewsSense ("estado presente + acao corretiva = positivo"), que difere
do criterio padrao com que o modelo foi originalmente treinado.

Uso:
    python src/finetuning.py

Saida:
    models/finbert_newssense/   <- modelo fine-tuned salvo aqui
    data/processed/finetuning_resultados.csv <- predicoes no conjunto de teste

Requisitos:
    pip install transformers torch scikit-learn
"""

import csv
import os
import random

import torch
from sklearn.metrics import classification_report, f1_score
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments,
)

# Caminhos
RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "noticias.csv")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "rotulos.csv")
MODEL_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "models", "finbert_newssense")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "finetuning_resultados.csv")

MODELO_BASE = "lucas-leme/FinBERT-PT-BR"
SEED = 42
TEST_SIZE = 0.2  # 20% para teste, 80% para treino

LABEL2ID = {"positivo": 0, "negativo": 1, "neutro": 2}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}

random.seed(SEED)
torch.manual_seed(SEED)


class NoticiasDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def carregar_dados():
    """Une noticias com rotulos manuais."""
    noticias = {}
    with open(RAW_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            noticias[row["link"]] = f"{row['titulo']} {row['resumo_rss']}"

    dados = []
    with open(LABELS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            texto = noticias.get(row["link"], row["titulo"])
            label = LABEL2ID.get(row["sentimento"])
            if label is not None:
                dados.append({"texto": texto[:512], "label": label, "link": row["link"]})

    return dados


def split_dados(dados, test_size=TEST_SIZE):
    random.shuffle(dados)
    n_test = max(1, int(len(dados) * test_size))
    return dados[n_test:], dados[:n_test]


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(axis=-1)
    f1 = f1_score(labels, preds, average="macro")
    acc = (preds == labels).mean()
    return {"f1_macro": f1, "accuracy": acc}


def treinar():
    print(f"Carregando dados...")
    dados = carregar_dados()
    print(f"Total de exemplos rotulados: {len(dados)}")

    treino, teste = split_dados(dados)
    print(f"Treino: {len(treino)} | Teste: {len(teste)}")

    print(f"\nCarregando modelo base {MODELO_BASE}...")
    tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE)
    model = BertForSequenceClassification.from_pretrained(
        MODELO_BASE,
        num_labels=3,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        ignore_mismatched_sizes=True,
    )

    textos_treino = [d["texto"] for d in treino]
    labels_treino = [d["label"] for d in treino]
    textos_teste = [d["texto"] for d in teste]
    labels_teste = [d["label"] for d in teste]

    enc_treino = tokenizer(textos_treino, truncation=True, padding=True, max_length=128)
    enc_teste = tokenizer(textos_teste, truncation=True, padding=True, max_length=128)

    ds_treino = NoticiasDataset(enc_treino, labels_treino)
    ds_teste = NoticiasDataset(enc_teste, labels_teste)

    # Detecta dispositivo: MPS (Apple Silicon) > CUDA > CPU
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    print(f"Dispositivo: {device}")

    os.makedirs(MODEL_OUTPUT, exist_ok=True)

    args = TrainingArguments(
        output_dir=MODEL_OUTPUT,
        num_train_epochs=5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        learning_rate=2e-5,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
        seed=SEED,
        logging_steps=10,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds_treino,
        eval_dataset=ds_teste,
        compute_metrics=compute_metrics,
    )

    print("\nIniciando fine-tuning...")
    trainer.train()

    print("\nAvaliando no conjunto de teste...")
    preds_output = trainer.predict(ds_teste)
    preds = preds_output.predictions.argmax(axis=-1)

    print("\n" + "=" * 50)
    print("RESULTADO FINAL NO CONJUNTO DE TESTE")
    print("=" * 50)
    print(classification_report(
        labels_teste, preds,
        target_names=["positivo", "negativo", "neutro"]
    ))

    f1 = f1_score(labels_teste, preds, average="macro")
    print(f"F1-macro: {f1:.4f}")
    print(f"Meta da proposta: >= 0.70")
    print(f"Status: {'ATINGIDA' if f1 >= 0.70 else 'NAO ATINGIDA (continuar rotulando)'}")

    # Salva predicoes
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)
    with open(RESULTS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "rotulo_manual", "predicao_finetuned"])
        writer.writeheader()
        for i, d in enumerate(teste):
            writer.writerow({
                "titulo": d["texto"][:80],
                "rotulo_manual": ID2LABEL[d["label"]],
                "predicao_finetuned": ID2LABEL[preds[i]],
            })

    print(f"\nPredicoes salvas em {RESULTS_PATH}")

    # Salva modelo
    trainer.save_model(MODEL_OUTPUT)
    tokenizer.save_pretrained(MODEL_OUTPUT)
    print(f"Modelo salvo em {MODEL_OUTPUT}")


if __name__ == "__main__":
    treinar()

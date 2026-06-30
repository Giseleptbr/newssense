"""
Rotina diaria de coleta: roda RSS + paginas de categoria + enriquecimento
de resumo, em sequencia, com um resumo final do que foi feito.

Uso:
    python src/rotina_diaria.py
"""

import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).parent


def rodar(script: str, *args: str) -> bool:
    print(f"\n{'=' * 60}")
    print(f"Executando {script} {' '.join(args)}")
    print("=" * 60)
    resultado = subprocess.run([sys.executable, str(SRC_DIR / script), *args])
    return resultado.returncode == 0


def main():
    etapas_ok = []

    etapas_ok.append(("coleta_rss.py", rodar("coleta_rss.py")))
    etapas_ok.append(("coleta_paginas.py", rodar("coleta_paginas.py", "--paginas", "1")))
    etapas_ok.append(("enriquecer_resumo.py", rodar("enriquecer_resumo.py")))

    print(f"\n{'=' * 60}")
    print("RESUMO DA ROTINA")
    print("=" * 60)
    for nome, ok in etapas_ok:
        status = "OK" if ok else "FALHOU"
        print(f"  [{status}] {nome}")

    print("\nProximo passo sugerido: python src/rotular.py")


if __name__ == "__main__":
    main()

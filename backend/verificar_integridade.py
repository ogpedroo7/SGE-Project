import sqlite3
from pathlib import Path

caminho = Path(__file__).parent / "SGE.db"

conexao = sqlite3.connect(
    f"file:{caminho.resolve().as_posix()}?mode=ro",
    uri=True
)

print("Integridade do arquivo:")
print(conexao.execute("PRAGMA integrity_check").fetchone()[0])

print("\nRelacionamentos inválidos:")
problemas = conexao.execute("PRAGMA foreign_key_check").fetchall()

if problemas:
    for problema in problemas:
        print(problema)
else:
    print("Nenhum relacionamento inválido encontrado.")

conexao.close()

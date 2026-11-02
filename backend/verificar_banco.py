import sqlite3
from pathlib import Path

caminho = Path(__file__).parent / "SGE.db"
conexao = sqlite3.connect(
    f"file:{caminho.resolve().as_posix()}?mode=ro",
    uri=True
)

tabelas = conexao.execute(
    "SELECT name FROM sqlite_master "
    "WHERE type = ? AND name NOT LIKE ? "
    "ORDER BY name",
    ("table", "sqlite_%")
).fetchall()

for (tabela,) in tabelas:
    print(f"\n--- {tabela} ---")

    colunas = conexao.execute(
        f'PRAGMA table_info("{tabela}")'
    ).fetchall()

    for coluna in colunas:
        print(f"Coluna: {coluna[1]} | Tipo: {coluna[2]}")

    chaves = conexao.execute(
        f'PRAGMA foreign_key_list("{tabela}")'
    ).fetchall()

    for chave in chaves:
        print(f"Relacionamento: {chave[3]} -> {chave[2]}.{chave[4]}")

conexao.close()

import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent / "SGE.db"


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabelas():
    with conectar_banco() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS progresso_estudos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                materia TEXT NOT NULL UNIQUE,
                horas_estudadas REAL NOT NULL DEFAULT 0,
                progresso INTEGER NOT NULL DEFAULT 0,
                nivel INTEGER NOT NULL DEFAULT 1
            )
        """)


if __name__ == "__main__":
    criar_tabelas()
    print("Banco de dados do SGE preparado!")

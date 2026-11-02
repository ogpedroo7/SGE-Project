import sqlite3
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent / "SGE.db"


def conectar_banco():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
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

        # Preserva a estrutura antiga, caso ela ainda exista.
        tabela = conexao.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table'
              AND name = 'progresso_estudos'
        """).fetchone()

        if tabela:
            colunas = {
                linha["name"]
                for linha in conexao.execute(
                    "PRAGMA table_info(progresso_estudos)"
                ).fetchall()
            }

            if "usuario_id" not in colunas:
                conexao.execute("""
                    ALTER TABLE progresso_estudos
                    RENAME TO progresso_estudos_legado
                """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS progresso_estudos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                materia TEXT NOT NULL,
                horas_estudadas REAL NOT NULL DEFAULT 0,
                progresso INTEGER NOT NULL DEFAULT 0,
                nivel INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id),
                UNIQUE (usuario_id, materia)
            )
        """)

        # Estado atual do curso de cada usuário.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS progresso_aulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                materia TEXT NOT NULL,
                nivel INTEGER NOT NULL DEFAULT 1
                    CHECK (nivel BETWEEN 1 AND 10),
                pagina INTEGER NOT NULL DEFAULT 1
                    CHECK (pagina BETWEEN 1 AND 10),
                paginas_concluidas TEXT NOT NULL DEFAULT '[]',
                segundos_estudados INTEGER NOT NULL DEFAULT 0
                    CHECK (segundos_estudados >= 0),
                atualizado_em TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id),
                UNIQUE (usuario_id, materia)
            )
        """)

        # Respostas únicas por questão de quiz.
        # Uma questão acertada permanece acertada
        # nas tentativas de recuperação.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS respostas_quiz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                materia TEXT NOT NULL,
                nivel INTEGER NOT NULL
                    CHECK (nivel BETWEEN 1 AND 10),
                questao_id TEXT NOT NULL,
                resposta TEXT NOT NULL,
                acertou INTEGER NOT NULL
                    CHECK (acertou IN (0, 1)),
                respondido_em TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id),
                UNIQUE (
                    usuario_id,
                    materia,
                    nivel,
                    questao_id
                )
            )
        """)

        # Controle de conclusão e aprovação de cada nível.
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS niveis_curso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                materia TEXT NOT NULL,
                nivel INTEGER NOT NULL
                    CHECK (nivel BETWEEN 1 AND 10),
                resumo_concluido INTEGER NOT NULL DEFAULT 0
                    CHECK (resumo_concluido IN (0, 1)),
                aprovado INTEGER NOT NULL DEFAULT 0
                    CHECK (aprovado IN (0, 1)),
                atualizado_em TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id),
                UNIQUE (usuario_id, materia, nivel)
            )
        """)


if __name__ == "__main__":
    criar_tabelas()
    print("Banco de dados do SGE preparado!")

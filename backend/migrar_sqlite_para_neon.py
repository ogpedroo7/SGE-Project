"""
Migra os dados do banco SQLite local do SGE para o PostgreSQL/Neon.

Uso, a partir da raiz do repositório:
    python -m backend.migrar_sqlite_para_neon

Pré-requisitos:
- DATABASE_URL configurada no ambiente, sem compartilhá-la.
- backend/SGE.db presente.
- Executar primeiro em um banco Neon vazio ou em um banco revisado.
O script não apaga dados no SQLite e não migra a tabela legada
progresso_estudos_legado, pois ela não faz parte do esquema ativo.
"""

import os
import sqlite3
import sys
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


BASE_DIR = Path(__file__).resolve().parent
CAMINHO_SQLITE = BASE_DIR / "SGE.db"

# Ordem respeita as chaves estrangeiras. IDs são preservados.
TABELAS = {
    "usuarios": [
        "id", "nome", "email", "senha_hash",
    ],
    "progresso_estudos": [
        "id", "usuario_id", "materia", "horas_estudadas",
        "progresso", "nivel",
    ],
    "progresso_aulas": [
        "id", "usuario_id", "materia", "nivel", "pagina",
        "paginas_concluidas", "segundos_estudados", "atualizado_em",
    ],
    "respostas_quiz": [
        "id", "usuario_id", "materia", "nivel", "questao_id",
        "resposta", "acertou", "respondido_em",
    ],
    "niveis_curso": [
        "id", "usuario_id", "materia", "nivel",
        "resumo_concluido", "aprovado", "atualizado_em",
    ],
}


def conectar_neon():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL não está configurada. Configure-a no ambiente "
            "local antes de executar a migração; não coloque a senha no código."
        )
    return psycopg.connect(url, row_factory=dict_row, connect_timeout=10)


def tabelas_sqlite(conexao):
    linhas = conexao.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    return {linha["name"] for linha in linhas}


def colunas_sqlite(conexao, tabela):
    return {
        linha["name"]
        for linha in conexao.execute(
            f'PRAGMA table_info("{tabela}")'
        ).fetchall()
    }


def migrar():
    if not CAMINHO_SQLITE.is_file():
        raise FileNotFoundError(
            f"Banco de origem não encontrado: {CAMINHO_SQLITE}"
        )

    with sqlite3.connect(CAMINHO_SQLITE) as sqlite_conn:
        sqlite_conn.row_factory = sqlite3.Row
        existentes = tabelas_sqlite(sqlite_conn)

        faltantes = [
            nome for nome in TABELAS
            if nome not in existentes
        ]
        if faltantes:
            raise RuntimeError(
                "O SQLite não contém as tabelas esperadas: "
                + ", ".join(faltantes)
                + ". Nenhum dado foi migrado."
            )

        dados = {}
        for tabela, colunas_esperadas in TABELAS.items():
            colunas_disponiveis = colunas_sqlite(sqlite_conn, tabela)
            faltam_colunas = [
                coluna for coluna in colunas_esperadas
                if coluna not in colunas_disponiveis
            ]
            if faltam_colunas:
                raise RuntimeError(
                    f"A tabela SQLite {tabela} não contém as colunas: "
                    + ", ".join(faltam_colunas)
                    + ". Nenhum dado foi migrado."
                )

            nomes = ", ".join(f'"{c}"' for c in colunas_esperadas)
            linhas = sqlite_conn.execute(
                f'SELECT {nomes} FROM "{tabela}" ORDER BY id'
            ).fetchall()
            dados[tabela] = [
                {coluna: linha[coluna] for coluna in colunas_esperadas}
                for linha in linhas
            ]

    totais = {tabela: len(linhas) for tabela, linhas in dados.items()}

    with conectar_neon() as pg:
        # Valida o esquema antes de escrever qualquer registro.
        tabelas_pg = {
            linha["table_name"]
            for linha in pg.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """
            ).fetchall()
        }
        faltantes_pg = [t for t in TABELAS if t not in tabelas_pg]
        if faltantes_pg:
            raise RuntimeError(
                "As tabelas do Neon ainda não existem: "
                + ", ".join(faltantes_pg)
                + ". Configure DATABASE_URL e inicialize o esquema primeiro."
            )

        for tabela, linhas in dados.items():
            if not linhas:
                continue

            colunas = list(linhas[0].keys())
            nomes = ", ".join(f'"{c}"' for c in colunas)
            marcadores = ", ".join(["%s"] * len(colunas))
            sql = (
                f'INSERT INTO "{tabela}" ({nomes}) '
                f'VALUES ({marcadores}) ON CONFLICT DO NOTHING'
            )

            for linha in linhas:
                pg.execute(sql, tuple(linha[c] for c in colunas))

        # IDs foram preservados; sincroniza sequências para novos cadastros.
        for tabela in TABELAS:
            pg.execute(
                """
                SELECT setval(
                    pg_get_serial_sequence(%s, 'id'),
                    GREATEST(COALESCE((SELECT MAX(id) FROM """
                + f'"{tabela}"' +
                """), 1), 1),
                    COALESCE((SELECT MAX(id) FROM """
                + f'"{tabela}"' +
                """) IS NOT NULL)
                )
                """,
                (f"public.{tabela}",),
            )

        # Conta os registros após os inserts e valida que todos existem.
        totais_pg = {}
        for tabela, esperado in totais.items():
            total_pg = pg.execute(
                f'SELECT COUNT(*) AS total FROM "{tabela}"'
            ).fetchone()["total"]
            totais_pg[tabela] = total_pg
            if total_pg < esperado:
                raise RuntimeError(
                    f"Validação falhou em {tabela}: SQLite tem {esperado}, "
                    f"Neon tem {total_pg}. A transação será revertida."
                )

    print("Migração concluída. Contagens verificadas:")
    for tabela in TABELAS:
        print(
            f"- {tabela}: {totais[tabela]} registros no SQLite; "
            f"{totais_pg[tabela]} no Neon"
        )
    print("O arquivo SQLite original foi mantido intacto.")


if __name__ == "__main__":
    try:
        migrar()
    except Exception as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        sys.exit(1)

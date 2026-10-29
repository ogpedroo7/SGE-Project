import hashlib
import hmac
import secrets

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from backend.database import conectar_banco, criar_tabelas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


criar_tabelas()


class CadastroUsuario(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    senha: str = Field(min_length=8, max_length=128)


class LoginUsuario(BaseModel):
    email: str
    senha: str


class AtualizacaoProgresso(BaseModel):
    horas_estudadas: float = Field(ge=0)
    progresso: int = Field(ge=0, le=100)


def gerar_hash_senha(senha: str) -> str:
    salt = secrets.token_bytes(16)
    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        600_000
    )
    return salt.hex() + ":" + resultado.hex()


def verificar_senha(senha: str, senha_hash: str) -> bool:
    salt_hex, hash_salvo = senha_hash.split(":")
    salt = bytes.fromhex(salt_hex)

    resultado = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        600_000
    )

    return hmac.compare_digest(resultado.hex(), hash_salvo)


@app.get("/status")
def verificar_status():
    return {"mensagem": "StudyCore está funcionando!"}


@app.post("/usuarios/cadastro", status_code=201)
def cadastrar_usuario(dados: CadastroUsuario):
    nome = dados.nome.strip()
    email = dados.email.strip().lower()

    if len(nome) < 2 or "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(
            status_code=400,
            detail="Informe um nome e um e-mail válidos."
        )

    senha_hash = gerar_hash_senha(dados.senha)

    try:
        with conectar_banco() as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash)
                VALUES (?, ?, ?)
                """,
                (nome, email, senha_hash)
            )
            usuario_id = cursor.lastrowid
    except Exception as erro:
        if "UNIQUE constraint failed" in str(erro):
            raise HTTPException(
                status_code=409,
                detail="Este e-mail já está cadastrado."
            )
        raise

    return {
        "mensagem": "Conta criada com sucesso!",
        "usuario": {
            "id": usuario_id,
            "nome": nome,
            "email": email
        }
    }


@app.post("/usuarios/login")
def login_usuario(dados: LoginUsuario):
    email = dados.email.strip().lower()

    with conectar_banco() as conexao:
        usuario = conexao.execute(
            """
            SELECT id, nome, email, senha_hash
            FROM usuarios
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    if usuario is None or not verificar_senha(
        dados.senha, usuario["senha_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos."
        )

    return {
        "mensagem": "Login realizado com sucesso!",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"]
        }
    }


@app.get("/python/progresso")
def obter_progresso_python():
    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT OR IGNORE INTO progresso_estudos (materia)
            VALUES (?)
            """,
            ("Python",)
        )

        registro = conexao.execute(
            """
            SELECT materia, horas_estudadas, progresso, nivel
            FROM progresso_estudos
            WHERE materia = ?
            """,
            ("Python",)
        ).fetchone()

    return dict(registro)


@app.put("/python/progresso")
def atualizar_progresso(dados: AtualizacaoProgresso):
    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT OR IGNORE INTO progresso_estudos (materia)
            VALUES (?)
            """,
            ("Python",)
        )

        conexao.execute(
            """
            UPDATE progresso_estudos
            SET horas_estudadas = ?, progresso = ?
            WHERE materia = ?
            """,
            (dados.horas_estudadas, dados.progresso, "Python")
        )

        registro = conexao.execute(
            """
            SELECT materia, horas_estudadas, progresso, nivel
            FROM progresso_estudos
            WHERE materia = ?
            """,
            ("Python",)
        ).fetchone()

    return dict(registro)

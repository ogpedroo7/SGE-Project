
import os
import secrets

# Configura uma chave exclusiva para os testes locais.
os.environ["STUDYCORE_SECRET_KEY"] = secrets.token_urlsafe(48)

# Impede a criação de tabelas durante a importação da API.
import backend.database as database
database.criar_tabelas = lambda: None

from fastapi import HTTPException
from fastapi.testclient import TestClient
from backend import api


def test_hash_verifica_senha_correta():
    senha_hash = api.gerar_hash_senha("SenhaForte123!")
    assert api.verificar_senha("SenhaForte123!", senha_hash)


def test_hash_rejeita_senha_incorreta():
    senha_hash = api.gerar_hash_senha("SenhaForte123!")
    assert not api.verificar_senha("SenhaErrada123!", senha_hash)


def test_hash_rejeita_hash_invalido():
    assert not api.verificar_senha("qualquer senha", "hash-invalido")


def test_validar_materia_remove_espacos_externos():
    assert api.validar_materia("  Python  ") == "Python"


def test_validar_materia_rejeita_texto_vazio():
    try:
        api.validar_materia("   ")
        assert False, "Deveria rejeitar uma matéria vazia"
    except HTTPException as erro:
        assert erro.status_code == 422


def test_validar_materia_rejeita_texto_acima_de_100_caracteres():
    try:
        api.validar_materia("A" * 101)
        assert False, "Deveria rejeitar mais de 100 caracteres"
    except HTTPException as erro:
        assert erro.status_code == 422


def test_token_criado_pode_ser_verificado():
    token = api.criar_token(123)
    credenciais = api.HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )
    dados = api.verificar_token(123, credenciais)
    assert dados == 123


def test_endpoint_status():
    cliente = TestClient(api.app)
    resposta = cliente.get("/status")

    assert resposta.status_code == 200
    assert resposta.json()["mensagem"] == "SGE está funcionando!"

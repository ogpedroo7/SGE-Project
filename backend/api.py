import hashlib
import hmac
import json
import secrets
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.database import conectar_banco, criar_tabelas


app = FastAPI(title="SGE - API", version="2.0.0")

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

NIVEIS = [
    "Iniciante Absoluto",
    "Fundamentos Básicos",
    "Lógica de Programação",
    "Controle de Fluxo",
    "Manipulação de Dados",
    "Funções e Organização",
    "Python Intermediário",
    "Orientação a Objetos",
    "Python Avançado",
    "Domínio Prático",
]

# Cada página possui conteúdo, exemplo e exercício.
# As respostas corretas ficam exclusivamente no backend.
CONTEUDO = [
    [
        ("Conhecendo o Python", "Python é uma linguagem de programação usada para criar programas, automatizar tarefas e desenvolver aplicações.", 'print("Olá, mundo!")', "O que print() faz?", ["Exibe uma mensagem", "Apaga um arquivo", "Cria uma variável"], "a"),
        ("Seu primeiro programa", "Um programa é uma sequência de instruções que o computador executa.", 'print("Estou aprendendo Python")', "Qual comando exibe o texto na tela?", ["input()", "print()", "type()"], "b"),
        ("Textos e strings", "Textos são representados por strings, normalmente delimitadas por aspas.", 'print("Estudo de Python")', "Qual opção representa um texto?", ['"Python"', "123", "True"], "a"),
        ("Números inteiros", "O tipo int representa números inteiros, positivos, negativos ou zero.", "print(25)", "Qual é um número inteiro?", ['"25"', "25", "25.5"], "b"),
        ("Números decimais", "O tipo float representa números com casas decimais.", "print(3.14)", "Qual valor é float?", ["10", "3.14", '"3.14"'], "b"),
        ("Valores booleanos", "O tipo bool representa verdadeiro ou falso.", "print(True)", "Qual valor é booleano?", ['"True"', "True", "100"], "b"),
        ("Variáveis", "Variáveis associam nomes a valores, facilitando sua reutilização.", "nome = 'Ana'\nprint(nome)", "Como guardar o nome Ana em uma variável?", ['nome = "Ana"', 'print = "Ana"', "Ana = nome()"], "a"),
        ("Usando variáveis", "Uma variável pode ser utilizada em várias partes do programa.", "idade = 19\nprint(idade)", "O que print(idade) exibe?", ["O texto idade sempre", "O valor guardado em idade", "Nada"], "b"),
        ("Comentários", "Comentários começam com # e servem para explicar o código.", "# Meu primeiro comentário\nprint('Oi')", "Qual símbolo inicia um comentário?", ["//", "#", "<!--"], "b"),
        ("Revisão inicial", "Nesta etapa, você conheceu comandos, textos, números, valores lógicos e variáveis.", 'linguagem = "Python"\nprint(linguagem)', "Qual é a finalidade de uma variável?", ["Guardar ou referenciar um valor", "Desligar o computador", "Instalar o Python"], "a"),
    ],
    [
        ("Operadores aritméticos", "Python permite somar, subtrair, multiplicar e dividir valores.", "print(8 + 2)", "Qual é o resultado de 8 + 2?", ["10", "6", "16"], "a"),
        ("Subtração", "O operador - calcula a diferença entre números.", "print(9 - 4)", "Quanto vale 9 - 4?", ["13", "5", "36"], "b"),
        ("Multiplicação", "O operador * multiplica valores.", "print(6 * 3)", "Quanto vale 6 * 3?", ["9", "18", "2"], "b"),
        ("Divisão", "O operador / realiza uma divisão e normalmente retorna float.", "print(10 / 2)", "Qual é o resultado de 10 / 2 em Python?", ["5.0", "8", "102"], "a"),
        ("Divisão inteira", "O operador // retorna o quociente inteiro da divisão.", "print(10 // 3)", "Quanto vale 10 // 3?", ["3", "3.33", "1"], "a"),
        ("Resto da divisão", "O operador % retorna o resto de uma divisão.", "print(10 % 3)", "Quanto vale 10 % 3?", ["3", "1", "0"], "b"),
        ("Potência", "O operador ** calcula uma potência.", "print(2 ** 3)", "Quanto vale 2 ** 3?", ["6", "8", "9"], "b"),
        ("Entrada de dados", "input() recebe texto digitado pelo usuário.", 'nome = input("Nome: ")', "Qual função recebe uma entrada?", ["print()", "input()", "len()"], "b"),
        ("Conversão de tipos", "int() converte valores compatíveis para inteiro.", 'idade = int("20")', "Qual função converte um texto numérico para inteiro?", ["str()", "float()", "int()"], "c"),
        ("Concatenação", "O operador + pode juntar strings.", 'print("Bom " + "dia")', "Qual será a saída?", ["Bom dia", "Bom + dia", "Erro sempre"], "a"),
    ],
    [
        ("O que é lógica", "Lógica de programação organiza instruções para resolver problemas.", "entrada = 5\nresultado = entrada * 2\nprint(resultado)", "Qual é a saída?", ["5", "10", "25"], "b"),
        ("Comparação de igualdade", "O operador == verifica se dois valores são iguais.", "print(5 == 5)", "Qual é o resultado de 5 == 5?", ["True", "False", "5"], "a"),
        ("Diferença", "O operador != verifica se dois valores são diferentes.", "print(4 != 7)", "Qual é o resultado de 4 != 7?", ["False", "True", "11"], "b"),
        ("Maior e menor", "Os operadores > e < comparam valores.", "print(8 > 3)", "Qual é o resultado de 8 > 3?", ["True", "False", "8"], "a"),
        ("Operador and", "and resulta em True quando as duas condições são verdadeiras.", "print(True and False)", "Qual é o resultado?", ["True", "False", "None"], "b"),
        ("Operador or", "or resulta em True quando pelo menos uma condição é verdadeira.", "print(True or False)", "Qual é o resultado?", ["True", "False", "Erro"], "a"),
        ("Operador not", "not inverte um valor booleano.", "print(not True)", "Qual é o resultado?", ["True", "False", "1"], "b"),
        ("Algoritmos", "Um algoritmo descreve passos ordenados para resolver uma tarefa.", "passo1 = 'abrir'\npasso2 = 'executar'", "O que é um algoritmo?", ["Uma sequência de passos", "Um tipo de monitor", "Um banco de dados"], "a"),
        ("Decomposição", "Dividir um problema em partes menores ajuda a resolver tarefas complexas.", "print('Etapa 1')\nprint('Etapa 2')", "Por que dividir um problema?", ["Para dificultar", "Para organizar a solução", "Para remover instruções"], "b"),
        ("Revisão de lógica", "Condições e operadores permitem avaliar situações e tomar decisões.", "print(10 >= 10)", "Qual é o resultado de 10 >= 10?", ["False", "True", "10"], "b"),
    ],
    [
        ("Condição if", "if executa um bloco quando a condição é verdadeira.", "idade = 20\nif idade >= 18:\n    print('Maior')", "Quando o bloco do if executa?", ["Quando a condição é verdadeira", "Sempre duas vezes", "Somente quando o programa fecha"], "a"),
        ("Alternativa else", "else executa quando a condição do if não é satisfeita.", "if False:\n    print('A')\nelse:\n    print('B')", "Qual texto aparece?", ["A", "B", "Nenhum"], "b"),
        ("Condição elif", "elif permite verificar outra condição depois de um if.", "nota = 7\nif nota >= 9:\n    print('A')\nelif nota >= 6:\n    print('B')", "Qual texto aparece?", ["A", "B", "Erro"], "b"),
        ("Múltiplas condições", "É possível combinar condições com and e or.", "idade = 20\nprint(idade >= 18 and idade < 60)", "Qual é o resultado?", ["True", "False", "20"], "a"),
        ("Laço while", "while repete um bloco enquanto a condição for verdadeira.", "contador = 0\nwhile contador < 2:\n    contador += 1", "Quantas vezes o corpo executa?", ["Uma", "Duas", "Infinitas"], "b"),
        ("Laço for", "for percorre os itens de uma sequência ou intervalo.", "for n in range(3):\n    print(n)", "Quais números são exibidos?", ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3"], "b"),
        ("range", "range( início, fim ) inclui o início e exclui o fim.", "print(list(range(1, 4)))", "Qual lista é criada?", ["[1, 2, 3]", "[1, 2, 3, 4]", "[0, 1, 2, 3]"], "a"),
        ("break", "break encerra imediatamente o laço atual.", "for n in range(5):\n    if n == 2:\n        break", "O que break faz?", ["Pula para a próxima iteração", "Encerra o laço", "Reinicia o Python"], "b"),
        ("continue", "continue pula o restante da iteração atual.", "for n in range(3):\n    if n == 1:\n        continue\n    print(n)", "Qual valor não é exibido?", ["0", "1", "2"], "b"),
        ("Revisão de fluxo", "Condições e laços controlam quais instruções são executadas e quantas vezes.", "for n in range(2):\n    print('Oi')", "Quantas vezes aparece Oi?", ["Uma", "Duas", "Três"], "b"),
    ],
    [
        ("Listas", "Listas armazenam vários valores em uma sequência mutável.", "frutas = ['maçã', 'pera']\nprint(frutas[0])", "Qual item está no índice 0?", ["pera", "maçã", "frutas"], "b"),
        ("Índices", "Os índices das listas começam em zero.", "valores = [10, 20, 30]\nprint(valores[1])", "Qual valor é exibido?", ["10", "20", "30"], "b"),
        ("Adicionar itens", "append() adiciona um item ao final de uma lista.", "numeros = [1]\nnumeros.append(2)", "O que append(2) faz?", ["Remove 2", "Adiciona 2 ao final", "Ordena a lista"], "b"),
        ("Remover itens", "remove() remove a primeira ocorrência de um valor especificado.", "itens = ['a', 'b']\nitens.remove('a')", "Qual item permanece?", ["a", "b", "Nenhum"], "b"),
        ("Tuplas", "Tuplas são sequências que não podem ser alteradas após a criação.", "coordenada = (10, 20)", "Qual característica define uma tupla?", ["É imutável", "Sempre ordena números", "Só aceita texto"], "a"),
        ("Dicionários", "Dicionários armazenam pares de chave e valor.", "pessoa = {'nome': 'Ana'}\nprint(pessoa['nome'])", "Qual valor é exibido?", ["nome", "Ana", "pessoa"], "b"),
        ("Conjuntos", "set representa uma coleção de elementos únicos.", "valores = set([1, 1, 2])\nprint(len(valores))", "Qual é o tamanho do conjunto?", ["3", "2", "1"], "b"),
        ("Strings e métodos", "Métodos como upper() retornam uma versão em maiúsculas do texto.", "print('python'.upper())", "Qual é a saída?", ["python", "PYTHON", "Python"], "b"),
        ("Tamanho", "len() retorna a quantidade de itens de uma sequência.", "print(len('casa'))", "Qual é o resultado?", ["3", "4", "5"], "b"),
        ("Percorrer coleções", "for pode visitar cada item de uma lista.", "for cor in ['azul', 'verde']:\n    print(cor)", "Quantas cores são exibidas?", ["Uma", "Duas", "Três"], "b"),
    ],
    [
        ("Criando funções", "def define uma função reutilizável.", "def saudar():\n    print('Olá')\nsaudar()", "Qual palavra define uma função?", ["func", "def", "function"], "b"),
        ("Parâmetros", "Parâmetros recebem valores usados pela função.", "def dobrar(n):\n    return n * 2", "Qual é o parâmetro?", ["dobrar", "n", "return"], "b"),
        ("return", "return devolve um resultado para quem chamou a função.", "def somar(a, b):\n    return a + b", "O que return faz?", ["Devolve um resultado", "Repete o código", "Imprime sempre na tela"], "a"),
        ("Argumentos", "Argumentos são os valores fornecidos ao chamar uma função.", "def dobro(n):\n    return n * 2\nprint(dobro(4))", "Qual argumento foi fornecido?", ["n", "4", "2"], "b"),
        ("Escopo local", "Uma variável criada dentro de uma função normalmente tem escopo local.", "def exemplo():\n    valor = 10", "Onde valor foi criado?", ["Dentro da função", "No banco de dados", "No navegador"], "a"),
        ("Valores padrão", "Parâmetros podem ter valores padrão.", "def saudar(nome='amigo'):\n    return nome", "O que ocorre sem argumento?", ["Usa 'amigo'", "Retorna erro sempre", "Usa uma string vazia"], "a"),
        ("Módulos", "Módulos permitem organizar e reutilizar código em arquivos.", "import math\nprint(math.sqrt(9))", "Qual módulo é importado?", ["random", "math", "json"], "b"),
        ("Bibliotecas", "Bibliotecas oferecem funcionalidades prontas para reutilização.", "import random", "Por que importar uma biblioteca?", ["Reutilizar funcionalidades", "Apagar variáveis", "Desligar o interpretador"], "a"),
        ("Tratamento de erros", "try e except permitem tratar determinadas exceções.", "try:\n    int('abc')\nexcept ValueError:\n    print('Inválido')", "Qual bloco trata o erro?", ["try", "except", "def"], "b"),
        ("Organização", "Funções pequenas e bem nomeadas ajudam a manter o código organizado.", "def calcular_total(preco, quantidade):\n    return preco * quantidade", "Qual é uma vantagem de funções?", ["Reutilização e organização", "Impedir entradas", "Substituir todas as variáveis"], "a"),
    ],
    [
        ("List comprehensions", "Compreensões criam listas de maneira concisa.", "quadrados = [n*n for n in range(3)]", "Qual lista é produzida?", ["[0, 1, 4]", "[1, 4, 9]", "[0, 1, 2]"], "a"),
        ("Funções lambda", "lambda cria uma função pequena e anônima.", "dobro = lambda n: n * 2", "O que lambda cria?", ["Uma classe", "Uma função anônima", "Uma lista"], "b"),
        ("Ordenação", "sorted() retorna uma nova lista ordenada.", "print(sorted([3, 1, 2]))", "Qual é a saída?", ["[3, 2, 1]", "[1, 2, 3]", "[3, 1, 2]"], "b"),
        ("Funções de ordem superior", "Funções podem receber outras funções como argumentos.", "print(list(map(str, [1, 2])))", "O que map aplica aos itens?", ["A função fornecida", "Uma consulta SQL", "Uma condição HTML"], "a"),
        ("Arquivos", "open() permite abrir arquivos para leitura ou escrita.", "with open('dados.txt', 'r') as arquivo:\n    texto = arquivo.read()", "Qual modo indica leitura?", ["'w'", "'r'", "'x'"], "b"),
        ("JSON", "JSON é um formato comum para representar dados estruturados.", "import json\njson.dumps({'ativo': True})", "Qual formato está sendo usado?", ["JSON", "CSS", "SQL"], "a"),
        ("Datas", "O módulo datetime oferece tipos e operações para datas e horários.", "from datetime import date", "Qual módulo foi importado?", ["pathlib", "datetime", "sqlite3"], "b"),
        ("Iteradores", "Iteradores fornecem itens um de cada vez.", "iter([1, 2, 3])", "Qual função cria um iterador?", ["iter()", "print()", "str()"], "a"),
        ("Geradores", "yield permite produzir valores de forma gradual em um gerador.", "def numeros():\n    yield 1\n    yield 2", "Qual palavra produz um valor no gerador?", ["return apenas", "yield", "class"], "b"),
        ("Ambientes virtuais", "Ambientes virtuais isolam dependências de projetos Python.", "python -m venv .venv", "Qual é a finalidade de um ambiente virtual?", ["Isolar dependências", "Aumentar a RAM", "Criar páginas HTML automaticamente"], "a"),
    ],
    [
        ("Classes", "Classes definem estruturas para criar objetos.", "class Pessoa:\n    pass", "Qual palavra define uma classe?", ["def", "class", "object"], "b"),
        ("Objetos", "Objetos são instâncias de classes.", "class Pessoa:\n    pass\np = Pessoa()", "O que p representa?", ["Uma instância", "Uma biblioteca", "Um laço"], "a"),
        ("Método inicializador", "__init__ configura um objeto quando ele é criado.", "class Pessoa:\n    def __init__(self, nome):\n        self.nome = nome", "Quando __init__ é chamado?", ["Na inicialização do objeto", "Ao importar CSS", "A cada comentário"], "a"),
        ("self", "self referencia a instância atual dentro de métodos de instância.", "class Contador:\n    def mostrar(self):\n        return self", "O que self representa?", ["A instância atual", "Uma variável global obrigatória", "O nome do módulo"], "a"),
        ("Atributos", "Atributos armazenam dados associados a um objeto ou classe.", "pessoa.nome = 'Ana'", "O que nome é nesse exemplo?", ["Um atributo", "Um operador", "Um módulo"], "a"),
        ("Herança", "Herança permite criar classes baseadas em outras classes.", "class Animal:\n    pass\nclass Cachorro(Animal):\n    pass", "Cachorro herda de qual classe?", ["Animal", "object apenas explicitamente", "Cachorro"], "a"),
        ("Polimorfismo", "Polimorfismo permite que objetos diferentes respondam à mesma operação.", "print(len('abc'))", "Qual função retorna o tamanho?", ["len()", "sum()", "open()"], "a"),
        ("Encapsulamento", "Encapsulamento organiza dados e comportamentos dentro de uma abstração.", "class Conta:\n    def __init__(self):\n        self.saldo = 0", "Onde o saldo é armazenado?", ["No atributo do objeto", "No CSS", "No terminal"], "a"),
        ("Métodos de classe", "classmethod recebe a classe como primeiro argumento convencional, cls.", "class Exemplo:\n    @classmethod\n    def criar(cls):\n        return cls()", "Qual decorador indica um método de classe?", ["@staticmethod", "@classmethod", "@property"], "b"),
        ("Composição", "Composição permite que um objeto utilize outros objetos como componentes.", "class Motor:\n    pass\nclass Carro:\n    def __init__(self):\n        self.motor = Motor()", "Qual objeto o carro contém?", ["Um motor", "Uma função externa", "Um módulo CSS"], "a"),
    ],
    [
        ("Decoradores", "Decoradores envolvem funções ou classes para modificar seu comportamento.", "def decorador(func):\n    return func", "O que um decorador recebe frequentemente?", ["Uma função ou classe", "Apenas um número", "Uma imagem"], "a"),
        ("Context managers", "Gerenciadores de contexto permitem preparar e finalizar recursos com with.", "with open('dados.txt', 'w') as arquivo:\n    arquivo.write('Oi')", "Qual palavra inicia o contexto?", ["with", "yield", "global"], "a"),
        ("Anotações de tipo", "Anotações documentam os tipos esperados, sem validar tudo automaticamente.", "def somar(a: int, b: int) -> int:\n    return a + b", "O que -> int indica?", ["Tipo de retorno documentado", "Conversão obrigatória automática", "Um comentário CSS"], "a"),
        ("Dataclasses", "dataclass reduz código repetitivo em classes usadas principalmente para armazenar dados.", "from dataclasses import dataclass", "Qual módulo contém dataclass?", ["dataclasses", "datetime", "sqlite3"], "a"),
        ("Expressões regulares", "O módulo re permite buscar padrões em textos.", "import re\nre.search(r'\\d+', 'abc123')", "Qual módulo foi usado?", ["re", "json", "math"], "a"),
        ("Concorrência", "Concorrência permite estruturar tarefas que progridem de forma intercalada.", "import asyncio", "Qual módulo fornece suporte a programação assíncrona?", ["asyncio", "pathlib", "csv"], "a"),
        ("Logging", "logging registra eventos e mensagens de diagnóstico.", "import logging\nlogging.warning('Atenção')", "Qual módulo registra mensagens?", ["logging", "random", "turtle"], "a"),
        ("Testes automatizados", "Testes automatizados verificam se o comportamento do código corresponde ao esperado.", "assert 2 + 2 == 4", "O que assert verifica?", ["Uma condição", "A velocidade da internet", "O tamanho do monitor"], "a"),
        ("Segurança de senhas", "Senhas não devem ser armazenadas em texto puro; use técnicas de hash apropriadas.", "import hashlib", "Qual é uma prática segura?", ["Guardar senha em texto puro", "Guardar hash de senha com salt", "Compartilhar senhas em logs"], "b"),
        ("Desempenho", "Antes de otimizar, meça o desempenho para identificar gargalos reais.", "import time", "Qual é a melhor primeira etapa para otimizar?", ["Medir o desempenho", "Reescrever tudo", "Remover os testes"], "a"),
    ],
    [
        ("Projeto integrador", "Um projeto real reúne entrada, processamento, validação e saída.", "def calcular_total(preco, quantidade):\n    return preco * quantidade", "Qual etapa calcula o resultado?", ["Processamento", "Cadastro de usuário", "Formatação CSS"], "a"),
        ("Validação de entrada", "Dados recebidos precisam ser validados antes de serem usados.", "idade = int(input('Idade: '))", "Por que validar entradas?", ["Para reduzir dados inválidos", "Para aceitar qualquer valor sem análise", "Para desativar erros"], "a"),
        ("Persistência", "Persistência permite recuperar dados após o encerramento do programa.", "import sqlite3", "Qual é a finalidade da persistência?", ["Manter dados armazenados", "Apagar toda informação", "Exibir animações"], "a"),
        ("Banco de dados", "Bancos relacionais organizam dados em tabelas e relacionamentos.", "SELECT * FROM usuarios;", "Qual linguagem é usada na consulta?", ["SQL", "CSS", "Markdown"], "a"),
        ("APIs", "APIs permitem que aplicações troquem dados por interfaces definidas.", "import json", "Para que serve uma API?", ["Permitir comunicação entre sistemas", "Trocar o processador", "Editar o gabinete"], "a"),
        ("HTTP", "HTTP define métodos e mensagens usados na comunicação web.", "GET /usuarios", "Qual é o propósito típico de GET?", ["Consultar um recurso", "Excluir sempre o banco", "Criar uma senha local automaticamente"], "a"),
        ("Tratamento de falhas", "Erros devem ser tratados sem esconder problemas importantes.", "try:\n    resultado = 10 / 0\nexcept ZeroDivisionError:\n    resultado = None", "Qual exceção ocorre na divisão por zero?", ["ZeroDivisionError", "KeyError", "ImportError"], "a"),
        ("Git", "Git registra versões e mudanças no código.", "git status", "O que git status mostra?", ["Estado das alterações", "A senha do usuário", "A temperatura do processador"], "a"),
        ("Documentação", "Uma boa documentação explica instalação, uso e decisões importantes.", "# Como executar\npython main.py", "O que a documentação deve explicar?", ["Como utilizar o projeto", "Apenas a cor do editor", "Somente o nome do autor"], "a"),
        ("Entrega final", "Uma entrega confiável inclui testes, documentação e instruções para executar.", "print('Projeto concluído')", "O que ajuda a validar uma entrega?", ["Testes e verificação de funcionamento", "Ignorar erros", "Apagar os arquivos-fonte"], "a"),
    ],
]


def gerar_hash_senha(senha):
    salt = secrets.token_bytes(16)
    resultado = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, 600_000
    )
    return salt.hex() + ":" + resultado.hex()


def verificar_senha(senha, senha_hash):
    try:
        salt_hex, hash_salvo = senha_hash.split(":")
        resultado = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            bytes.fromhex(salt_hex),
            600_000,
        )
        return hmac.compare_digest(resultado.hex(), hash_salvo)
    except (ValueError, TypeError):
        return False


def validar_materia(materia):
    materia = materia.strip()
    if not materia or len(materia) > 100:
        raise HTTPException(422, "A matéria deve ter entre 1 e 100 caracteres.")
    return materia


def buscar_usuario(usuario_id):
    with conectar_banco() as conexao:
        usuario = conexao.execute(
            "SELECT id FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
    if usuario is None:
        raise HTTPException(404, "Usuário não encontrado.")


def obter_estado(usuario_id, materia):
    buscar_usuario(usuario_id)
    with conectar_banco() as conexao:
        conexao.execute(
            "INSERT OR IGNORE INTO progresso_aulas (usuario_id, materia) VALUES (?, ?)",
            (usuario_id, materia),
        )
        estado = conexao.execute(
            "SELECT * FROM progresso_aulas WHERE usuario_id = ? AND materia = ?",
            (usuario_id, materia),
        ).fetchone()
    return dict(estado)


def progresso_percentual(usuario_id, materia):
    with conectar_banco() as conexao:
        registros = conexao.execute(
            "SELECT paginas_concluidas FROM progresso_aulas WHERE usuario_id = ? AND materia = ?",
            (usuario_id, materia),
        ).fetchall()
    paginas = set()
    for registro in registros:
        try:
            paginas.update(json.loads(registro["paginas_concluidas"]))
        except (TypeError, json.JSONDecodeError):
            pass
    return min(100, round(len(paginas) / 100 * 100))


def atualizar_resumo(usuario_id, materia):
    estado = obter_estado(usuario_id, materia)
    percentual = progresso_percentual(usuario_id, materia)
    horas = int(estado["segundos_estudados"]) / 3600
    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO progresso_estudos
                (usuario_id, materia, horas_estudadas, progresso, nivel)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(usuario_id, materia) DO UPDATE SET
                horas_estudadas = excluded.horas_estudadas,
                progresso = excluded.progresso,
                nivel = excluded.nivel
            """,
            (usuario_id, materia, horas, percentual, estado["nivel"]),
        )


def exigir_nivel_disponivel(usuario_id, materia, nivel):
    estado = obter_estado(usuario_id, materia)
    if nivel > estado["nivel"]:
        raise HTTPException(403, "Esse nível ainda está bloqueado.")
    if materia.lower() != "python":
        raise HTTPException(404, "O conteúdo desta matéria ainda não foi criado.")


def obter_aula(nivel, pagina):
    if not 1 <= nivel <= 10 or not 1 <= pagina <= 10:
        raise HTTPException(404, "Aula não encontrada.")
    titulo, conteudo, codigo, pergunta, opcoes, resposta = CONTEUDO[nivel - 1][pagina - 1]
    return {
        "nivel": nivel,
        "pagina": pagina,
        "titulo": titulo,
        "conteudo": conteudo,
        "codigo": codigo,
        "pergunta": pergunta,
        "opcoes": [
            {"id": letra, "texto": texto}
            for letra, texto in zip(("a", "b", "c"), opcoes)
        ],
    }


def resposta_correta(nivel, pagina):
    return CONTEUDO[nivel - 1][pagina - 1][5]


def exigir_paginas_concluidas(usuario_id, materia, nivel):
    estado = obter_estado(usuario_id, materia)
    paginas = set(json.loads(estado["paginas_concluidas"]))
    necessarias = {f"{nivel}:{p}" for p in range(1, 11)}
    if not necessarias.issubset(paginas):
        raise HTTPException(403, "Conclua as 10 páginas deste nível primeiro.")


class CadastroUsuario(BaseModel):
    nome: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    senha: str = Field(min_length=8, max_length=128)


class LoginUsuario(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    senha: str = Field(min_length=1, max_length=128)


class SalvarPagina(BaseModel):
    nivel: int = Field(ge=1, le=10)
    pagina: int = Field(ge=1, le=10)
    concluir: bool = False


class RegistrarTempo(BaseModel):
    segundos: int = Field(ge=1, le=3600)


class RespostaAula(BaseModel):
    nivel: int = Field(ge=1, le=10)
    pagina: int = Field(ge=1, le=10)
    resposta: str = Field(min_length=1, max_length=10)


class NivelRequest(BaseModel):
    nivel: int = Field(ge=1, le=10)


class RespostaQuiz(BaseModel):
    nivel: int = Field(ge=1, le=10)
    questao_id: str = Field(min_length=1, max_length=10)
    resposta: str = Field(min_length=1, max_length=10)


@app.get("/status")
def status():
    return {"mensagem": "StudyCore está funcionando!", "versao": "2.0.0"}


@app.post("/usuarios/cadastro", status_code=201)
def cadastrar_usuario(dados: CadastroUsuario):
    nome = dados.nome.strip()
    email = dados.email.strip().lower()
    if len(nome) < 2 or "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(400, "Informe um nome e um e-mail válidos.")
    try:
        with conectar_banco() as conexao:
            cursor = conexao.execute(
                "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
                (nome, email, gerar_hash_senha(dados.senha)),
            )
            usuario_id = cursor.lastrowid
    except sqlite3.IntegrityError as erro:
        if "UNIQUE constraint failed" in str(erro):
            raise HTTPException(409, "Este e-mail já está cadastrado.")
        raise
    return {
        "mensagem": "Conta criada com sucesso!",
        "usuario": {"id": usuario_id, "nome": nome, "email": email},
    }


@app.post("/usuarios/login")
def login(dados: LoginUsuario):
    with conectar_banco() as conexao:
        usuario = conexao.execute(
            "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?",
            (dados.email.strip().lower(),),
        ).fetchone()
    if usuario is None or not verificar_senha(dados.senha, usuario["senha_hash"]):
        raise HTTPException(401, "E-mail ou senha incorretos.")
    return {
        "mensagem": "Login realizado com sucesso!",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
        },
    }


@app.get("/usuarios/{usuario_id}/progresso")
def listar_progressos(usuario_id: int):
    buscar_usuario(usuario_id)
    with conectar_banco() as conexao:
        registros = conexao.execute(
            "SELECT materia, horas_estudadas, progresso, nivel FROM progresso_estudos WHERE usuario_id = ? ORDER BY materia",
            (usuario_id,),
        ).fetchall()
    return {"progressos": [dict(r) for r in registros]}


@app.get("/usuarios/{usuario_id}/materias/{materia}/progresso")
def obter_progresso(usuario_id: int, materia: str):
    materia = validar_materia(materia)
    atualizar_resumo(usuario_id, materia)
    with conectar_banco() as conexao:
        registro = conexao.execute(
            "SELECT materia, horas_estudadas, progresso, nivel FROM progresso_estudos WHERE usuario_id = ? AND materia = ?",
            (usuario_id, materia),
        ).fetchone()
    estado = obter_estado(usuario_id, materia)
    return {
        **dict(registro),
        "segundos_estudados": estado["segundos_estudados"],
        "pagina": estado["pagina"],
    }


@app.get("/usuarios/{usuario_id}/materias/{materia}/curso")
def obter_curso(usuario_id: int, materia: str):
    materia = validar_materia(materia)
    estado = obter_estado(usuario_id, materia)
    with conectar_banco() as conexao:
        niveis = conexao.execute(
            "SELECT nivel, resumo_concluido, aprovado FROM niveis_curso WHERE usuario_id = ? AND materia = ? ORDER BY nivel",
            (usuario_id, materia),
        ).fetchall()
        respostas = conexao.execute(
            "SELECT nivel, questao_id, resposta, acertou FROM respostas_quiz WHERE usuario_id = ? AND materia = ? ORDER BY nivel, questao_id",
            (usuario_id, materia),
        ).fetchall()

    paginas = json.loads(estado["paginas_concluidas"])
    return {
        "curso": materia,
        "estado": {**estado, "paginas_concluidas": paginas},
        "niveis": [dict(r) for r in niveis],
        "respostas_quiz": [dict(r) for r in respostas],
        "nomes_niveis": NIVEIS if materia.lower() == "python" else [],
    }


@app.get("/usuarios/{usuario_id}/materias/{materia}/curso/aula")
def carregar_aula(usuario_id: int, materia: str, nivel: int = 1, pagina: int = 1):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, nivel)
    return obter_aula(nivel, pagina)


@app.put("/usuarios/{usuario_id}/materias/{materia}/curso/pagina")
def salvar_pagina(usuario_id: int, materia: str, dados: SalvarPagina):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, dados.nivel)

    estado = obter_estado(usuario_id, materia)
    paginas = set(json.loads(estado["paginas_concluidas"]))

    # Não permite marcar a página como concluída sem responder corretamente.
    if dados.concluir and f"{dados.nivel}:{dados.pagina}" not in paginas:
        raise HTTPException(
            403,
            "Responda corretamente ao exercício desta página antes de concluí-la.",
        )

    with conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE progresso_aulas
            SET nivel = ?, pagina = ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE usuario_id = ? AND materia = ?
            """,
            (dados.nivel, dados.pagina, usuario_id, materia),
        )
    atualizar_resumo(usuario_id, materia)
    return {
        "mensagem": "Posição de estudo salva.",
        "nivel": dados.nivel,
        "pagina": dados.pagina,
        "paginas_concluidas": sorted(paginas),
    }


@app.post("/usuarios/{usuario_id}/materias/{materia}/curso/aula/responder")
def responder_aula(usuario_id: int, materia: str, dados: RespostaAula):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, dados.nivel)

    # Valida a página e registra que o aluno respondeu.
    resposta_correta(dados.nivel, dados.pagina)

    estado = obter_estado(usuario_id, materia)
    paginas = set(json.loads(estado["paginas_concluidas"]))

    # A página é concluída independentemente de a resposta estar certa.
    paginas.add(f"{dados.nivel}:{dados.pagina}")

    with conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE progresso_aulas
            SET paginas_concluidas = ?,
                nivel = ?,
                pagina = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE usuario_id = ? AND materia = ?
            """,
            (
                json.dumps(sorted(paginas)),
                dados.nivel,
                dados.pagina,
                usuario_id,
                materia,
            ),
        )

    atualizar_resumo(usuario_id, materia)

    # Não revela se a resposta estava certa ou errada durante a aula.
    return {
        "mensagem": "Resposta registrada. Você já pode continuar.",
        "paginas_concluidas": sorted(paginas),
        "progresso": progresso_percentual(usuario_id, materia),
    }

@app.post("/usuarios/{usuario_id}/materias/{materia}/curso/tempo")
def registrar_tempo(usuario_id: int, materia: str, dados: RegistrarTempo):
    materia = validar_materia(materia)
    obter_estado(usuario_id, materia)
    with conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE progresso_aulas
            SET segundos_estudados = segundos_estudados + ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE usuario_id = ? AND materia = ?
            """,
            (dados.segundos, usuario_id, materia),
        )
    atualizar_resumo(usuario_id, materia)
    with conectar_banco() as conexao:
        segundos = conexao.execute(
            "SELECT segundos_estudados FROM progresso_aulas WHERE usuario_id = ? AND materia = ?",
            (usuario_id, materia),
        ).fetchone()["segundos_estudados"]
    return {
        "segundos_estudados": segundos,
        "horas_estudadas": round(segundos / 3600, 2),
    }


@app.post("/usuarios/{usuario_id}/materias/{materia}/curso/resumo")
def concluir_resumo(usuario_id: int, materia: str, dados: NivelRequest):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, dados.nivel)
    exigir_paginas_concluidas(usuario_id, materia, dados.nivel)

    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO niveis_curso (usuario_id, materia, nivel, resumo_concluido)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(usuario_id, materia, nivel)
            DO UPDATE SET resumo_concluido = 1, atualizado_em = CURRENT_TIMESTAMP
            """,
            (usuario_id, materia, dados.nivel),
        )

    return {
        "mensagem": "Resumo concluído. Você já pode iniciar o quiz.",
        "nivel": dados.nivel,
    }


@app.get("/usuarios/{usuario_id}/materias/{materia}/curso/quiz")
def obter_quiz(usuario_id: int, materia: str, nivel: int = 1):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, nivel)
    exigir_paginas_concluidas(usuario_id, materia, nivel)

    with conectar_banco() as conexao:
        resumo = conexao.execute(
            "SELECT resumo_concluido FROM niveis_curso WHERE usuario_id = ? AND materia = ? AND nivel = ?",
            (usuario_id, materia, nivel),
        ).fetchone()
        respostas = conexao.execute(
            "SELECT questao_id, resposta, acertou FROM respostas_quiz WHERE usuario_id = ? AND materia = ? AND nivel = ?",
            (usuario_id, materia, nivel),
        ).fetchall()

    if resumo is None or not resumo["resumo_concluido"]:
        raise HTTPException(403, "Conclua o resumo antes do quiz.")

    # As dez questões do nível são baseadas nas dez aulas.
    perguntas = []
    for pagina, item in enumerate(CONTEUDO[nivel - 1], start=1):
        titulo, conteudo, codigo, pergunta, opcoes, _ = item
        perguntas.append({
            "id": str(pagina),
            "pergunta": pergunta,
            "opcoes": [
                {"id": letra, "texto": texto}
                for letra, texto in zip(("a", "b", "c"), opcoes)
            ],
        })

    return {
        "nivel": nivel,
        "questoes": perguntas,
        "respostas_salvas": [dict(r) for r in respostas],
        "minimo_para_aprovar": 8,
    }


@app.post("/usuarios/{usuario_id}/materias/{materia}/curso/quiz/responder")
def responder_quiz(usuario_id: int, materia: str, dados: RespostaQuiz):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, dados.nivel)
    exigir_paginas_concluidas(usuario_id, materia, dados.nivel)

    try:
        pagina = int(dados.questao_id)
    except ValueError:
        raise HTTPException(422, "Identificador de questão inválido.")

    if not 1 <= pagina <= 10:
        raise HTTPException(404, "Questão não encontrada.")

    with conectar_banco() as conexao:
        resumo = conexao.execute(
            "SELECT resumo_concluido FROM niveis_curso WHERE usuario_id = ? AND materia = ? AND nivel = ?",
            (usuario_id, materia, dados.nivel),
        ).fetchone()

    if resumo is None or not resumo["resumo_concluido"]:
        raise HTTPException(403, "Conclua o resumo antes do quiz.")

    # A resposta é corrigida no servidor; o navegador não envia um booleano "correta".
    correta = resposta_correta(dados.nivel, pagina)
    acertou_agora = dados.resposta.strip().lower() == correta

    with conectar_banco() as conexao:
        anterior = conexao.execute(
            """
            SELECT acertou FROM respostas_quiz
            WHERE usuario_id = ? AND materia = ? AND nivel = ? AND questao_id = ?
            """,
            (usuario_id, materia, dados.nivel, dados.questao_id),
        ).fetchone()

        acertou_final = acertou_agora or (
            anterior is not None and anterior["acertou"] == 1
        )

        conexao.execute(
            """
            INSERT INTO respostas_quiz
                (usuario_id, materia, nivel, questao_id, resposta, acertou)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(usuario_id, materia, nivel, questao_id)
            DO UPDATE SET
                resposta = excluded.resposta,
                acertou = MAX(respostas_quiz.acertou, excluded.acertou),
                respondido_em = CURRENT_TIMESTAMP
            """,
            (
                usuario_id,
                materia,
                dados.nivel,
                dados.questao_id,
                dados.resposta,
                int(acertou_final),
            ),
        )

        total = conexao.execute(
            """
            SELECT COUNT(*) AS respondidas, COALESCE(SUM(acertou), 0) AS acertos
            FROM respostas_quiz
            WHERE usuario_id = ? AND materia = ? AND nivel = ?
            """,
            (usuario_id, materia, dados.nivel),
        ).fetchone()

        aprovado = total["acertos"] >= 8

        if aprovado:
            conexao.execute(
                """
                INSERT INTO niveis_curso
                    (usuario_id, materia, nivel, resumo_concluido, aprovado)
                VALUES (?, ?, ?, 1, 1)
                ON CONFLICT(usuario_id, materia, nivel)
                DO UPDATE SET aprovado = 1, atualizado_em = CURRENT_TIMESTAMP
                """,
                (usuario_id, materia, dados.nivel),
            )

            proximo = min(10, dados.nivel + 1)
            conexao.execute(
                """
                UPDATE progresso_aulas
                SET nivel = ?, pagina = 1, atualizado_em = CURRENT_TIMESTAMP
                WHERE usuario_id = ? AND materia = ?
                """,
                (proximo, usuario_id, materia),
            )

    atualizar_resumo(usuario_id, materia)

    with conectar_banco() as conexao:
        erradas = conexao.execute(
            """
            SELECT questao_id FROM respostas_quiz
            WHERE usuario_id = ? AND materia = ? AND nivel = ? AND acertou = 0
            ORDER BY CAST(questao_id AS INTEGER)
            """,
            (usuario_id, materia, dados.nivel),
        ).fetchall()

    return {
        "acertou": acertou_agora,
        "questoes_respondidas": total["respondidas"],
        "acertos_acumulados": total["acertos"],
        "minimo_para_aprovar": 8,
        "aprovado": aprovado,
        "recuperacao": not aprovado,
        "questoes_para_revisar": [r["questao_id"] for r in erradas],
        "proximo_nivel": min(10, dados.nivel + 1) if aprovado else None,
    }

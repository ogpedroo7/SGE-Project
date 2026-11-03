import hashlib
import hmac
import json
import secrets
import psycopg
from psycopg.errors import UniqueViolation
import os
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.database import conectar_banco, criar_tabelas


app = FastAPI(title="SGE - API", version="2.0.0")

CHAVE_SECRETA = os.getenv("STUDYCORE_SECRET_KEY")

if not CHAVE_SECRETA:
    raise RuntimeError(
        "A variável STUDYCORE_SECRET_KEY não foi configurada."
    )

ALGORITMO_TOKEN = "HS256"
TEMPO_TOKEN_HORAS = 2

seguranca = HTTPBearer()


def criar_token(usuario_id: int) -> str:
    agora = datetime.now(timezone.utc)

    payload = {
        "sub": str(usuario_id),
        "iat": agora,
        "exp": agora + timedelta(hours=TEMPO_TOKEN_HORAS),
    }

    return jwt.encode(
        payload,
        CHAVE_SECRETA,
        algorithm=ALGORITMO_TOKEN,
    )


def verificar_token(
    usuario_id: int,
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca),
):
    try:
        payload = jwt.decode(
            credenciais.credentials,
            CHAVE_SECRETA,
            algorithms=[ALGORITMO_TOKEN],
        )

        usuario_token = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado.",
        )

    if usuario_token != usuario_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode acessar os dados de outro usuário.",
        )

    return usuario_token


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sge-project-ten.vercel.app",
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
    # NÍVEL 1 — INICIANTE ABSOLUTO
    [
        (
            "Conhecendo o Python",
            """Python é uma linguagem de programação usada para criar programas, automatizar tarefas, desenvolver sites e trabalhar com dados.

Um programa é um conjunto de instruções que o computador executa. Em Python, podemos começar com uma instrução simples: print().

O texto colocado entre aspas é chamado de string. Os parênteses indicam o valor que será passado à função.

Quando executamos o exemplo abaixo, o Python exibe a mensagem no terminal.

Saída esperada:
Olá, mundo!

O computador executa a instrução escrita no código. Ele não interpreta automaticamente a intenção do programador; por isso, a sintaxe precisa estar correta.""",
            'print("Olá, mundo!")',
            "O que a função print() faz?",
            ["Exibe informações", "Cria um banco de dados", "Instala o Python"],
            "a",
        ),
        (
            "Seu primeiro programa",
            """Um programa pode conter várias instruções. Em geral, o Python executa essas instruções na ordem em que aparecem.

No exemplo, a primeira chamada de print() exibe uma mensagem. Depois, a segunda chamada exibe outra.

Saída esperada:
Estou aprendendo Python
Meu primeiro programa

Cada chamada de print() termina a linha exibida por padrão. Isso facilita organizar as informações.

É possível escrever programas com centenas ou milhares de instruções. Aprender a dividir um problema em passos menores ajuda a manter o código compreensível.""",
            'print("Estou aprendendo Python")\nprint("Meu primeiro programa")',
            "Qual comando é usado para exibir um texto no terminal?",
            ["input()", "print()", "type()"],
            "b",
        ),
        (
            "Textos e strings",
            """Em Python, uma string representa uma sequência de caracteres, como letras, números escritos como texto, espaços e símbolos.

Strings podem ser delimitadas por aspas simples ou duplas.

Exemplos:
"Python"
'Meu curso'
"123"

Embora "123" pareça um número, as aspas indicam que ele é texto. Isso faz diferença quando queremos realizar cálculos.

Podemos exibir uma string usando print(). As aspas delimitam o texto no código, mas normalmente não aparecem no resultado do terminal.""",
            'print("Estudo de Python")',
            'Qual alternativa representa uma string?',
            ['"Python"', "123", "True"],
            "a",
        ),
        (
            "Números inteiros",
            """O tipo int representa números inteiros, como 0, 12 e -5. Esses valores podem participar de operações matemáticas.

Observe:
idade = 19
print(idade)

A primeira linha associa o número inteiro 19 à variável idade. A segunda exibe o valor armazenado.

Saída esperada:
19

O número 19 sem aspas é um valor numérico. Já "19" entre aspas é uma string.

Entender a diferença entre tipos de dados evita erros quando o programa precisa calcular, comparar ou transformar informações.""",
            "idade = 19\nprint(idade)",
            "Qual alternativa é um número inteiro?",
            ['"25"', "25", "25.5"],
            "b",
        ),
        (
            "Números decimais",
            """O tipo float representa números com casas decimais. Ele é útil para representar medidas, preços e outros valores numéricos que não são inteiros.

Exemplo:
preco = 12.50
print(preco)

Saída esperada:
12.5

O Python pode exibir um número decimal sem zeros finais desnecessários. Isso não significa que o valor tenha sido alterado.

Em Python, a parte decimal é escrita com ponto, e não com vírgula. Por exemplo, 3.5 é um número decimal, enquanto 3,5 é interpretado como dois valores separados por uma vírgula.""",
            "preco = 12.5\nprint(preco)",
            "Qual valor é do tipo float?",
            ["10", "3.14", '"3.14"'],
            "b",
        ),
        (
            "Valores booleanos",
            """O tipo bool representa um valor lógico. Existem dois valores booleanos: True e False.

Eles são utilizados para representar condições que podem ser verdadeiras ou falsas.

Exemplo:
esta_estudando = True
print(esta_estudando)

Saída esperada:
True

Os valores True e False são escritos com a primeira letra maiúscula. Não são a mesma coisa que os textos "True" e "False".

Valores booleanos aparecem frequentemente em comparações, validações e decisões tomadas pelo programa.""",
            "esta_estudando = True\nprint(esta_estudando)",
            "Qual alternativa é um valor booleano?",
            ['"True"', "True", '"Verdadeiro"'],
            "b",
        ),
        (
            "Variáveis",
            """Uma variável é um nome associado a um valor. Ela permite guardar uma informação para usá-la em outras partes do programa.

Exemplo:
nome = "Ana"
print(nome)

A primeira linha associa o texto Ana à variável nome. A segunda consulta essa variável e exibe o valor.

Saída esperada:
Ana

O sinal = é usado para atribuir um valor. O nome da variável deve seguir as regras de nomenclatura do Python e não pode conter espaços.

Variáveis ajudam a evitar a repetição de valores e permitem que o programa trabalhe com informações que podem mudar.""",
            'nome = "Ana"\nprint(nome)',
            "Como associar o texto Ana à variável nome?",
            ['nome = "Ana"', 'print = "Ana"', "nome == Ana"],
            "a",
        ),
        (
            "Usando variáveis",
            """Depois de criar uma variável, podemos utilizar seu valor em diferentes instruções.

Exemplo:
idade = 19
print(idade)
print(idade + 1)

A primeira chamada de print() exibe 19. A segunda calcula 19 + 1 e exibe 20.

Saída esperada:
19
20

O valor associado a uma variável pode ser utilizado em expressões. Isso torna possível calcular resultados sem precisar repetir manualmente os mesmos valores.

Escolher nomes claros, como idade, preco e quantidade, também facilita a leitura do programa.""",
            "idade = 19\nprint(idade)\nprint(idade + 1)",
            "O que print(idade) exibe quando idade = 19?",
            ["O texto idade", "O valor 19", "O valor 20"],
            "b",
        ),
        (
            "Comentários",
            """Comentários são trechos escritos para explicar o código. O Python ignora o conteúdo de um comentário iniciado pelo símbolo #.

Exemplo:
# Guarda o nome do usuário
nome = "Ana"
print(nome)

A primeira linha explica a finalidade da variável. As duas linhas seguintes são instruções executáveis.

Comentários úteis explicam decisões ou partes que poderiam ser difíceis de entender. Não é necessário comentar cada linha quando o código já está claro.

O símbolo # inicia um comentário de linha. Ele não é equivalente aos símbolos usados para comentários em todas as outras linguagens.""",
            '# Guarda o nome\nnome = "Ana"\nprint(nome)',
            "Qual símbolo inicia um comentário de linha em Python?",
            ["//", "#", "<!--"],
            "b",
        ),
        (
            "Revisão inicial",
            """Você conheceu os primeiros elementos de um programa Python: print(), strings, números, valores booleanos, variáveis e comentários.

Observe o exemplo:
linguagem = "Python"
idade = 19
estudando = True

print(linguagem)
print(idade)
print(estudando)

O programa guarda três valores em variáveis e depois exibe cada um deles.

Saída esperada:
Python
19
True

Antes de avançar, procure reconhecer o tipo de cada valor e diferenciar a atribuição de um valor da exibição desse valor.""",
            'linguagem = "Python"\nidade = 19\nestudando = True\nprint(linguagem)\nprint(idade)\nprint(estudando)',
            "Qual é a principal finalidade de uma variável?",
            ["Guardar ou referenciar um valor", "Desligar o computador", "Instalar o Python"],
            "a",
        ),
    ],

    # NÍVEL 2 — FUNDAMENTOS BÁSICOS
    [
        (
            "Variáveis e armazenamento de valores",
            """Uma variável é um nome associado a um valor. Ela permite armazenar informações e reutilizá-las ao longo do programa.

Exemplo:
nome = "Ana"
idade = 20

A primeira linha associa o texto Ana à variável nome. A segunda associa o inteiro 20 à variável idade.

Podemos consultar esses valores usando print(nome) e print(idade).

Saída esperada:
Ana
20

Atenção: print("nome") exibe a palavra nome literalmente. Já print(nome), sem aspas, consulta a variável.

Variáveis são úteis para guardar nomes, preços, quantidades e resultados usados por um programa.""",
            'nome = "Ana"\nidade = 20\nprint(nome)\nprint(idade)',
            "Considere a = 5, b = 6 e print(a + b). O que será exibido?",
            ["56", "11", "a + b"],
            "b",
        ),
        (
            "Tipos de dados",
            """Cada valor possui um tipo, que influencia como o Python trabalha com ele.

str representa textos, como "Python".
int representa números inteiros, como 20.
float representa números decimais, como 3.5.
bool representa valores lógicos: True ou False.

Exemplo:
nome = "João"
idade = 19
altura = 1.75
estudando = True

Podemos consultar o tipo de uma variável usando type().

Exemplo:
print(type(idade))

Saída:
<class 'int'>

As aspas fazem diferença: "20" é texto, enquanto 20 é um inteiro. Mesmo que pareçam semelhantes na tela, seus tipos são diferentes.""",
            'idade = 19\npreco = 3.5\nnome = "João"\nprint(type(idade))\nprint(type(preco))\nprint(type(nome))',
            'Qual é o tipo do valor "20", escrito entre aspas?',
            ["int", "str", "float"],
            "b",
        ),
        (
            "Exibindo informações com print()",
            """A função print() mostra informações na saída do programa. Ela pode exibir textos, números, variáveis e resultados de expressões.

Exemplo:
nome = "Ana"
idade = 20
print(nome)
print(idade)
print("Bem-vinda!")

Saída:
Ana
20
Bem-vinda!

Cada chamada de print() normalmente termina a linha exibida. Também podemos passar vários valores separados por vírgulas.

Exemplo:
print("Idade:", idade)

Saída:
Idade: 20

As vírgulas permitem exibir valores de tipos diferentes sem precisar concatenar tudo manualmente. Esquecer aspas ou parênteses pode causar um erro de sintaxe.""",
            'produto = "Teclado"\npreco = 80\nprint("Produto:", produto)\nprint("Preço:", preco)',
            'O que print("Produto:", produto) faz se produto = "Teclado"?',
            ["Exibe Produto: Teclado", "Cria uma variável chamada Produto", "Apaga o valor de produto"],
            "a",
        ),
        (
            "Recebendo dados com input()",
            """A função input() permite que o usuário digite uma informação durante a execução do programa.

Exemplo:
nome = input("Digite seu nome: ")
print("Olá,", nome)

O Python mostra a mensagem e espera que a pessoa digite algo. O texto digitado é associado à variável nome.

Se a pessoa digitar Ana, a saída final será:
Olá, Ana

Importante: input() retorna texto, mesmo quando a pessoa digita algarismos. Para fazer cálculos com um número digitado, geralmente precisamos converter esse valor para um tipo numérico.

Essa função torna os programas interativos, pois permite receber informações diferentes a cada execução.""",
            'nome = input("Digite seu nome: ")\nprint("Olá,", nome)',
            "Qual é a finalidade de input()?",
            ["Exibir somente resultados", "Receber dados digitados pelo usuário", "Converter qualquer valor em inteiro"],
            "b",
        ),
        (
            "Convertendo valores com int() e float()",
            """Como input() retorna texto, podemos precisar converter a entrada antes de realizar cálculos.

int() converte um valor compatível para inteiro.
float() converte um valor compatível para número decimal.
str() converte um valor para texto.

Exemplo:
idade_texto = input("Idade: ")
idade = int(idade_texto)
print(idade + 1)

Se a pessoa digitar 20, int() transforma o texto "20" no número inteiro 20. Depois, o programa soma 1 e exibe 21.

Também podemos escrever idade = int(input("Idade: ")).

Atenção: int("vinte") provoca ValueError, porque o texto não representa um inteiro válido. Programas reais precisam considerar entradas inesperadas.""",
            'numero = int("20")\nprint(numero + 1)',
            'Qual é a saída de numero = int("20") seguido de print(numero + 1)?',
            ["201", "21", "Erro em todos os casos"],
            "b",
        ),
        (
            "Operadores e expressões",
            """Operadores permitem realizar operações com valores. Uma expressão combina valores, variáveis e operadores para produzir um resultado.

Os principais operadores aritméticos são:
+ soma
- subtração
* multiplicação
/ divisão comum
// divisão inteira
% resto da divisão
** potência

Exemplo:
preco = 10
quantidade = 3
total = preco * quantidade
print(total)

Saída:
30

A variável total recebe o resultado da multiplicação. A divisão comum pode produzir um float, mesmo quando o resultado matemático é inteiro.

Compreender expressões é importante porque programas usam cálculos para processar dados e produzir resultados.""",
            "preco = 10\nquantidade = 3\ntotal = preco * quantidade\nprint(total)",
            "Se preco = 10 e quantidade = 3, qual é a saída de print(preco * quantidade)?",
            ["13", "30", "103"],
            "b",
        ),
        (
            "Juntando textos e usando f-strings",
            """Concatenar significa juntar textos. O operador + pode juntar duas strings.

Exemplo:
nome = "Ana"
mensagem = "Olá, " + nome
print(mensagem)

Saída:
Olá, Ana

Se tentarmos somar diretamente uma string e um inteiro, como "Idade: " + 20, o Python gera TypeError. Uma solução é converter o número com str(20).

Outra forma prática é usar uma f-string:
idade = 20
print(f"Idade: {idade}")

O prefixo f permite colocar o valor de uma variável entre chaves dentro do texto. Isso deixa mensagens com variáveis mais legíveis.""",
            'nome = "Ana"\nidade = 20\nprint(f"{nome} tem {idade} anos")',
            'Qual é a saída com nome = "Ana" e idade = 20?',
            ["nome tem idade anos", "Ana tem 20 anos", "Erro sempre que há chaves"],
            "b",
        ),
        (
            "Comparando valores",
            """Comparações verificam uma relação entre valores e retornam True ou False.

== verifica igualdade.
!= verifica diferença.
> verifica se um valor é maior.
< verifica se um valor é menor.
>= verifica se é maior ou igual.
<= verifica se é menor ou igual.

Exemplo:
idade = 20
print(idade >= 18)

A saída é True porque 20 é maior que 18.

Cuidado para não confundir = com ==. Um único = atribui um valor a uma variável. Dois sinais de igual comparam valores.

Comparações são usadas em condições, validações e regras de negócio.""",
            "idade = 20\nprint(idade >= 18)\nprint(idade == 18)",
            "O que será exibido por print(10 == 10)?",
            ["True", "False", "10 como texto"],
            "a",
        ),
        (
            "Valores lógicos e operadores and, or e not",
            """O tipo bool possui dois valores: True e False. Eles representam verdadeiro e falso.

and exige que as duas condições sejam verdadeiras para produzir True.
or produz True quando pelo menos uma condição é verdadeira.
not inverte o valor lógico.

Exemplos:
print(True and False)
print(True or False)
print(not True)

Saída:
False
True
False

Podemos combinar comparações:
idade = 20
autorizado = True
print(idade >= 18 and autorizado)

O resultado é True porque as duas condições são verdadeiras. Esses operadores ajudam a representar regras com mais de uma exigência.""",
            "idade = 20\nautorizado = True\nprint(idade >= 18 and autorizado)",
            "Qual é o resultado de True and False?",
            ["True", "False", "20"],
            "b",
        ),
        (
            "Revisão prática de fundamentos",
            """Nesta aula, você reuniu os conceitos essenciais para criar programas: variáveis, tipos de dados, print(), input(), conversões e operadores.

Observe:
produto = input("Produto: ")
preco = float(input("Preço: "))
quantidade = int(input("Quantidade: "))
total = preco * quantidade
print(f"{produto}: R$ {total:.2f}")

A primeira linha recebe o nome do produto como texto.
A segunda converte o preço para float.
A terceira converte a quantidade para int.
A quarta calcula o total.
A última exibe o resultado com duas casas decimais.

Se a pessoa digitar Café, 4.5 e 2, o resultado será:
Café: R$ 9.00

O exemplo combina entrada, conversão, processamento e saída, uma estrutura comum em programas reais.""",
            'produto = "Café"\npreco = 4.5\nquantidade = 2\ntotal = preco * quantidade\nprint(f"{produto}: R$ {total:.2f}")',
            'Com produto = "Café", preco = 4.5 e quantidade = 2, o que será exibido?',
            ["Café: R$ 6.50", "Café: R$ 9.00", "Café: R$ 45.02"],
            "b",
        ),
    ],

    # NÍVEL 3 — LÓGICA DE PROGRAMAÇÃO
    [
        (
            "O que é um algoritmo",
            """Um algoritmo é uma sequência organizada de passos para resolver um problema. Ele não depende necessariamente de uma linguagem de programação: uma receita e um procedimento de atendimento também podem ser descritos como algoritmos.

Em programação, primeiro identificamos os dados necessários, depois definimos as operações e por fim determinamos como apresentar o resultado.

Exemplo:
preco = 50
desconto = 10
total = preco - desconto
print(total)

O programa recebe valores, realiza o processamento e exibe o resultado.

Saída:
40

Essa estrutura de entrada, processamento e saída ajuda a organizar soluções antes de escrever programas maiores.""",
            "preco = 50\ndesconto = 10\ntotal = preco - desconto\nprint(total)",
            "Qual é a finalidade de um algoritmo?",
            ["Organizar passos para resolver um problema", "Substituir o sistema operacional", "Armazenar somente imagens"],
            "a",
        ),
        (
            "Decompondo problemas",
            """Decomposição significa dividir um problema grande em partes menores. Isso facilita entender, implementar e testar cada parte.

Imagine um programa de vendas. Podemos separar o trabalho em:
1. Receber o preço.
2. Receber a quantidade.
3. Calcular o total.
4. Exibir o resultado.

Cada etapa possui uma responsabilidade clara.

Exemplo:
preco = 12
quantidade = 4
total = preco * quantidade
print(total)

Saída:
48

Separar etapas também ajuda a localizar erros. Se o resultado estiver errado, podemos verificar se a entrada, o cálculo ou a exibição está causando o problema.""",
            "preco = 12\nquantidade = 4\ntotal = preco * quantidade\nprint(total)",
            "Por que dividir um problema em partes menores?",
            ["Para organizar e facilitar a solução", "Para tornar o código sempre mais longo", "Para impedir que o programa seja testado"],
            "a",
        ),
        (
            "Rastreamento de variáveis",
            """Rastrear um programa significa acompanhar como os valores mudam durante a execução.

Exemplo:
pontos = 10
pontos = pontos + 5
pontos = pontos - 2
print(pontos)

Na primeira linha, pontos recebe 10.
Na segunda, o valor atual é somado a 5, passando a 15.
Na terceira, 2 é subtraído, passando a 13.

Saída:
13

A expressão pontos = pontos + 5 não é uma equação matemática comum. Em Python, ela calcula o lado direito e atribui o resultado à variável do lado esquerdo.

Esse raciocínio é útil para depurar programas e entender contadores, saldos e pontuações.""",
            "pontos = 10\npontos = pontos + 5\npontos = pontos - 2\nprint(pontos)",
            "Qual valor será exibido ao final?",
            ["10", "13", "15"],
            "b",
        ),
        (
            "Operadores de atribuição",
            """Operadores de atribuição modificam o valor associado a uma variável.

O operador = atribui um valor.
O operador += soma um valor ao existente.
O operador -= subtrai um valor.
O operador *= multiplica pelo valor informado.

Exemplo:
saldo = 100
saldo += 25
saldo -= 10
print(saldo)

O saldo começa em 100. Depois aumenta para 125 e diminui para 115.

Saída:
115

Essas formas abreviadas tornam o código mais compacto. É importante acompanhar o valor anterior da variável para entender o resultado de cada operação.""",
            "saldo = 100\nsaldo += 25\nsaldo -= 10\nprint(saldo)",
            "Qual valor fica armazenado em saldo?",
            ["90", "115", "125"],
            "b",
        ),
        (
            "Ordem das operações",
            """O Python segue regras de precedência para determinar a ordem dos cálculos. Multiplicações e divisões são avaliadas antes de somas e subtrações, salvo quando os parênteses alteram a ordem.

Exemplo:
resultado = 2 + 3 * 4
print(resultado)

Primeiro, o Python calcula 3 * 4, que resulta em 12. Depois soma 2, chegando a 14.

Saída:
14

Com parênteses:
resultado = (2 + 3) * 4

Nesse caso, a soma ocorre primeiro e o resultado é 20.

Usar parênteses pode deixar expressões complexas mais claras, mesmo quando não são estritamente necessários.""",
            "resultado = 2 + 3 * 4\nprint(resultado)",
            "Qual é o resultado de 2 + 3 * 4?",
            ["20", "14", "24"],
            "b",
        ),
        (
            "Funções como ferramentas",
            """Uma função é um bloco de código identificado por um nome e destinado a realizar uma tarefa. Algumas funções já vêm disponíveis no Python, como print(), len() e type().

Exemplo:
nome = "Python"
tamanho = len(nome)
print(tamanho)

len() conta quantos caracteres existem na string. A palavra Python possui seis caracteres.

Saída:
6

Usar funções prontas evita reimplementar operações comuns. Mais adiante, você aprenderá a criar suas próprias funções para dividir programas em componentes reutilizáveis.""",
            'nome = "Python"\ntamanho = len(nome)\nprint(tamanho)',
            "O que len() retorna quando recebe uma string?",
            ["A quantidade de caracteres", "O tipo de computador", "O último caractere sempre"],
            "a",
        ),
        (
            "Transformando requisitos em código",
            """Um requisito descreve o que o programa precisa fazer. Antes de programar, é útil transformar o requisito em passos claros.

Requisito: calcular o preço total de vários itens.
Passos:
1. Guardar o preço unitário.
2. Guardar a quantidade.
3. Multiplicar os valores.
4. Exibir o total.

Exemplo:
preco = 8
quantidade = 3
total = preco * quantidade
print(f"Total: R$ {total:.2f}")

Saída:
Total: R$ 24.00

O programa atende ao requisito porque calcula e apresenta o total. Em projetos reais, também devemos pensar em entradas inválidas, limites e situações especiais.""",
            "preco = 8\nquantidade = 3\ntotal = preco * quantidade\nprint(f'Total: R$ {total:.2f}')",
            "Qual etapa calcula o valor total?",
            ["Multiplicar preço pela quantidade", "Renomear o computador", "Criar um comentário"],
            "a",
        ),
        (
            "Depuração básica",
            """Depurar é investigar um programa para encontrar e corrigir problemas. Um erro pode estar na sintaxe, nos valores usados ou na lógica da solução.

Exemplo com problema:
preco = 10
quantidade = 3
total = preco + quantidade
print(total)

O programa executa, mas apresenta 13, pois somou os valores. Se o objetivo era calcular o custo de três unidades, a operação adequada é multiplicar.

Versão corrigida:
total = preco * quantidade

Saída esperada:
30

Nem todo erro provoca uma mensagem de exceção. Às vezes, o programa funciona tecnicamente, mas não resolve o problema correto. Por isso, compare o resultado com o requisito.""",
            "preco = 10\nquantidade = 3\ntotal = preco * quantidade\nprint(total)",
            "Para calcular o custo de várias unidades, qual operação é adequada?",
            ["Somar preço e quantidade", "Multiplicar preço pela quantidade", "Concatenar os dois valores como texto"],
            "b",
        ),
        (
            "Testando resultados",
            """Um teste verifica se um programa produz o resultado esperado para uma entrada conhecida.

Considere uma função simples que calcula a área de um retângulo multiplicando largura por altura.

Exemplo:
largura = 5
altura = 4
area = largura * altura
print(area)

O resultado esperado é 20. Se o programa exibir outro valor, precisamos investigar o cálculo.

Testar somente um caso não garante que o programa esteja correto para todas as entradas. Também podemos testar zero, valores maiores e dados inválidos quando fizer sentido.

Os testes tornam os problemas mais fáceis de identificar antes que o programa seja utilizado por outras pessoas.""",
            "largura = 5\naltura = 4\narea = largura * altura\nprint(area)",
            "Qual resultado o teste deve esperar?",
            ["9", "20", "54"],
            "b",
        ),
        (
            "Revisão de lógica",
            """Nesta etapa, você praticou algoritmos, decomposição, rastreamento de variáveis, precedência, funções e depuração.

Um programa pode ser entendido como uma sequência de transformações de dados. A entrada fornece informações; o processamento transforma essas informações; a saída apresenta o resultado.

Exemplo:
quantidade = 4
preco = 7
subtotal = quantidade * preco
desconto = 5
total = subtotal - desconto
print(total)

O subtotal é 28. Depois de subtrair 5, o total é 23.

Saída:
23

Ao analisar um programa, acompanhe cada variável e verifique se cada instrução contribui para o objetivo definido.""",
            "quantidade = 4\npreco = 7\nsubtotal = quantidade * preco\ntotal = subtotal - 5\nprint(total)",
            "Qual é o valor final exibido?",
            ["23", "28", "33"],
            "a",
        ),
    ],

    # NÍVEL 4 — CONTROLE DE FLUXO
    [
        (
            "Tomando decisões com if",
            """A instrução if permite executar um bloco somente quando uma condição é verdadeira.

Exemplo:
idade = 20
if idade >= 18:
    print("Maior de idade")

O Python avalia idade >= 18. Como a condição é verdadeira, executa o bloco indentado.

Saída:
Maior de idade

A indentação, ou recuo, define quais instruções pertencem ao bloco. Em Python, ela faz parte da sintaxe.

Se a condição for falsa, o bloco do if será ignorado. Isso permite que o comportamento do programa dependa dos dados recebidos.""",
            'idade = 20\nif idade >= 18:\n    print("Maior de idade")',
            "Quando o bloco de um if é executado?",
            ["Quando sua condição é verdadeira", "Sempre duas vezes", "Somente quando o programa fecha"],
            "a",
        ),
        (
            "Usando else",
            """A instrução else define um caminho alternativo quando a condição do if é falsa.

Exemplo:
idade = 16
if idade >= 18:
    print("Adulto")
else:
    print("Menor")

Como 16 não é maior ou igual a 18, o programa executa o bloco else.

Saída:
Menor

O else não recebe uma condição própria. Ele representa o caminho alternativo ao if associado.

Esse padrão é útil quando precisamos escolher entre duas possibilidades, como aprovado ou reprovado, disponível ou indisponível.""",
            'idade = 16\nif idade >= 18:\n    print("Adulto")\nelse:\n    print("Menor")',
            "Qual texto será exibido?",
            ["Adulto", "Menor", "Os dois textos"],
            "b",
        ),
        (
            "Múltiplas alternativas com elif",
            """elif significa uma alternativa condicional. Ele permite verificar outra condição quando as anteriores não foram satisfeitas.

Exemplo:
nota = 7
if nota >= 9:
    print("Excelente")
elif nota >= 6:
    print("Aprovado")
else:
    print("Revisar")

A primeira condição é falsa. O Python então verifica nota >= 6, que é verdadeira, e exibe Aprovado.

Saída:
Aprovado

A ordem importa: assim que uma condição de uma cadeia if/elif/else é verdadeira, o Python executa aquele bloco e ignora as alternativas seguintes.""",
            'nota = 7\nif nota >= 9:\n    print("Excelente")\nelif nota >= 6:\n    print("Aprovado")\nelse:\n    print("Revisar")',
            "Qual mensagem aparece para nota = 7?",
            ["Excelente", "Aprovado", "Revisar"],
            "b",
        ),
        (
            "Condições combinadas",
            """Podemos combinar condições usando and e or.

and exige que todas as condições sejam verdadeiras.
or exige que pelo menos uma condição seja verdadeira.

Exemplo:
idade = 25
tem_ingresso = True

if idade >= 18 and tem_ingresso:
    print("Entrada permitida")

As duas condições são verdadeiras, então a mensagem aparece.

Saída:
Entrada permitida

Ao criar regras, verifique se a combinação lógica corresponde ao requisito. Uma condição incorreta pode permitir ou bloquear uma ação indevidamente.""",
            'idade = 25\ntem_ingresso = True\nif idade >= 18 and tem_ingresso:\n    print("Entrada permitida")',
            "Com and, o que é necessário para a expressão ser verdadeira?",
            ["Todas as condições precisam ser verdadeiras", "Basta qualquer condição ser verdadeira", "Todas as condições precisam ser falsas"],
            "a",
        ),
        (
            "Laços while",
            """O while repete um bloco enquanto sua condição for verdadeira.

Exemplo:
contador = 0
while contador < 3:
    print(contador)
    contador += 1

O programa exibe 0, 1 e 2. Depois, contador passa a 3, a condição se torna falsa e o laço termina.

Saída:
0
1
2

É importante atualizar as variáveis usadas na condição. Caso contrário, o programa pode entrar em um laço infinito, repetindo o bloco sem parar.

O while é útil quando o número de repetições depende de uma condição.""",
            "contador = 0\nwhile contador < 3:\n    print(contador)\n    contador += 1",
            "Quantas vezes print() é executado?",
            ["Duas", "Três", "Quatro"],
            "b",
        ),
        (
            "Laços for e range",
            """O for percorre os itens de uma sequência. Com range(), podemos produzir uma sequência de números para controlar repetições.

Exemplo:
for numero in range(3):
    print(numero)

range(3) produz os números 0, 1 e 2. O limite final não é incluído.

Saída:
0
1
2

Também podemos definir início e fim: range(1, 4) produz 1, 2 e 3.

O for costuma ser adequado quando queremos percorrer uma coleção ou repetir uma tarefa por uma quantidade conhecida de vezes.""",
            "for numero in range(3):\n    print(numero)",
            "Quais valores são exibidos?",
            ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3"],
            "b",
        ),
        (
            "Percorrendo listas",
            """Uma lista guarda vários itens em uma sequência. O for pode visitar cada item sem precisar acessar os índices manualmente.

Exemplo:
frutas = ["maçã", "pera", "uva"]
for fruta in frutas:
    print(fruta)

A cada repetição, a variável fruta recebe o próximo item da lista.

Saída:
maçã
pera
uva

Esse padrão é usado para processar nomes, produtos, registros e outros conjuntos de dados. O código se adapta à quantidade de itens da lista sem precisar escrever um print() para cada elemento.""",
            'frutas = ["maçã", "pera", "uva"]\nfor fruta in frutas:\n    print(fruta)',
            "Quantas vezes o corpo do for é executado?",
            ["Uma vez", "Três vezes", "Quatro vezes"],
            "b",
        ),
        (
            "Interrompendo com break",
            """A instrução break encerra imediatamente o laço mais próximo.

Exemplo:
for numero in range(5):
    if numero == 2:
        break
    print(numero)

Quando numero chega a 2, a condição é verdadeira e break termina o laço. O print() daquela repetição não é executado.

Saída:
0
1

break é útil quando encontramos o que procuramos e não precisamos continuar percorrendo os itens.

Use-o com cuidado para que a interrupção corresponda à lógica desejada.""",
            "for numero in range(5):\n    if numero == 2:\n        break\n    print(numero)",
            "Qual é a função de break?",
            ["Encerra o laço atual", "Reinicia o programa", "Pula sempre para a próxima repetição"],
            "a",
        ),
        (
            "Pulando uma repetição com continue",
            """A instrução continue interrompe a iteração atual e passa para a próxima, sem executar o restante do bloco daquela repetição.

Exemplo:
for numero in range(4):
    if numero == 2:
        continue
    print(numero)

Quando numero vale 2, o programa pula o print() e continua com o próximo número.

Saída:
0
1
3

Diferentemente de break, continue não encerra o laço inteiro. Ele apenas pula o restante da iteração atual.

Esse recurso pode ser útil para ignorar itens que não atendem a um critério.""",
            "for numero in range(4):\n    if numero == 2:\n        continue\n    print(numero)",
            "Qual número não será exibido?",
            ["1", "2", "3"],
            "b",
        ),
        (
            "Revisão de controle de fluxo",
            """Condições escolhem quais blocos executar. Laços repetem instruções. break encerra um laço e continue pula para a próxima iteração.

Exemplo:
for numero in range(5):
    if numero % 2 == 0:
        print(numero)

O operador % calcula o resto da divisão. Números pares deixam resto zero quando divididos por 2.

Saída:
0
2
4

A condição do if é avaliada em cada repetição. Assim, o programa exibe somente os valores que atendem ao critério.

Esse tipo de lógica aparece em filtros, validações e processamento de coleções.""",
            "for numero in range(5):\n    if numero % 2 == 0:\n        print(numero)",
            "Quais valores são exibidos?",
            ["1, 3", "0, 2, 4", "0, 1, 2, 3, 4"],
            "b",
        ),
    ],

    # NÍVEL 5 — MANIPULAÇÃO DE DADOS
    [
        (
            "Criando listas",
            """Uma lista permite armazenar vários valores em uma única estrutura. Em Python, listas são escritas entre colchetes e seus itens são separados por vírgulas.

Exemplo:
frutas = ["maçã", "pera", "uva"]
print(frutas)

A lista mantém os itens em uma sequência e permite acessar, adicionar ou remover elementos.

Uma lista pode conter strings, números ou outros tipos de dados. Em geral, é melhor manter uma estrutura organizada de acordo com o propósito dos dados.

Listas são muito utilizadas para representar conjuntos de produtos, tarefas, notas e registros.""",
            'frutas = ["maçã", "pera", "uva"]\nprint(frutas)',
            "Qual símbolo delimita uma lista em Python?",
            ["Parênteses obrigatoriamente", "Colchetes", "Chaves sempre"],
            "b",
        ),
        (
            "Índices de listas",
            """Cada item de uma lista possui um índice. Em Python, o primeiro índice é 0, o segundo é 1 e assim por diante.

Exemplo:
numeros = [10, 20, 30]
print(numeros[1])

O índice 1 corresponde ao segundo elemento, que é 20.

Saída:
20

Tentar acessar um índice inexistente pode gerar IndexError. Antes de acessar uma posição, verifique o tamanho da lista ou percorra seus elementos com for.

Os índices também permitem modificar elementos específicos de uma lista mutável.""",
            "numeros = [10, 20, 30]\nprint(numeros[1])",
            "Qual valor está no índice 1?",
            ["10", "20", "30"],
            "b",
        ),
        (
            "Adicionando elementos",
            """O método append() adiciona um elemento ao final de uma lista.

Exemplo:
tarefas = ["estudar"]
tarefas.append("praticar")
print(tarefas)

A lista passa a conter dois itens na ordem em que foram adicionados.

Saída:
['estudar', 'praticar']

append() modifica a lista original e não precisa criar uma nova lista. Isso é útil quando os dados são coletados aos poucos, por exemplo, ao registrar tarefas ou produtos.

Não confunda append() com extend(): append() adiciona um único elemento, enquanto extend() adiciona os elementos de um iterável.""",
            'tarefas = ["estudar"]\ntarefas.append("praticar")\nprint(tarefas)',
            "O que append() faz?",
            ["Adiciona um item ao final da lista", "Remove todos os itens", "Ordena automaticamente a lista"],
            "a",
        ),
        (
            "Removendo e alterando itens",
            """Listas são mutáveis, ou seja, seus elementos podem ser alterados após a criação.

Exemplo:
cores = ["azul", "verde", "vermelho"]
cores[1] = "amarelo"
cores.remove("vermelho")
print(cores)

A primeira operação substitui o elemento do índice 1. A segunda remove a primeira ocorrência de vermelho.

Saída:
['azul', 'amarelo']

remove() gera ValueError se o valor não for encontrado. Para remover por posição, existe pop(), que também pode devolver o elemento removido.

Escolha o método de acordo com a informação que você possui: o valor do item ou sua posição.""",
            'cores = ["azul", "verde", "vermelho"]\ncores[1] = "amarelo"\ncores.remove("vermelho")\nprint(cores)',
            "Qual lista resulta após as duas operações?",
            ["['azul', 'verde']", "['azul', 'amarelo']", "['amarelo', 'vermelho']"],
            "b",
        ),
        (
            "Tuplas",
            """Uma tupla armazena vários valores em uma sequência, geralmente usando parênteses.

Exemplo:
coordenada = (10, 20)
print(coordenada[0])

A saída é 10, porque o índice 0 representa o primeiro elemento.

Tuplas são imutáveis: depois de criadas, seus elementos não podem ser substituídos diretamente. Isso pode ser útil para representar dados que devem permanecer fixos, como uma coordenada.

Listas e tuplas são semelhantes na forma de acessar itens, mas diferem principalmente na possibilidade de modificação.""",
            "coordenada = (10, 20)\nprint(coordenada[0])",
            "Qual característica distingue uma tupla de uma lista?",
            ["A tupla é imutável", "A tupla só aceita textos", "A tupla não pode ser percorrida"],
            "a",
        ),
        (
            "Dicionários e pares chave-valor",
            """Um dicionário associa chaves a valores. Ele é útil quando cada informação tem um nome, como nome, idade ou email.

Exemplo:
pessoa = {
    "nome": "Ana",
    "idade": 20
}
print(pessoa["nome"])

A chave nome permite recuperar o valor Ana.

Saída:
Ana

Podemos acessar, adicionar ou atualizar valores por meio de suas chaves. A chave precisa existir para uma consulta direta com colchetes; caso contrário, pode ocorrer KeyError.

Dicionários são muito usados para representar registros e dados recebidos de APIs.""",
            'pessoa = {"nome": "Ana", "idade": 20}\nprint(pessoa["nome"])',
            "O que pessoa['nome'] retorna?",
            ["A chave idade", "O valor Ana", "O dicionário inteiro como texto"],
            "b",
        ),
        (
            "Conjuntos e valores únicos",
            """Um conjunto, representado pelo tipo set, armazena elementos únicos. Valores repetidos são eliminados da coleção.

Exemplo:
numeros = {1, 1, 2, 3}
print(len(numeros))

O conjunto contém os valores 1, 2 e 3. A repetição do número 1 não cria um segundo elemento.

Saída:
3

Conjuntos são úteis para eliminar duplicatas e verificar pertencimento com o operador in.

Diferentemente das listas, conjuntos não devem ser usados quando você precisa preservar uma ordem posicional ou acessar elementos por índice.""",
            "numeros = {1, 1, 2, 3}\nprint(len(numeros))",
            "Quantos elementos únicos existem no conjunto?",
            ["2", "3", "4"],
            "b",
        ),
        (
            "Manipulando strings",
            """Strings possuem métodos que ajudam a transformar e consultar textos.

upper() retorna uma versão em maiúsculas.
lower() retorna uma versão em minúsculas.
strip() remove espaços em branco das extremidades.
replace() substitui ocorrências de um trecho.

Exemplo:
nome = "  Ana  "
nome = nome.strip()
print(nome.upper())

strip() remove os espaços do início e do fim. Depois, upper() transforma as letras em maiúsculas.

Saída:
ANA

Strings são imutáveis: esses métodos retornam novas strings, em vez de modificar a string original diretamente. Para guardar o resultado, normalmente atribuímos o retorno a uma variável.""",
            'nome = "  Ana  "\nnome = nome.strip()\nprint(nome.upper())',
            "O que upper() faz?",
            ["Transforma as letras em maiúsculas", "Remove números", "Converte o texto em uma lista de arquivos"],
            "a",
        ),
        (
            "Percorrendo e filtrando dados",
            """Podemos usar for e if para percorrer uma coleção e selecionar apenas os elementos que atendem a um critério.

Exemplo:
notas = [4, 8, 6, 9]
for nota in notas:
    if nota >= 7:
        print(nota)

O laço visita cada nota. O if permite exibir somente as notas maiores ou iguais a 7.

Saída:
8
9

Esse padrão é chamado de filtragem. Ele aparece em listas de produtos disponíveis, usuários ativos, resultados de pesquisas e muitos outros casos.

A condição deve representar o critério que você deseja aplicar aos dados.""",
            "notas = [4, 8, 6, 9]\nfor nota in notas:\n    if nota >= 7:\n        print(nota)",
            "Quais notas serão exibidas?",
            ["4 e 6", "8 e 9", "Todas as notas"],
            "b",
        ),
        (
            "Revisão de coleções",
            """Listas, tuplas, dicionários e conjuntos resolvem necessidades diferentes.

Listas mantêm uma sequência mutável.
Tuplas mantêm uma sequência imutável.
Dicionários associam chaves a valores.
Conjuntos armazenam elementos únicos.

Exemplo:
estoque = {"teclado": 4, "mouse": 7}
estoque["teclado"] -= 1
print(estoque["teclado"])

O programa consulta a quantidade de teclados e reduz o valor em uma unidade.

Saída:
3

Escolher a estrutura correta facilita organizar e consultar os dados. Em aplicações maiores, a estrutura influencia a clareza e a forma de processar as informações.""",
            'estoque = {"teclado": 4, "mouse": 7}\nestoque["teclado"] -= 1\nprint(estoque["teclado"])',
            "Qual valor será exibido?",
            ["3", "4", "7"],
            "a",
        ),
    ],

    # NÍVEL 6 — FUNÇÕES E ORGANIZAÇÃO
    [
        (
            "Criando funções com def",
            """Uma função agrupa instruções que realizam uma tarefa. Ela pode ser chamada várias vezes, evitando a repetição do mesmo código.

Exemplo:
def saudar():
    print("Olá!")

saudar()
saudar()

def inicia a definição da função. O bloco indentado contém as instruções que serão executadas quando a função for chamada.

Saída:
Olá!
Olá!

Definir uma função não significa executá-la imediatamente. A chamada saudar() é que faz o corpo da função ser executado.

Funções ajudam a dividir um programa em partes menores, nomeadas e reutilizáveis.""",
            'def saudar():\n    print("Olá!")\n\nsaudar()',
            "Qual palavra-chave define uma função em Python?",
            ["func", "def", "function"],
            "b",
        ),
        (
            "Parâmetros e argumentos",
            """Parâmetros são nomes declarados na definição de uma função. Argumentos são os valores fornecidos quando a função é chamada.

Exemplo:
def dobrar(numero):
    return numero * 2

print(dobrar(4))

numero é o parâmetro. O valor 4 é o argumento fornecido na chamada. A função calcula 4 * 2 e devolve o resultado.

Saída:
8

Parâmetros permitem que uma função execute a mesma tarefa com diferentes valores. Isso evita criar uma função diferente para cada número ou pessoa.""",
            "def dobrar(numero):\n    return numero * 2\n\nprint(dobrar(4))",
            "Qual valor é passado como argumento em dobrar(4)?",
            ["numero", "4", "2"],
            "b",
        ),
        (
            "Devolvendo resultados com return",
            """return encerra a execução da função atual e devolve um resultado a quem a chamou.

Exemplo:
def somar(a, b):
    return a + b

resultado = somar(3, 5)
print(resultado)

A função soma os argumentos e devolve 8. Esse resultado é guardado na variável resultado.

Saída:
8

print() e return têm funções diferentes. print() exibe uma informação. return devolve um valor para que o restante do programa possa utilizá-lo.

Uma função pode exibir algo, devolver um valor ou fazer as duas coisas, conforme a necessidade.""",
            "def somar(a, b):\n    return a + b\n\nresultado = somar(3, 5)\nprint(resultado)",
            "O que return faz nesse exemplo?",
            ["Devolve o resultado da soma", "Exibe sempre o resultado diretamente", "Repete a função infinitamente"],
            "a",
        ),
        (
            "Parâmetros com valores padrão",
            """Um parâmetro pode ter um valor padrão, utilizado quando a chamada não fornece aquele argumento.

Exemplo:
def saudar(nome="amigo"):
    print(f"Olá, {nome}!")

saudar()
saudar("Ana")

Na primeira chamada, o programa usa o valor padrão amigo. Na segunda, usa Ana.

Saída:
Olá, amigo!
Olá, Ana!

Valores padrão tornam funções mais flexíveis. Parâmetros sem valor padrão precisam ser fornecidos de acordo com a assinatura da função, respeitando as regras de chamada.""",
            'def saudar(nome="amigo"):\n    print(f"Olá, {nome}!")\n\nsaudar()',
            "O que acontece quando saudar() é chamada sem argumento?",
            ["Usa o valor padrão amigo", "Sempre causa TypeError", "Não executa o corpo da função"],
            "a",
        ),
        (
            "Escopo de variáveis",
            """O escopo define onde um nome pode ser acessado. Uma variável criada dentro de uma função normalmente é local àquela função.

Exemplo:
def calcular():
    total = 10
    return total

print(calcular())

A variável total é criada dentro de calcular(). A função devolve seu valor, permitindo que print() exiba 10.

Saída:
10

Tentar acessar total diretamente fora da função não funciona nesse exemplo, porque o nome não foi definido no escopo externo.

Usar variáveis locais ajuda a reduzir interferências entre partes diferentes do programa.""",
            "def calcular():\n    total = 10\n    return total\n\nprint(calcular())",
            "Onde total é definido nesse exemplo?",
            ["Dentro da função calcular", "Dentro do módulo math", "No banco de dados"],
            "a",
        ),
        (
            "Separando responsabilidades",
            """Uma função deve ter um objetivo claro. Dividir um programa em funções menores ajuda a testar, reutilizar e compreender cada etapa.

Exemplo:
def calcular_total(preco, quantidade):
    return preco * quantidade

def exibir_total(total):
    print(f"Total: R$ {total:.2f}")

valor = calcular_total(10, 3)
exibir_total(valor)

A primeira função calcula. A segunda apresenta o resultado. Cada função tem uma responsabilidade específica.

Saída:
Total: R$ 30.00

Essa separação facilita mudanças. Se o formato da mensagem precisar ser alterado, podemos modificar a função de exibição sem mudar o cálculo.""",
            "def calcular_total(preco, quantidade):\n    return preco * quantidade\n\nvalor = calcular_total(10, 3)\nprint(valor)",
            "Qual é a responsabilidade de calcular_total()?",
            ["Calcular o produto entre preço e quantidade", "Criar uma janela gráfica", "Salvar automaticamente no banco de dados"],
            "a",
        ),
        (
            "Importando módulos",
            """Um módulo é um arquivo Python que oferece código reutilizável. A instrução import permite acessar funcionalidades definidas em outros módulos.

Exemplo:
import math
print(math.sqrt(81))

O módulo math fornece funções matemáticas. sqrt() calcula a raiz quadrada de um número.

Saída:
9.0

Ao usar math.sqrt(), indicamos que a função pertence ao módulo math. Isso ajuda a identificar de onde vem a funcionalidade.

O Python possui módulos da biblioteca padrão, e também permite instalar pacotes externos quando um projeto precisa de recursos adicionais.""",
            "import math\nprint(math.sqrt(81))",
            "Qual módulo fornece a função sqrt() nesse exemplo?",
            ["json", "math", "random"],
            "b",
        ),
        (
            "Tratando exceções",
            """Exceções são situações que interrompem o fluxo normal de execução quando não são tratadas. try e except permitem responder a erros esperados.

Exemplo:
try:
    numero = int("abc")
except ValueError:
    print("Número inválido")

int("abc") não consegue converter o texto para inteiro e provoca ValueError. O except correspondente captura esse tipo de erro.

Saída:
Número inválido

O tratamento permite apresentar uma mensagem útil ou adotar outra estratégia. Não é uma boa prática capturar todos os erros indiscriminadamente e escondê-los, pois isso pode dificultar a investigação de falhas reais.""",
            'try:\n    numero = int("abc")\nexcept ValueError:\n    print("Número inválido")',
            "Qual exceção é tratada nesse exemplo?",
            ["ValueError", "IndexError", "ImportError"],
            "a",
        ),
           (
    "Documentando funções",
    """Nomes claros e docstrings ajudam outras pessoas a entender o propósito de uma função.

Exemplo:
def calcular_area(largura, altura):
    '''Retorna a área de um retângulo.'''
    return largura * altura

A docstring fica logo após a definição da função e documenta o que ela faz. Também podemos documentar os parâmetros e o tipo de resultado em funções mais complexas.

Uma boa documentação não substitui um código claro, mas explica o objetivo e as regras que não ficam evidentes apenas pela implementação.""",
    'def calcular_area(largura, altura):\n    """Retorna a área de um retângulo."""\n    return largura * altura\n\nprint(calcular_area(5, 4))',
    "Qual é a finalidade de uma docstring?",
    [
        "Documentar a finalidade de uma função ou objeto",
        "Executar a função automaticamente",
        "Converter a função em uma classe",
    ],
    "a",
),
        (
            "Revisão de funções",
            """Funções permitem organizar programas, receber argumentos, devolver resultados e tratar erros. Módulos ajudam a separar o código em arquivos reutilizáveis.

Exemplo:
def calcular_desconto(preco, percentual):
    desconto = preco * percentual / 100
    return preco - desconto

resultado = calcular_desconto(200, 10)
print(resultado)

A função calcula o valor correspondente ao percentual de desconto e devolve o preço final.

Saída:
180.0

Antes de avançar, certifique-se de diferenciar parâmetros, argumentos, valores retornados e variáveis locais. Esses conceitos serão utilizados nas etapas intermediárias do curso.""",
            "def calcular_desconto(preco, percentual):\n    desconto = preco * percentual / 100\n    return preco - desconto\n\nprint(calcular_desconto(200, 10))",
            "Qual é o resultado de calcular_desconto(200, 10)?",
            ["20", "180.0", "190.0"],
            "b",
        ),
    ],

    # NÍVEL 7 — PYTHON INTERMEDIÁRIO
    [
        (
            "List comprehensions",
            """Uma list comprehension cria uma lista a partir de uma expressão e de um iterável. Ela pode substituir alguns laços simples quando isso deixa a intenção mais clara.

Exemplo:
quadrados = [numero ** 2 for numero in range(4)]
print(quadrados)

O for percorre 0, 1, 2 e 3. A expressão numero ** 2 calcula o quadrado de cada valor.

Saída:
[0, 1, 4, 9]

Compreensões também podem incluir uma condição de filtragem. Apesar de compactas, não devem ser usadas quando tornam o código difícil de entender.""",
            "quadrados = [numero ** 2 for numero in range(4)]\nprint(quadrados)",
            "Qual lista será criada?",
            ["[0, 1, 4, 9]", "[1, 4, 9, 16]", "[0, 1, 2, 3]"],
            "a",
        ),
        (
            "Funções lambda",
            """lambda cria uma pequena função anônima por meio de uma expressão. Ela é útil em situações simples, por exemplo, ao definir um critério de ordenação.

Exemplo:
dobrar = lambda numero: numero * 2
print(dobrar(5))

A função recebe numero e devolve o resultado da multiplicação por 2.

Saída:
10

Funções lambda são limitadas a uma única expressão. Para uma lógica extensa, com várias instruções ou documentação importante, uma função definida com def costuma ser mais legível.""",
            "dobrar = lambda numero: numero * 2\nprint(dobrar(5))",
            "Qual é a finalidade de lambda?",
            ["Criar uma função anônima simples", "Declarar obrigatoriamente uma classe", "Abrir um arquivo automaticamente"],
            "a",
        ),
        (
            "Ordenando coleções",
            """sorted() devolve uma nova lista com os elementos ordenados. A lista original não é modificada por essa chamada.

Exemplo:
numeros = [3, 1, 2]
ordenados = sorted(numeros)
print(ordenados)
print(numeros)

Saída:
[1, 2, 3]
[3, 1, 2]

Podemos usar reverse=True para ordenar em ordem decrescente. Para ordenar objetos ou estruturas mais complexas, o argumento key permite definir o critério.

É importante distinguir sorted(), que retorna uma nova lista, de métodos mutáveis como list.sort(), que ordenam a própria lista.""",
            "numeros = [3, 1, 2]\nordenados = sorted(numeros)\nprint(ordenados)",
            "Qual é o resultado de sorted([3, 1, 2])?",
            ["[3, 2, 1]", "[1, 2, 3]", "[3, 1, 2]"],
            "b",
        ),
        (
            "map e filter",
            """map() aplica uma função a cada item de um iterável. filter() seleciona os itens que atendem a uma condição.

Exemplo:
numeros = [1, 2, 3]
dobrados = list(map(lambda n: n * 2, numeros))
print(dobrados)

map() aplica a função a cada número. list() transforma o resultado iterável em uma lista.

Saída:
[2, 4, 6]

Essas ferramentas podem tornar transformações concisas, mas um laço for explícito também é válido e às vezes mais fácil de ler para iniciantes.""",
            "numeros = [1, 2, 3]\ndobrados = list(map(lambda n: n * 2, numeros))\nprint(dobrados)",
            "O que map() faz nesse exemplo?",
            ["Aplica a função a cada item", "Ordena os itens automaticamente", "Remove todos os itens pares"],
            "a",
        ),
        (
            "Trabalhando com arquivos",
            """A função open() permite abrir arquivos. O modo r é usado para leitura, w para escrita e a para acrescentar conteúdo ao final.

Exemplo:
with open("dados.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write("Estudo de Python")

O bloco cria ou substitui o conteúdo do arquivo dados.txt. encoding="utf-8" ajuda a trabalhar corretamente com caracteres acentuados.

O uso de with garante que o arquivo seja fechado ao sair do bloco, inclusive quando ocorre uma exceção.

Atenção: o modo w pode apagar o conteúdo anterior. Escolha o modo de abertura de acordo com a tarefa e evite sobrescrever dados importantes sem querer.""",
            'with open("dados.txt", "w", encoding="utf-8") as arquivo:\n    arquivo.write("Estudo de Python")',
            "Qual modo é usado para ler um arquivo existente?",
            ["w", "r", "a"],
            "b",
        ),
        (
            "Lendo e escrevendo JSON",
            """JSON é um formato de texto usado para representar dados estruturados. Ele é comum em APIs, configurações e troca de informações entre aplicações.

O módulo json permite converter estruturas Python para JSON e fazer a conversão inversa.

Exemplo:
import json

dados = {"nome": "Ana", "ativo": True}
texto = json.dumps(dados)
print(texto)

dumps() converte o dicionário em uma string JSON.

O método loads() faz a conversão inversa a partir de uma string JSON válida. É importante tratar dados externos como entrada não confiável e verificar se possuem a estrutura esperada.""",
            'import json\ndados = {"nome": "Ana", "ativo": True}\ntexto = json.dumps(dados)\nprint(texto)',
            "Qual é a finalidade de json.dumps()?",
            ["Converter dados Python para uma string JSON", "Criar uma classe automaticamente", "Executar uma consulta SQL"],
            "a",
        ),
        (
            "Datas e horários",
            """O módulo datetime oferece ferramentas para representar e manipular datas e horários.

Exemplo:
from datetime import date

hoje = date(2026, 11, 3)
print(hoje.year)

date() cria uma data usando ano, mês e dia. O atributo year permite consultar o ano armazenado.

Saída:
2026

Para sistemas reais, é importante considerar fusos horários quando os horários precisam representar instantes globais. Datas e horários não devem ser tratados como simples strings quando precisamos fazer comparações e cálculos temporais confiáveis.""",
            "from datetime import date\nhoje = date(2026, 11, 3)\nprint(hoje.year)",
            "Qual valor é exibido?",
            ["3", "11", "2026"],
            "c",
        ),
        (
            "Iteradores",
            """Um iterador fornece itens um de cada vez. O for utiliza esse mecanismo internamente para percorrer listas, strings, arquivos e outros iteráveis.

Exemplo:
numeros = iter([10, 20, 30])
print(next(numeros))
print(next(numeros))

iter() obtém um iterador. next() solicita o próximo valor disponível.

Saída:
10
20

Quando não existem mais itens, next() pode lançar StopIteration. O laço for trata esse encerramento automaticamente.

Iteradores são úteis para processar dados gradualmente sem precisar criar uma lista completa de todos os resultados.""",
            "numeros = iter([10, 20, 30])\nprint(next(numeros))\nprint(next(numeros))",
            "O que a segunda chamada de next() retorna?",
            ["10", "20", "30"],
            "b",
        ),
        (
            "Geradores com yield",
            """Um gerador produz valores gradualmente. A palavra-chave yield entrega um valor e suspende temporariamente a execução da função, permitindo que ela continue depois.

Exemplo:
def numeros():
    yield 1
    yield 2

for numero in numeros():
    print(numero)

A chamada numeros() cria um objeto gerador. O for solicita os valores, um por vez.

Saída:
1
2

Geradores podem economizar memória quando precisamos processar grandes sequências. Em vez de armazenar todos os resultados de uma vez, eles os produzem conforme são solicitados.""",
            "def numeros():\n    yield 1\n    yield 2\n\nfor numero in numeros():\n    print(numero)",
            "Qual palavra-chave produz um valor em um gerador?",
            ["class", "yield", "import"],
            "b",
        ),
        (
            "Ambientes virtuais e dependências",
            """Um ambiente virtual isola os pacotes instalados para um projeto Python. Isso ajuda projetos diferentes a usarem versões de bibliotecas sem interferir uns nos outros.

Um ambiente pode ser criado no terminal com:
python -m venv .venv

Depois, ele pode ser ativado conforme o sistema operacional. Pacotes podem ser instalados no ambiente ativo usando pip.

Isolamento de dependências facilita reproduzir o ambiente de desenvolvimento e reduz conflitos entre projetos.

Em um projeto compartilhado, registrar as dependências utilizadas também ajuda outra pessoa a preparar o ambiente para executar o código.""",
            "python -m venv .venv",
            "Qual é a finalidade de um ambiente virtual?",
            ["Isolar dependências de um projeto", "Aumentar fisicamente a memória RAM", "Criar páginas HTML automaticamente"],
            "a",
        ),
    ],

    # NÍVEL 8 — ORIENTAÇÃO A OBJETOS
    [
        (
            "Classes e objetos",
            """Uma classe define uma estrutura que pode ser usada para criar objetos. Um objeto é uma instância dessa classe e pode possuir dados e comportamentos.

Exemplo:
class Pessoa:
    pass

pessoa = Pessoa()
print(type(pessoa).__name__)

class define a classe. A chamada Pessoa() cria uma instância. pass indica que o corpo ainda não possui implementação.

Saída:
Pessoa

Classes são úteis para representar entidades com características e operações relacionadas, como usuários, produtos, contas e pedidos.""",
            "class Pessoa:\n    pass\n\npessoa = Pessoa()\nprint(type(pessoa).__name__)",
            "O que é pessoa nesse exemplo?",
            ["Uma instância da classe Pessoa", "Um módulo importado", "Uma instrução de repetição"],
            "a",
        ),
        (
            "O método __init__",
            """O método __init__ é executado durante a inicialização de uma instância. Ele costuma configurar os atributos iniciais do objeto.

Exemplo:
class Pessoa:
    def __init__(self, nome):
        self.nome = nome

pessoa = Pessoa("Ana")
print(pessoa.nome)

Ao criar Pessoa("Ana"), o argumento Ana é recebido pelo parâmetro nome. A instrução self.nome = nome guarda esse valor no objeto.

Saída:
Ana

__init__ não cria a classe: ele configura a instância durante sua inicialização.""",
            'class Pessoa:\n    def __init__(self, nome):\n        self.nome = nome\n\npessoa = Pessoa("Ana")\nprint(pessoa.nome)',
            "O que self.nome = nome faz?",
            ["Guarda o nome como atributo da instância", "Cria outro módulo Python", "Encerra a classe"],
            "a",
        ),
        (
            "Atributos de instância",
            """Atributos armazenam dados associados a um objeto. Em geral, atributos de instância são definidos por meio de self dentro de métodos.

Exemplo:
class Produto:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco

produto = Produto("Teclado", 80)
print(produto.preco)

Cada objeto pode ter seus próprios valores. Um segundo Produto pode representar outro item com preço diferente.

Saída:
80

Atributos permitem que os objetos mantenham estado, ou seja, informações que descrevem sua situação atual.""",
            'class Produto:\n    def __init__(self, nome, preco):\n        self.nome = nome\n        self.preco = preco\n\nproduto = Produto("Teclado", 80)\nprint(produto.preco)',
            "Qual é o valor de produto.preco?",
            ["'Teclado'", "80", "None"],
            "b",
        ),
        (
            "Métodos de instância",
            """Métodos são funções definidas dentro de uma classe. Um método de instância recebe convencionalmente self como primeiro parâmetro e pode acessar os atributos do objeto.

Exemplo:
class Conta:
    def __init__(self, saldo):
        self.saldo = saldo

    def consultar_saldo(self):
        return self.saldo

conta = Conta(150)
print(conta.consultar_saldo())

O método consulta o atributo saldo da instância.

Saída:
150

Métodos reúnem comportamentos relacionados aos dados que os objetos representam.""",
            "class Conta:\n    def __init__(self, saldo):\n        self.saldo = saldo\n\n    def consultar_saldo(self):\n        return self.saldo\n\nconta = Conta(150)\nprint(conta.consultar_saldo())",
            "O que consultar_saldo() retorna?",
            ["O saldo da instância", "O nome da classe como texto", "O número de métodos do Python"],
            "a",
        ),
        (
            "Encapsulamento e validação",
            """Encapsulamento organiza dados e comportamentos relacionados dentro de uma classe. A classe pode oferecer métodos para controlar como seus dados são alterados.

Exemplo:
class Conta:
    def __init__(self, saldo):
        self.saldo = saldo

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor

conta = Conta(100)
conta.depositar(50)
print(conta.saldo)

O método aceita depósitos positivos e ignora valores que não atendem à condição.

Saída:
150

Este exemplo é didático; um sistema financeiro real exige validações, regras de segurança, persistência e controle de concorrência muito mais completos.""",
            "class Conta:\n    def __init__(self, saldo):\n        self.saldo = saldo\n\n    def depositar(self, valor):\n        if valor > 0:\n            self.saldo += valor\n\nconta = Conta(100)\nconta.depositar(50)\nprint(conta.saldo)",
            "Por que colocar a operação de depósito em um método?",
            ["Para organizar o comportamento e aplicar regras", "Para impedir que a classe tenha atributos", "Para transformar automaticamente o objeto em banco de dados"],
            "a",
        ),
        (
            "Herança",
            """Herança permite criar uma classe especializada a partir de outra. A classe derivada pode reutilizar comportamentos da classe base e adicionar ou modificar funcionalidades.

Exemplo:
class Animal:
    def falar(self):
        return "Som"

class Cachorro(Animal):
    pass

animal = Cachorro()
print(animal.falar())

Cachorro herda o método falar() de Animal, então a instância pode utilizá-lo.

Saída:
Som

Herança é útil quando existe uma relação real entre os conceitos. Nem toda reutilização de código precisa de herança; composição e funções comuns também podem ser escolhas adequadas.""",
            'class Animal:\n    def falar(self):\n        return "Som"\n\nclass Cachorro(Animal):\n    pass\n\nanimal = Cachorro()\nprint(animal.falar())',
            "De qual classe Cachorro herda nesse exemplo?",
            ["Animal", "Cachorro", "str"],
            "a",
        ),
        (
            "Sobrescrita de métodos",
            """Uma classe derivada pode redefinir um método herdado. Isso é chamado de sobrescrita.

Exemplo:
class Animal:
    def falar(self):
        return "Som"

class Cachorro(Animal):
    def falar(self):
        return "Au"

print(Cachorro().falar())

A classe Cachorro fornece sua própria implementação de falar(). Ao chamar esse método na instância, o Python utiliza a implementação mais específica.

Saída:
Au

A sobrescrita permite adaptar o comportamento de classes derivadas sem abandonar a estrutura compartilhada da classe base.""",
            'class Animal:\n    def falar(self):\n        return "Som"\n\nclass Cachorro(Animal):\n    def falar(self):\n        return "Au"\n\nprint(Cachorro().falar())',
            "Qual método é executado para a instância Cachorro?",
            ["A implementação de Animal sempre", "A implementação sobrescrita em Cachorro", "Nenhum método"],
            "b",
        ),
        (
            "Polimorfismo",
            """Polimorfismo permite que objetos de tipos diferentes respondam à mesma operação, cada um de acordo com seu comportamento.

Exemplo:
class Gato:
    def falar(self):
        return "Miau"

class Cachorro:
    def falar(self):
        return "Au"

for animal in [Gato(), Cachorro()]:
    print(animal.falar())

O laço não precisa verificar explicitamente a classe de cada objeto. Basta que os objetos ofereçam o método utilizado.

Saída:
Miau
Au

Essa abordagem torna o código flexível e facilita acrescentar novos tipos que implementem a operação esperada.""",
            'class Gato:\n    def falar(self):\n        return "Miau"\n\nclass Cachorro:\n    def falar(self):\n        return "Au"\n\nfor animal in [Gato(), Cachorro()]:\n    print(animal.falar())',
            "Qual conceito permite usar a mesma operação com objetos de comportamentos diferentes?",
            ["Polimorfismo", "Conversão de strings", "Indentação"],
            "a",
        ),
        (
            "Métodos de classe e métodos estáticos",
            """Métodos de classe usam o decorador @classmethod e recebem convencionalmente cls, que referencia a classe. Métodos estáticos usam @staticmethod e não recebem automaticamente self ou cls.

Exemplo:
class Conversor:
    @staticmethod
    def dobrar(valor):
        return valor * 2

print(Conversor.dobrar(6))

O método não precisa acessar atributos de uma instância ou da classe. Por isso, um método estático pode ser adequado.

Saída:
12

Escolha o tipo de método conforme a responsabilidade. Métodos de instância trabalham com um objeto específico; métodos de classe podem trabalhar com a classe; métodos estáticos agrupam operações relacionadas sem receber automaticamente esses parâmetros.""",
            "class Conversor:\n    @staticmethod\n    def dobrar(valor):\n        return valor * 2\n\nprint(Conversor.dobrar(6))",
            "Qual é o resultado do método dobrar(6)?",
            ["8", "12", "36"],
            "b",
        ),
        (
            "Composição de objetos",
            """Composição acontece quando um objeto contém ou utiliza outro objeto como parte de sua estrutura.

Exemplo:
class Motor:
    def ligar(self):
        return "Motor ligado"

class Carro:
    def __init__(self):
        self.motor = Motor()

carro = Carro()
print(carro.motor.ligar())

Carro possui uma instância de Motor e utiliza seu método. Os dois objetos colaboram para realizar a tarefa.

Saída:
Motor ligado

Composição é útil quando um sistema pode ser construído combinando componentes com responsabilidades diferentes. Ela evita hierarquias de herança desnecessariamente complexas.""",
            'class Motor:\n    def ligar(self):\n        return "Motor ligado"\n\nclass Carro:\n    def __init__(self):\n        self.motor = Motor()\n\ncarro = Carro()\nprint(carro.motor.ligar())',
            "Qual objeto o Carro contém nesse exemplo?",
            ["Uma instância de Motor", "Uma instância de str obrigatoriamente", "Uma conexão SQL automática"],
            "a",
        ),
    ],

    # NÍVEL 9 — PYTHON AVANÇADO
    [
        (
            "Decoradores",
            """Um decorador recebe uma função ou classe e retorna uma versão modificada ou envolvida por outro comportamento. Ele é frequentemente aplicado com a sintaxe @nome.

Exemplo:
def anunciar(funcao):
    def envolvida():
        print("Iniciando")
        funcao()
    return envolvida

@anunciar
def tarefa():
    print("Executando tarefa")

tarefa()

O decorador cria uma função envolvida que exibe uma mensagem e depois chama a função original.

Saída:
Iniciando
Executando tarefa

Decoradores são utilizados para implementar funcionalidades transversais, como registros, medição de tempo e verificações de acesso. Em código real, também é comum preservar metadados com functools.wraps.""",
            'def anunciar(funcao):\n    def envolvida():\n        print("Iniciando")\n        funcao()\n    return envolvida\n\n@anunciar\ndef tarefa():\n    print("Executando tarefa")\n\ntarefa()',
            "O que o decorador faz nesse exemplo?",
            ["Envolve a função e adiciona uma mensagem antes de chamá-la", "Apaga a função original sem substituição", "Converte a função em um arquivo JSON"],
            "a",
        ),
        (
            "Gerenciadores de contexto",
            """A instrução with utiliza um gerenciador de contexto para preparar e finalizar um recurso de forma controlada.

Exemplo:
with open("dados.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write("Olá")

O arquivo é aberto para escrita e o conteúdo é gravado. Ao sair do bloco, o gerenciador fecha o arquivo automaticamente.

Esse mecanismo reduz o risco de deixar recursos abertos, inclusive quando ocorre uma exceção dentro do bloco.

Gerenciadores de contexto também podem controlar conexões, bloqueios e outros recursos. O comportamento exato depende do objeto utilizado com with.""",
            'with open("dados.txt", "w", encoding="utf-8") as arquivo:\n    arquivo.write("Olá")',
            "Qual é uma vantagem de usar with ao trabalhar com arquivos?",
            ["O arquivo é fechado automaticamente ao sair do bloco", "O arquivo nunca pode ser sobrescrito", "O código dispensa qualquer tratamento de erro"],
            "a",
        ),
        (
            "Anotações de tipo",
            """Anotações de tipo documentam os tipos esperados para parâmetros e retornos. Elas ajudam leitores, editores e ferramentas de análise estática.

Exemplo:
def somar(a: int, b: int) -> int:
    return a + b

print(somar(2, 3))

As anotações indicam que a função espera inteiros e declara um retorno do tipo int.

Saída:
5

Python não aplica automaticamente todas essas restrições durante a execução. Se for necessário garantir tipos ou formatos de entrada, o programa deve validar os dados explicitamente ou utilizar ferramentas apropriadas.""",
            "def somar(a: int, b: int) -> int:\n    return a + b\n\nprint(somar(2, 3))",
            "O que -> int documenta nesse exemplo?",
            ["O tipo esperado de retorno", "Uma conversão obrigatória automática", "Uma condição de repetição"],
            "a",
        ),
        (
            "Dataclasses",
            """dataclass é um decorador do módulo dataclasses que reduz código repetitivo em classes usadas principalmente para armazenar dados.

Exemplo:
from dataclasses import dataclass

@dataclass
class Produto:
    nome: str
    preco: float

produto = Produto("Mouse", 50.0)
print(produto.nome)

A declaração dos campos permite que o Python gere métodos comuns, como um inicializador, de acordo com as opções utilizadas.

Saída:
Mouse

Dataclasses são úteis para representar registros simples. Elas não substituem a necessidade de validar dados ou definir comportamentos específicos quando o domínio do problema exige isso.""",
            'from dataclasses import dataclass\n\n@dataclass\nclass Produto:\n    nome: str\n    preco: float\n\nproduto = Produto("Mouse", 50.0)\nprint(produto.nome)',
            "Qual é uma vantagem de dataclass?",
            ["Reduz código repetitivo em classes de dados", "Cria automaticamente um banco de dados remoto", "Impede todos os valores inválidos"],
            "a",
        ),
        (
            "Expressões regulares",
            """Expressões regulares descrevem padrões de texto. O módulo re permite procurar, verificar e substituir trechos que correspondem a esses padrões.

Exemplo:
import re

resultado = re.search(r"\d+", "pedido 123")
print(resultado.group())

\d representa um dígito e + significa uma ou mais ocorrências. A busca encontra a sequência 123.

Saída:
123

Expressões regulares podem ajudar a identificar padrões, mas não substituem validações completas de formatos complexos. Para dados importantes, considere também regras específicas do domínio e tratamento de entradas inválidas.""",
            'import re\nresultado = re.search(r"\\d+", "pedido 123")\nprint(resultado.group())',
            "O que o padrão r'\\d+' procura?",
            ["Uma ou mais ocorrências de dígitos", "Somente letras maiúsculas", "Um arquivo com extensão .py"],
            "a",
        ),
        (
            "Programação assíncrona",
            """Programação assíncrona ajuda a organizar tarefas que passam tempo aguardando operações, como chamadas de rede ou leitura de recursos.

O módulo asyncio oferece ferramentas para trabalhar com corrotinas e operações assíncronas.

Exemplo:
import asyncio

async def tarefa():
    print("Executando")

asyncio.run(tarefa())

async def define uma corrotina. asyncio.run() inicia a execução assíncrona de uma corrotina principal.

Saída:
Executando

Assincronismo não torna automaticamente todo cálculo mais rápido. Ele é especialmente útil quando várias tarefas precisam aguardar operações de entrada e saída sem bloquear desnecessariamente o fluxo de trabalho.""",
            'import asyncio\n\nasync def tarefa():\n    print("Executando")\n\nasyncio.run(tarefa())',
            "Qual palavra-chave define uma corrotina?",
            ["async", "class", "global"],
            "a",
        ),
        (
            "Logging e diagnóstico",
            """O módulo logging registra mensagens que ajudam a acompanhar o comportamento de uma aplicação.

Os níveis comuns incluem DEBUG, INFO, WARNING, ERROR e CRITICAL. Eles indicam a importância ou gravidade da mensagem.

Exemplo:
import logging

logging.basicConfig(level=logging.WARNING)
logging.warning("Atenção")
logging.info("Informação")

Com o nível WARNING, a mensagem de aviso é exibida, enquanto a mensagem INFO fica abaixo do limite configurado.

Registros são úteis para investigar problemas em aplicações que continuam funcionando por longos períodos. Evite incluir senhas, tokens ou dados sensíveis nos logs.""",
            'import logging\nlogging.basicConfig(level=logging.WARNING)\nlogging.warning("Atenção")\nlogging.info("Informação")',
            "Qual nível normalmente representa uma condição que merece atenção?",
            ["WARNING", "DEBUG", "INFO sempre acima de WARNING"],
            "a",
        ),
        (
            "Testes automatizados",
            """Testes automatizados verificam se partes do programa produzem os resultados esperados. O comando assert verifica uma condição e gera AssertionError quando ela é falsa.

Exemplo:
def dobrar(numero):
    return numero * 2

assert dobrar(3) == 6
print("Teste concluído")

A expressão compara o resultado de dobrar(3) com 6. Como a condição é verdadeira, o programa continua.

Saída:
Teste concluído

Projetos maiores podem usar frameworks como unittest ou pytest para organizar testes, preparar dados e apresentar relatórios. Testes ajudam a detectar regressões quando o código é alterado.""",
            "def dobrar(numero):\n    return numero * 2\n\nassert dobrar(3) == 6\nprint('Teste concluído')",
            "O que acontece se a condição de assert for falsa?",
            ["Uma AssertionError é levantada", "O programa corrige automaticamente a função", "A condição é ignorada em qualquer situação"],
            "a",
        ),
        (
            "Segurança de dados",
            """Aplicações devem tratar dados sensíveis com cuidado. Senhas, tokens e chaves secretas não devem ser gravados em texto puro nos registros nem enviados desnecessariamente a terceiros.

Para armazenar senhas, sistemas devem usar algoritmos próprios para hashing de senhas, com salt e parâmetros de custo adequados, como Argon2id, scrypt ou PBKDF2.

Exemplo didático:
import secrets
salt = secrets.token_bytes(16)

secrets gera valores adequados para usos relacionados à segurança. Um salt é um valor aleatório usado no processo de armazenamento de senhas.

A geração de um salt, sozinha, não protege uma senha. É necessário utilizar uma função de derivação de senha adequada e verificar as senhas com um procedimento seguro.""",
            "import secrets\nsalt = secrets.token_bytes(16)\nprint(len(salt))",
            "Qual prática é adequada para armazenar senhas?",
            ["Armazenar o texto original", "Usar hashing de senha com salt e custo apropriado", "Escrever a senha nos logs"],
            "b",
        ),
        (
            "Desempenho e otimização",
            """Otimizar significa melhorar aspectos como tempo de execução ou consumo de memória. Antes de modificar o código, é importante medir seu desempenho.

O módulo time pode medir intervalos simples. Para análises mais detalhadas, Python também oferece ferramentas como timeit e cProfile.

Exemplo:
import time

inicio = time.perf_counter()
resultado = sum(range(1000))
fim = time.perf_counter()

print(resultado)
print(fim >= inicio)

perf_counter() fornece um contador adequado para medir intervalos. O exemplo não é um benchmark completo, mas demonstra a estrutura de uma medição.

Uma otimização deve ser guiada por evidências e acompanhada de testes para confirmar que o comportamento continua correto.""",
            "import time\ninicio = time.perf_counter()\nresultado = sum(range(1000))\nfim = time.perf_counter()\nprint(fim >= inicio)",
            "Qual é uma boa primeira etapa para otimizar um programa?",
            ["Medir e identificar o gargalo", "Reescrever tudo sem testar", "Remover todas as validações"],
            "a",
        ),
    ],

    # NÍVEL 10 — DOMÍNIO PRÁTICO
    [
        (
            "Planejando um projeto",
            """Um projeto começa com um problema claro e requisitos verificáveis. Antes de implementar, defina quem utilizará o sistema, quais informações serão necessárias e qual resultado deve ser entregue.

Um gerenciador de tarefas, por exemplo, pode precisar cadastrar tarefas, listar as pendentes e marcar tarefas como concluídas.

É possível separar o projeto em componentes:
- Entrada e validação de dados.
- Regras de negócio.
- Armazenamento.
- Apresentação dos resultados.
- Testes.

Essa separação facilita o desenvolvimento e permite testar cada parte de forma independente.

Comece com uma versão pequena que resolva o problema principal. Depois, acrescente funcionalidades conforme necessário.""",
            'tarefas = ["Estudar Python", "Praticar exercícios"]\nfor tarefa in tarefas:\n    print(tarefa)',
            "Por que definir os requisitos antes de programar?",
            ["Para entender o problema e orientar a implementação", "Para dispensar os testes", "Para impedir alterações futuras"],
            "a",
        ),
        (
            "Validando entradas",
            """Dados recebidos de usuários podem estar vazios, ter formatos inesperados ou não atender às regras do sistema. Validar significa verificar se esses dados são aceitáveis antes de utilizá-los.

Exemplo:
def validar_nome(nome):
    return bool(nome.strip())

print(validar_nome(" Ana "))
print(validar_nome("   "))

strip() remove espaços das extremidades. bool() transforma o resultado em um valor lógico.

Saída:
True
False

Essa validação é apenas um exemplo simples. Regras reais dependem do contexto: um email, uma senha e um preço exigem verificações diferentes.

Validar entradas ajuda a prevenir erros de lógica e melhora a experiência do usuário.""",
            'def validar_nome(nome):\n    return bool(nome.strip())\n\nprint(validar_nome(" Ana "))\nprint(validar_nome("   "))',
            "O que validar_nome() retorna para uma string composta somente por espaços?",
            ["True", "False", "A própria função"],
            "b",
        ),
        (
            "Persistência de dados",
            """Persistência significa guardar dados de modo que possam ser recuperados depois que o programa termina.

Um arquivo JSON pode ser suficiente para um exemplo pequeno. Sistemas com vários usuários, consultas complexas ou atualizações concorrentes normalmente precisam de um banco de dados.

Exemplo:
import json

dados = {"tema": "Python", "concluido": True}
with open("progresso.json", "w", encoding="utf-8") as arquivo:
    json.dump(dados, arquivo)

json.dump() escreve os dados no arquivo. O uso de with ajuda a garantir o fechamento do recurso.

A escolha entre arquivos e banco de dados depende da quantidade de dados, da concorrência, das consultas necessárias e dos requisitos de confiabilidade.""",
            'import json\ndados = {"tema": "Python", "concluido": True}\nwith open("progresso.json", "w", encoding="utf-8") as arquivo:\n    json.dump(dados, arquivo)',
            "O que significa persistência de dados?",
            ["Manter os dados armazenados para uso posterior", "Exibir dados sem guardá-los", "Apagar informações ao fechar o programa"],
            "a",
        ),
        (
            "Banco de dados e SQL",
            """Bancos de dados armazenam informações de forma organizada. Em bancos relacionais, tabelas contêm registros e colunas descrevem os campos.

SQL é uma linguagem usada para consultar e manipular dados em muitos bancos relacionais.

Exemplo de consulta:
SELECT nome FROM usuarios;

Essa consulta solicita a coluna nome da tabela usuarios.

Em uma aplicação real, a consulta deve ser executada por meio da conexão apropriada, usando parâmetros para os valores externos. Concatenar dados de usuários diretamente em SQL pode criar vulnerabilidades de injeção de SQL.

Compreender o banco de dados é importante para criar sistemas que persistam informações de forma confiável.""",
            'consulta = "SELECT nome FROM usuarios;"\nprint(consulta)',
            "Qual linguagem é usada nessa consulta?",
            ["SQL", "CSS", "Markdown"],
            "a",
        ),
        (
            "APIs e comunicação entre sistemas",
            """Uma API define uma interface pela qual sistemas podem trocar informações. Uma aplicação pode solicitar dados a um serviço e receber uma resposta estruturada.

Por exemplo, um frontend pode enviar uma requisição para consultar o progresso de um aluno. O backend verifica a solicitação, consulta os dados e devolve uma resposta.

JSON é um formato comum para transportar esses dados.

Exemplo de objeto Python:
aluno = {"nome": "Ana", "progresso": 50}

O objeto representa dados que poderiam ser serializados para JSON e enviados por uma API.

Uma API precisa definir rotas, formatos, regras de validação e mecanismos de autenticação quando os dados não são públicos.""",
            'aluno = {"nome": "Ana", "progresso": 50}\nprint(aluno["progresso"])',
            "Qual é uma finalidade comum de uma API?",
            ["Permitir a comunicação entre sistemas", "Substituir a memória física do computador", "Impedir toda troca de dados"],
            "a",
        ),
        (
            "HTTP e métodos de requisição",
            """HTTP é um protocolo usado na comunicação entre clientes e servidores web.

GET costuma ser usado para consultar um recurso.
POST costuma enviar dados para criar ou processar algo.
PUT costuma substituir ou atualizar um recurso.
DELETE costuma solicitar a remoção de um recurso.

Esses significados dependem do contrato da API. O método, sozinho, não garante que uma operação seja segura ou autorizada.

Por exemplo, um frontend pode enviar GET para consultar o progresso e POST para registrar uma resposta de exercício.

A API deve validar os dados recebidos, verificar as permissões e devolver códigos de estado apropriados.""",
            'metodo = "GET"\nprint(metodo)',
            "Qual é o uso típico do método GET?",
            ["Consultar um recurso", "Apagar sempre todo o banco", "Desligar o servidor"],
            "a",
        ),
        (
            "Tratamento de falhas",
            """Falhas podem ocorrer por entradas inválidas, arquivos ausentes, conexões interrompidas ou erros inesperados.

try e except permitem tratar exceções conhecidas e definir uma resposta apropriada.

Exemplo:
try:
    numero = int("abc")
except ValueError:
    numero = None

print(numero)

A conversão provoca ValueError. O except captura esse erro e atribui None à variável.

Saída:
None

Em uma aplicação real, talvez seja melhor pedir uma nova entrada ou devolver uma mensagem de validação. Evite ocultar todos os erros sem registrar informações úteis para o diagnóstico.""",
            'try:\n    numero = int("abc")\nexcept ValueError:\n    numero = None\n\nprint(numero)',
            "Qual exceção é provocada pela conversão de 'abc' para inteiro?",
            ["ValueError", "KeyError", "ImportError"],
            "a",
        ),
        (
            "Controle de versão com Git",
            """Git é um sistema de controle de versão. Ele registra alterações no código e permite comparar versões, recuperar mudanças e colaborar com outras pessoas.

Comandos comuns:
git status
git add .
git commit -m "Descreve a alteração"

git status mostra o estado dos arquivos. git add seleciona alterações para o próximo commit. git commit cria um registro dessas alterações no histórico local.

Um commit deve representar uma mudança compreensível e ter uma mensagem que explique seu propósito.

O Git não substitui backups, testes ou revisão de código, mas ajuda a acompanhar a evolução do projeto.""",
            'comando = "git status"\nprint(comando)',
            "O que git status mostra?",
            ["O estado das alterações do repositório", "A senha do usuário", "A temperatura do processador"],
            "a",
        ),
        (
            "Documentação e manutenção",
            """Documentação explica como instalar, configurar, executar e utilizar um projeto. Ela também pode registrar decisões importantes e limitações conhecidas.

Um README útil geralmente contém:
- Descrição do projeto.
- Requisitos necessários.
- Instruções de instalação.
- Como configurar variáveis de ambiente.
- Como executar e testar.
- Problemas conhecidos ou formas de contribuição.

A documentação deve corresponder ao código atual. Instruções antigas podem causar erros mesmo quando o programa está correto.

Manutenção também inclui corrigir defeitos, atualizar dependências e revisar aspectos de segurança.""",
            'projeto = "StudyCore"\nobjetivo = "Organizar os estudos"\nprint(projeto, "-", objetivo)',
            "Qual é a finalidade principal de um README?",
            ["Explicar o projeto e orientar sua utilização", "Substituir todo o código-fonte", "Armazenar senhas em texto puro"],
            "a",
        ),
        (
            "Projeto integrador final",
            """Nesta última aula, reúna os conceitos estudados para analisar um pequeno programa que calcula e apresenta o total de uma compra.

Exemplo:
def calcular_total(preco, quantidade):
    if preco < 0 or quantidade < 0:
        raise ValueError("Valores inválidos")
    return preco * quantidade

total = calcular_total(12.5, 4)
print(f"Total: R$ {total:.2f}")

A função recebe dois argumentos, valida se os valores são negativos, calcula o produto e devolve o resultado. O programa apresenta o total com duas casas decimais.

Saída:
Total: R$ 50.00

Um projeto real ainda precisaria validar os tipos de entrada, tratar exceções, persistir dados quando necessário e incluir testes.

O objetivo do curso é que você consiga ler o código, explicar o comportamento, identificar erros e desenvolver soluções próprias com segurança.""",
            'def calcular_total(preco, quantidade):\n    if preco < 0 or quantidade < 0:\n        raise ValueError("Valores inválidos")\n    return preco * quantidade\n\ntotal = calcular_total(12.5, 4)\nprint(f"Total: R$ {total:.2f}")',
            "Qual é a saída do exemplo com preço 12.5 e quantidade 4?",
            ["Total: R$ 16.50", "Total: R$ 50.00", "Total: R$ 125.04"],
            "b",
        ),
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
        raise HTTPException(
            422,
            "A matéria deve ter entre 1 e 100 caracteres."
        )
    return materia


def buscar_usuario(usuario_id):
    with conectar_banco() as conexao:
        usuario = conexao.execute(
            "SELECT id FROM usuarios WHERE id = %s",
            (usuario_id,),
        ).fetchone()

    if usuario is None:
        raise HTTPException(404, "Usuário não encontrado.")


def obter_estado(usuario_id, materia):
    buscar_usuario(usuario_id)

    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO progresso_aulas (usuario_id, materia)
            VALUES (%s, %s)
            ON CONFLICT (usuario_id, materia) DO NOTHING
            """,
            (usuario_id, materia),
        )

        estado = conexao.execute(
            """
            SELECT * FROM progresso_aulas
            WHERE usuario_id = %s AND materia = %s
            """,
            (usuario_id, materia),
        ).fetchone()

    return dict(estado)


def progresso_percentual(usuario_id, materia):
    with conectar_banco() as conexao:
        registros = conexao.execute(
            """
            SELECT paginas_concluidas FROM progresso_aulas
            WHERE usuario_id = %s AND materia = %s
            """,
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
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT(usuario_id, materia) DO UPDATE SET
                horas_estudadas = excluded.horas_estudadas,
                progresso = excluded.progresso,
                nivel = excluded.nivel
            """,
            (
                usuario_id,
                materia,
                horas,
                percentual,
                estado["nivel"],
            ),
        )


def exigir_nivel_disponivel(usuario_id, materia, nivel):
    estado = obter_estado(usuario_id, materia)

    if nivel > estado["nivel"]:
        raise HTTPException(403, "Esse nível ainda está bloqueado.")

    if materia.lower() != "python":
        raise HTTPException(
            404,
            "O conteúdo desta matéria ainda não foi criado."
        )


def obter_aula(nivel, pagina):
    if not 1 <= nivel <= 10 or not 1 <= pagina <= 10:
        raise HTTPException(404, "Aula não encontrada.")

    (
        titulo,
        conteudo,
        codigo,
        pergunta,
        opcoes,
        resposta,
    ) = CONTEUDO[nivel - 1][pagina - 1]

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
        raise HTTPException(
            403,
            "Conclua as 10 páginas deste nível primeiro."
        )


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
    return {
        "mensagem": "SGE está funcionando!",
        "versao": "2.0.0",
    }


@app.post("/usuarios/cadastro", status_code=201)
def cadastrar_usuario(dados: CadastroUsuario):
    nome = dados.nome.strip()
    email = dados.email.strip().lower()

    if (
        len(nome) < 2
        or "@" not in email
        or "." not in email.split("@")[-1]
    ):
        raise HTTPException(400, "Informe um nome e um e-mail válidos.")

    try:
        with conectar_banco() as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (nome, email, gerar_hash_senha(dados.senha)),
            )
            usuario_id = cursor.fetchone()["id"]

    except UniqueViolation:
        raise HTTPException(409, "Este e-mail já está cadastrado.")

    return {
        "mensagem": "Conta criada com sucesso!",
        "usuario": {
            "id": usuario_id,
            "nome": nome,
            "email": email,
        },
    }


@app.post("/usuarios/login")
def login(dados: LoginUsuario):
    with conectar_banco() as conexao:
        usuario = conexao.execute(
            """
            SELECT id, nome, email, senha_hash
            FROM usuarios
            WHERE email = %s
            """,
            (dados.email.strip().lower(),),
        ).fetchone()

    if usuario is None or not verificar_senha(
        dados.senha,
        usuario["senha_hash"],
    ):
        raise HTTPException(401, "E-mail ou senha incorretos.")

    return {
        "mensagem": "Login realizado com sucesso!",
        "access_token": criar_token(usuario["id"]),
        "token_type": "bearer",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
        },
    }


# Lista o progresso de todas as matérias do usuário.
@app.get(
    "/usuarios/{usuario_id}/progresso",
    dependencies=[Depends(verificar_token)],
)
def listar_progressos(usuario_id: int):
    buscar_usuario(usuario_id)

    with conectar_banco() as conexao:
        registros = conexao.execute(
            """
            SELECT materia, horas_estudadas, progresso, nivel
            FROM progresso_estudos
            WHERE usuario_id = %s
            ORDER BY materia
            """,
            (usuario_id,),
        ).fetchall()

    return {"progressos": [dict(r) for r in registros]}


# Consulta o progresso de uma matéria específica.
@app.get(
    "/usuarios/{usuario_id}/materias/{materia}/progresso",
    dependencies=[Depends(verificar_token)],
)
def obter_progresso(usuario_id: int, materia: str):
    materia = validar_materia(materia)
    atualizar_resumo(usuario_id, materia)

    with conectar_banco() as conexao:
        registro = conexao.execute(
            """
            SELECT materia, horas_estudadas, progresso, nivel
            FROM progresso_estudos
            WHERE usuario_id = %s AND materia = %s
            """,
            (usuario_id, materia),
        ).fetchone()

    estado = obter_estado(usuario_id, materia)

    if registro is None:
        raise HTTPException(404, "Progresso não encontrado.")

    return {
        **dict(registro),
        "segundos_estudados": estado["segundos_estudados"],
        "pagina": estado["pagina"],
    }


# Consulta o estado completo do curso.
@app.get(
    "/usuarios/{usuario_id}/materias/{materia}/curso",
    dependencies=[Depends(verificar_token)],
)
def obter_curso(usuario_id: int, materia: str):
    materia = validar_materia(materia)
    estado = obter_estado(usuario_id, materia)

    with conectar_banco() as conexao:
        niveis = conexao.execute(
            """
            SELECT nivel, resumo_concluido, aprovado
            FROM niveis_curso
            WHERE usuario_id = %s AND materia = %s
            ORDER BY nivel
            """,
            (usuario_id, materia),
        ).fetchall()

        respostas = conexao.execute(
            """
            SELECT nivel, questao_id, resposta, acertou
            FROM respostas_quiz
            WHERE usuario_id = %s AND materia = %s
            ORDER BY nivel, questao_id
            """,
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


# Carrega uma aula específica.
@app.get(
    "/usuarios/{usuario_id}/materias/{materia}/curso/aula",
    dependencies=[Depends(verificar_token)],
)
def carregar_aula(
    usuario_id: int,
    materia: str,
    nivel: int = 1,
    pagina: int = 1,
):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, nivel)
    return obter_aula(nivel, pagina)


# Salva a posição atual do aluno.
@app.put(
    "/usuarios/{usuario_id}/materias/{materia}/curso/pagina",
    dependencies=[Depends(verificar_token)],
)
def salvar_pagina(
    usuario_id: int,
    materia: str,
    dados: SalvarPagina,
):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, dados.nivel)

    estado = obter_estado(usuario_id, materia)
    paginas = set(json.loads(estado["paginas_concluidas"]))

    if dados.concluir and f"{dados.nivel}:{dados.pagina}" not in paginas:
        raise HTTPException(
            403,
            "Responda corretamente ao exercício desta página antes de concluí-la.",
        )

    with conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE progresso_aulas
            SET nivel = %s, pagina = %s, atualizado_em = CURRENT_TIMESTAMP
            WHERE usuario_id = %s AND materia = %s
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



# Registra e corrige a resposta de um exercício de aula.
@app.post(
    "/usuarios/{usuario_id}/materias/{materia}/curso/aula/responder",
    dependencies=[Depends(verificar_token)],
)
def responder_aula(
    usuario_id: int,
    materia: str,
    dados: RespostaAula,
):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, dados.nivel)

    # Verifica a alternativa antes de concluir a página.
    correta = resposta_correta(dados.nivel, dados.pagina)
    acertou = dados.resposta.strip().lower() == correta

    estado = obter_estado(usuario_id, materia)
    paginas = set(json.loads(estado["paginas_concluidas"]))
    chave = f"{dados.nivel}:{dados.pagina}"

    # Se errar, não conclui a página nem altera o progresso.
    if not acertou:
        return {
            "acertou": False,
            "mensagem": "Resposta incorreta. Tente novamente!",
            "paginas_concluidas": sorted(paginas),
            "progresso": progresso_percentual(usuario_id, materia),
        }

    # Só registra a conclusão quando a resposta estiver correta.
    paginas.add(chave)

    with conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE progresso_aulas
            SET paginas_concluidas = %s,
                nivel = %s,
                pagina = %s,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE usuario_id = %s AND materia = %s
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

    return {
        "acertou": True,
        "mensagem": "Resposta correta! Página concluída.",
        "paginas_concluidas": sorted(paginas),
        "progresso": progresso_percentual(usuario_id, materia),
    }



# Registra o tempo estudado.
@app.post(
    "/usuarios/{usuario_id}/materias/{materia}/curso/tempo",
    dependencies=[Depends(verificar_token)],
)
def registrar_tempo(
    usuario_id: int,
    materia: str,
    dados: RegistrarTempo,
):
    materia = validar_materia(materia)
    obter_estado(usuario_id, materia)

    with conectar_banco() as conexao:
        conexao.execute(
            """
            UPDATE progresso_aulas
            SET segundos_estudados = segundos_estudados + %s,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE usuario_id = %s AND materia = %s
            """,
            (dados.segundos, usuario_id, materia),
        )

    atualizar_resumo(usuario_id, materia)

    with conectar_banco() as conexao:
        segundos = conexao.execute(
            """
            SELECT segundos_estudados
            FROM progresso_aulas
            WHERE usuario_id = %s AND materia = %s
            """,
            (usuario_id, materia),
        ).fetchone()["segundos_estudados"]

    return {
        "segundos_estudados": segundos,
        "horas_estudadas": round(segundos / 3600, 2),
    }


# Registra a conclusão do resumo de um nível.
@app.post(
    "/usuarios/{usuario_id}/materias/{materia}/curso/resumo",
    dependencies=[Depends(verificar_token)],
)
def concluir_resumo(
    usuario_id: int,
    materia: str,
    dados: NivelRequest,
):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, dados.nivel)
    exigir_paginas_concluidas(usuario_id, materia, dados.nivel)

    with conectar_banco() as conexao:
        conexao.execute(
            """
            INSERT INTO niveis_curso
                (usuario_id, materia, nivel, resumo_concluido)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT(usuario_id, materia, nivel)
            DO UPDATE SET
                resumo_concluido = 1,
                atualizado_em = CURRENT_TIMESTAMP
            """,
            (usuario_id, materia, dados.nivel),
        )

    return {
        "mensagem": "Resumo concluído. Você já pode iniciar o quiz.",
        "nivel": dados.nivel,
    }


# Carrega as questões do quiz.
@app.get(
    "/usuarios/{usuario_id}/materias/{materia}/curso/quiz",
    dependencies=[Depends(verificar_token)],
)
def obter_quiz(
    usuario_id: int,
    materia: str,
    nivel: int = 1,
):
    materia = validar_materia(materia)
    exigir_nivel_disponivel(usuario_id, materia, nivel)
    exigir_paginas_concluidas(usuario_id, materia, nivel)

    with conectar_banco() as conexao:
        resumo = conexao.execute(
            """
            SELECT resumo_concluido
            FROM niveis_curso
            WHERE usuario_id = %s AND materia = %s AND nivel = %s
            """,
            (usuario_id, materia, nivel),
        ).fetchone()

        respostas = conexao.execute(
            """
            SELECT questao_id, resposta, acertou
            FROM respostas_quiz
            WHERE usuario_id = %s AND materia = %s AND nivel = %s
            """,
            (usuario_id, materia, nivel),
        ).fetchall()

    if resumo is None or not resumo["resumo_concluido"]:
        raise HTTPException(403, "Conclua o resumo antes do quiz.")

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


# Registra e corrige uma resposta do quiz.
@app.post(
    "/usuarios/{usuario_id}/materias/{materia}/curso/quiz/responder",
    dependencies=[Depends(verificar_token)],
)
def responder_quiz(
    usuario_id: int,
    materia: str,
    dados: RespostaQuiz,
):
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
            """
            SELECT resumo_concluido
            FROM niveis_curso
            WHERE usuario_id = %s AND materia = %s AND nivel = %s
            """,
            (usuario_id, materia, dados.nivel),
        ).fetchone()

    if resumo is None or not resumo["resumo_concluido"]:
        raise HTTPException(403, "Conclua o resumo antes do quiz.")

    correta = resposta_correta(dados.nivel, pagina)
    acertou_agora = dados.resposta.strip().lower() == correta

    with conectar_banco() as conexao:
        anterior = conexao.execute(
            """
            SELECT acertou
            FROM respostas_quiz
            WHERE usuario_id = %s AND materia = %s AND nivel = %s AND questao_id = %s
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
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT(usuario_id, materia, nivel, questao_id)
            DO UPDATE SET
                resposta = excluded.resposta,
                acertou = GREATEST(respostas_quiz.acertou, excluded.acertou),
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
            SELECT
                COUNT(*) AS respondidas,
                COALESCE(SUM(acertou), 0) AS acertos
            FROM respostas_quiz
            WHERE usuario_id = %s AND materia = %s AND nivel = %s
            """,
            (usuario_id, materia, dados.nivel),
        ).fetchone()

        aprovado = total["acertos"] >= 8

        if aprovado:
            conexao.execute(
                """
                INSERT INTO niveis_curso
                    (usuario_id, materia, nivel, resumo_concluido, aprovado)
                VALUES (%s, %s, %s, 1, 1)
                ON CONFLICT(usuario_id, materia, nivel)
                DO UPDATE SET
                    aprovado = 1,
                    atualizado_em = CURRENT_TIMESTAMP
                """,
                (usuario_id, materia, dados.nivel),
            )

            proximo = min(10, dados.nivel + 1)

            conexao.execute(
                """
                UPDATE progresso_aulas
                SET nivel = %s, pagina = 1,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE usuario_id = %s AND materia = %s
                """,
                (proximo, usuario_id, materia),
            )

    atualizar_resumo(usuario_id, materia)

    with conectar_banco() as conexao:
        erradas = conexao.execute(
            """
            SELECT questao_id
            FROM respostas_quiz
            WHERE usuario_id = %s AND materia = %s AND nivel = %s AND acertou = 0
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

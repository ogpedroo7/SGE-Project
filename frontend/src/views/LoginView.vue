<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const email = ref('')
const senha = ref('')

async function entrar() {
  if (!email.value || !senha.value) {
    alert('Preencha seu e-mail e sua senha.')
    return
  }

  try {
    const resposta = await fetch('http://127.0.0.1:8000/usuarios/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email.value,
        senha: senha.value
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok) {
      throw new Error(dados.detail || 'Não foi possível entrar.')
    }

    localStorage.setItem('usuario', JSON.stringify(dados.usuario))

    router.push('/dashboard')
  } catch (erro) {
    alert(erro.message || 'Não foi possível conectar ao servidor.')
  }
}

</script>

<template>
  <main class="pagina-login">
    <div class="grade-fundo"></div>
    <div class="luz"></div>

    <header class="topo">
      <button class="marca" @click="router.push('/')">
        <span class="simbolo">✦</span>
        SG<span>E</span>
      </button>

      <button class="voltar" @click="router.push('/')">
        ← Página inicial
      </button>
    </header>

    <section class="conteudo">
      <div class="painel-info">
        <div class="etiqueta">
          <span class="ponto"></span>
          ACESSO AO SISTEMA
        </div>

        <h1>
          Seu próximo<br />
          nível começa <span>aqui.</span>
        </h1>

        <p>
          Entre na sua conta e continue construindo
          sua evolução, uma aula de cada vez.
        </p>

        <div class="mini-painel">
          <div class="mini-icone">⌘</div>
          <div>
            <strong>AMBIENTE DE APRENDIZADO</strong>
            <small>Seu progresso. Seu ritmo. Seu futuro.</small>
          </div>
          <span class="sinal">↗</span>
        </div>
      </div>

      <div class="cartao-login">
        <div class="cartao-topo">
          <div class="icone-login">⌑</div>
          <span class="tag">LOGIN / 001</span>
        </div>

        <h2>Bem-vindo de volta</h2>
        <p class="subtitulo">Insira seus dados para continuar.</p>

        <form @submit.prevent="entrar">
          <label for="email">E-MAIL</label>
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="voce@exemplo.com"
            autocomplete="email"
            required
          />

          <label for="senha">SENHA</label>
          <input
            id="senha"
            v-model="senha"
            type="password"
            placeholder="Digite sua senha"
            autocomplete="current-password"
            required
          />

          <button class="botao-entrar" type="submit">
            Entrar no sistema <span>→</span>
          </button>
        </form>

        <div class="divisor">
          <span></span>
          <small>ACESSO SEGURO</small>
          <span></span>
        </div>

        <p class="cadastro">
          Ainda não tem uma conta?
          <button @click="router.push('/cadastro')">
            Cadastre-se
          </button>
        </p>

        <div class="rodape-cartao">
          <span class="ponto"></span>
          INTERFACE DE ESTUDOS
          <span class="codigo">SC-01</span>
        </div>
      </div>
    </section>

    <footer class="rodape">
      <span>SGE © 2026</span>
      <span>LEARN // EVOLVE // REPEAT</span>
    </footer>
  </main>
</template>

<style>
.pagina-login {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 28px 7%;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(ellipse at 20% 50%, #0a285055, transparent 55%),
    #050816;
  color: #edf7ff;
  font-family: 'Rajdhani', sans-serif;
}

.grade-fundo {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.12;
  background-image:
    linear-gradient(#244a7a 1px, transparent 1px),
    linear-gradient(90deg, #244a7a 1px, transparent 1px);
  background-size: 45px 45px;
}

.pagina-login .luz {
  position: absolute;
  top: 20%;
  left: 15%;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: #0066ff;
  filter: blur(130px);
  opacity: 0.15;
  pointer-events: none;
}

.topo,
.conteudo,
.rodape {
  position: relative;
  z-index: 1;
}

.topo {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.marca,
.voltar {
  background: none;
  border: none;
  cursor: pointer;
  font-family: 'Orbitron', sans-serif;
}

.marca {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #edf7ff;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 1px;
}

.marca span:last-child {
  color: #00e5ff;
}

.simbolo {
  color: #00e5ff;
  font-size: 27px;
  text-shadow: 0 0 15px #00e5ff;
}

.voltar {
  color: #8ca3c4;
  font-family: 'Rajdhani', sans-serif;
  font-size: 16px;
}

.voltar:hover {
  color: #00e5ff;
}

.conteudo {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr minmax(320px, 430px);
  align-items: center;
  gap: 9%;
  padding: 65px 0;
}

.painel-info {
  max-width: 510px;
}

.etiqueta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border: 1px solid #00e5ff44;
  color: #00e5ff;
  background: #00e5ff0a;
  font-size: 12px;
  letter-spacing: 2px;
}

.ponto {
  display: inline-block;
  width: 7px;
  height: 7px;
  flex-shrink: 0;
  border-radius: 50%;
  background: #00e5ff;
  box-shadow: 0 0 10px #00e5ff;
}

.painel-info h1 {
  margin: 27px 0 20px;
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(32px, 4vw, 56px);
  line-height: 1.3;
  letter-spacing: -2px;
}

.painel-info h1 span {
  color: #00e5ff;
  text-shadow: 0 0 25px #00e5ff44;
}

.painel-info > p {
  max-width: 420px;
  color: #9bacc8;
  font-size: 20px;
  line-height: 1.6;
}

.mini-painel {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 38px;
  padding: 17px;
  border: 1px solid #203958;
  background: #0b1426bb;
}

.mini-icone {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border: 1px solid #00e5ff55;
  color: #00e5ff;
  font-size: 24px;
}

.mini-painel strong,
.mini-painel small {
  display: block;
}

.mini-painel strong {
  font-size: 13px;
  letter-spacing: 1px;
}

.mini-painel small {
  margin-top: 5px;
  color: #8095b5;
  font-size: 14px;
}

.sinal {
  margin-left: auto;
  color: #00e5ff;
  font-size: 24px;
}

.cartao-login {
  padding: 32px;
  border: 1px solid #25466b;
  border-radius: 8px;
  background: linear-gradient(145deg, #101b30f5, #080e1ef5);
  box-shadow: 0 0 45px #0066ff0d, inset 0 1px #ffffff08;
}

.cartao-topo {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.icone-login {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border: 1px solid #00e5ff66;
  color: #00e5ff;
  background: #00e5ff0b;
  font-size: 28px;
}

.tag {
  color: #6884a8;
  font-size: 12px;
  letter-spacing: 2px;
}

.cartao-login h2 {
  margin: 27px 0 6px;
  font-family: 'Orbitron', sans-serif;
  font-size: 23px;
}

.subtitulo {
  margin: 0 0 28px;
  color: #8da2bf;
  font-size: 17px;
}

.cartao-login form {
  display: flex;
  flex-direction: column;
}

.cartao-login label {
  margin: 16px 0 8px;
  color: #a5bad8;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
}

.cartao-login input {
  width: 100%;
  min-width: 0;
  padding: 14px;
  border: 1px solid #2b405e;
  border-radius: 4px;
  outline: none;
  background: #080f20;
  color: white;
  font-family: 'Rajdhani', sans-serif;
  font-size: 17px;
  transition: 0.2s;
}

.cartao-login input::placeholder {
  color: #566984;
}

.cartao-login input:focus {
  border-color: #00e5ff;
  box-shadow: 0 0 15px #00e5ff18;
}

.botao-entrar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 25px;
  padding: 15px 18px;
  border: 1px solid #00e5ff;
  border-radius: 4px;
  background: #00d9f5;
  color: #04101d;
  font-family: 'Rajdhani', sans-serif;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
}

.botao-entrar:hover {
  background: #8bf5ff;
  box-shadow: 0 0 25px #00e5ff44;
}

.botao-entrar span {
  font-size: 23px;
}

.divisor {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 26px 0;
}

.divisor span {
  flex: 1;
  height: 1px;
  background: #24344d;
}

.divisor small {
  color: #647c9d;
  font-size: 10px;
  letter-spacing: 2px;
}

.cadastro {
  color: #8296b2;
  text-align: center;
  font-size: 15px;
}

.cadastro button {
  border: none;
  background: none;
  color: #00e5ff;
  font-family: 'Rajdhani', sans-serif;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.cadastro button:hover {
  text-shadow: 0 0 10px #00e5ff;
}

.rodape-cartao {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 25px;
  padding-top: 17px;
  border-top: 1px solid #1e2e46;
  color: #617895;
  font-size: 10px;
  letter-spacing: 1px;
}

.rodape-cartao .ponto {
  width: 6px;
  height: 6px;
  background: #00ffb3;
  box-shadow: 0 0 8px #00ffb3;
}

.codigo {
  margin-left: auto;
  color: #48617f;
}

.rodape {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  color: #526783;
  font-size: 11px;
  letter-spacing: 2px;
}

@media (max-width: 850px) {
  .conteudo {
    grid-template-columns: 1fr;
    gap: 45px;
    max-width: 550px;
    width: 100%;
    margin: 0 auto;
  }

  .painel-info h1 {
    font-size: 38px;
  }

  .mini-painel {
    margin-top: 25px;
  }
}

@media (max-width: 480px) {
  .pagina-login {
    padding: 22px 5%;
  }

  .marca {
    font-size: 13px;
  }

  .voltar {
    font-size: 14px;
  }

  .conteudo {
    padding: 50px 0 35px;
  }

  .cartao-login {
    padding: 23px;
  }

  .rodape {
    flex-wrap: wrap;
    font-size: 9px;
    letter-spacing: 1px;
  }
}
</style>
```
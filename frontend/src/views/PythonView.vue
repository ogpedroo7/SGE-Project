<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { requisicaoAutenticada } from '../auth'

const router = useRouter()

const horasEstudadas = ref(0)
const progresso = ref(0)
const nivel = ref(1)
const jaComecou = ref(false)
const carregando = ref(true)
const salvando = ref(false)
const erro = ref('')

const API = 'http://127.0.0.1:8000'

function obterUsuario() {
  try {
    return JSON.parse(localStorage.getItem('usuario') || 'null')
  } catch {
    return null
  }
}

function urlProgresso() {
  const usuario = obterUsuario()

  if (!usuario?.id) {
    router.push('/login')
    throw new Error('Entre na sua conta para acessar seu progresso.')
  }

  return `${API}/usuarios/${usuario.id}/materias/Python/progresso`
}

async function carregarProgresso() {
  carregando.value = true
  erro.value = ''

  try {
    const resposta = await requisicaoAutenticada(urlProgresso())
    const dados = await resposta.json()

    if (!resposta.ok) {
      throw new Error(dados.detail || 'Não foi possível carregar o progresso.')
    }

    horasEstudadas.value = dados.horas_estudadas
    progresso.value = dados.progresso
    nivel.value = dados.nivel
    jaComecou.value = dados.progresso > 0 || dados.horas_estudadas > 0
  } catch (e) {
    erro.value = e.message || 'Não foi possível conectar ao servidor.'
  } finally {
    carregando.value = false
  }
}

async function salvarProgresso() {
  erro.value = ''

  if (
    !Number.isFinite(horasEstudadas.value) ||
    horasEstudadas.value < 0 ||
    !Number.isInteger(progresso.value) ||
    progresso.value < 0 ||
    progresso.value > 100
  ) {
    erro.value = 'Informe horas válidas e um progresso inteiro entre 0 e 100.'
    return
  }

  salvando.value = true

  try {
    const resposta = await requisicaoAutenticada(urlProgresso(), {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    horas_estudadas: horasEstudadas.value,
    progresso: progresso.value,
    nivel: nivel.value
  })
})

    const dados = await resposta.json()

    if (!resposta.ok) {
      throw new Error(dados.detail || 'Não foi possível salvar o progresso.')
    }

    horasEstudadas.value = dados.horas_estudadas
    progresso.value = dados.progresso
    nivel.value = dados.nivel
    jaComecou.value = dados.progresso > 0 || dados.horas_estudadas > 0

    alert('Progresso salvo com sucesso!')
  } catch (e) {
    erro.value = e.message || 'Não foi possível conectar ao servidor.'
  } finally {
    salvando.value = false
  }
}

function iniciarEstudos() {
  router.push('/python/estudo')
}

onMounted(carregarProgresso)
</script>

<template>
  <main class="painel-python">
    <button class="botao-voltar" @click="router.push('/dashboard')">
      ← Voltar às matérias
    </button>

    <header>
      <p class="identificador">SGE / MATÉRIA</p>
      <h1>Python</h1>
      <p class="descricao">
        Aprenda fundamentos, lógica de programação e desenvolvimento com Python.
      </p>
    </header>

    <p v-if="carregando">Carregando seu progresso...</p>
    <p v-else-if="erro" class="mensagem-erro">{{ erro }}</p>

    <template v-else>
      <section class="resumo">
        
<article class="card-resumo">
  <h2>Horas estudadas</h2>
  <p>
    {{
      Math.floor((horasEstudadas || 0) * 3600 / 3600)
    }} h
    {{
      Math.floor(((horasEstudadas || 0) * 3600) % 3600 / 60)
    }} min
    {{
      Math.floor(((horasEstudadas || 0) * 3600) % 60)
    }} s
  </p>
</article>


        <article class="card-resumo">
          <h2>Progresso geral</h2>
          <p>{{ progresso }}%</p>
        </article>
      </section>

      <section class="area-estudos">
        <h2>Sua jornada de aprendizagem</h2>
        <p>
          {{ jaComecou
            ? 'Continue de onde você parou e avance no seu aprendizado.'
            : 'Sua jornada está pronta para começar. Vamos nessa?' }}
        </p>

        <button class="botao-estudar" @click="iniciarEstudos">
          {{ jaComecou ? 'Continuar estudos →' : 'Iniciar estudos →' }}
        </button>
      </section>
    </template>
  </main>
</template>

<style scoped>
.painel-python {
  min-height: 100vh;
  padding: 40px;
  background: #07111f;
  color: #eaf6ff;
  font-family: Arial, sans-serif;
}

.botao-voltar {
  padding: 10px 16px;
  background: #101f33;
  color: #00e5ff;
  border: 1px solid #00bcd4;
  border-radius: 8px;
  cursor: pointer;
}

header {
  margin-top: 35px;
}

.identificador {
  color: #00e5ff;
  font-size: 12px;
  letter-spacing: 2px;
}

h1 {
  color: #00e5ff;
  font-size: 36px;
}

.descricao {
  color: #9db8d0;
  max-width: 600px;
  line-height: 1.6;
}

.resumo {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-top: 35px;
}

.card-resumo {
  flex: 1;
  min-width: 200px;
  padding: 24px;
  background: #101f33;
  border: 1px solid #00bcd4;
  border-radius: 12px;
}

.card-resumo h2 {
  color: #9db8d0;
  font-size: 16px;
}

.card-resumo p {
  color: #00e5ff;
  font-size: 30px;
  font-weight: bold;
  margin-bottom: 0;
}

.area-estudos {
  margin-top: 30px;
  padding: 28px;
  background: #101f33;
  border: 1px solid #24445d;
  border-radius: 12px;
}

.area-estudos h2,
.area-teste h3 {
  color: #eaf6ff;
}

.area-estudos p {
  color: #9db8d0;
  line-height: 1.6;
}

.botao-estudar,
.area-teste button {
  margin-top: 15px;
  padding: 14px 22px;
  background: #00d9f5;
  color: #07111f;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.botao-estudar:hover,
.area-teste button:hover {
  background: #66edff;
}

.area-teste {
  display: grid;
  gap: 15px;
  max-width: 400px;
  margin-top: 30px;
}

.area-teste label {
  display: grid;
  gap: 8px;
  color: #9db8d0;
}

.area-teste input {
  padding: 10px;
  border: 1px solid #2b405e;
  border-radius: 6px;
  background: #080f20;
  color: white;
}

.area-teste button:disabled {
  opacity: 0.6;
  cursor: wait;
}

.mensagem-erro {
  color: #ff8e8e;
}

@media (max-width: 600px) {
  .painel-python {
    padding: 24px 18px;
  }
}
</style>

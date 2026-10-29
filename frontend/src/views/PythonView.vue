<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const horasEstudadas = ref(0)
const progresso = ref(0)
const jaComecou = ref(false)
const carregando = ref(true)
const erro = ref('')

async function carregarProgresso() {
  try {
    const resposta = await fetch('http://127.0.0.1:8000/python/progresso')

    if (!resposta.ok) {
      throw new Error('Não foi possível carregar o progresso.')
    }

    const dados = await resposta.json()

    horasEstudadas.value = dados.horas_estudadas
    progresso.value = dados.progresso
  } catch (erroRecebido) {
    erro.value = erroRecebido.message
    console.error('Erro ao buscar progresso:', erroRecebido)
  } finally {
    carregando.value = false
  }
}

onMounted


async function salvarProgresso() {
  try {
    erro.value = ''

    const resposta = await fetch('http://127.0.0.1:8000/python/progresso', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        horas_estudadas: horasEstudadas.value,
        progresso: progresso.value
      })
    })

    if (!resposta.ok) {
      throw new Error('Não foi possível salvar o progresso.')
    }

    const dados = await resposta.json()
    horasEstudadas.value = dados.horas_estudadas
    progresso.value = dados.progresso
  } catch (erroRecebido) {
    erro.value = erroRecebido.message
    console.error('Erro ao salvar progresso:', erroRecebido)
  }
}


(carregarProgresso)

function iniciarEstudos() {
  jaComecou.value = true
  router.push('/python/estudo')
}
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

    <section class="resumo">
      <article class="card-resumo">
        <h2>Horas estudadas</h2>
        <p>{{ horasEstudadas }} h</p>
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
      <div class="area-teste">
  <label>
    Horas estudadas:
    <input v-model.number="horasEstudadas" type="number" min="0" step="0.5">
  </label>

  <label>
    Progresso (%):
    <input v-model.number="progresso" type="number" min="0" max="100">
  </label>

  <button @click="salvarProgresso">
    Salvar progresso de teste
  </button>

  <p v-if="erro">{{ erro }}</p>
</div>
    </section>
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
  margin-left: 100px;
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

.area-estudos h2 {
  color: #eaf6ff;
}

.area-estudos p {
  color: #9db8d0;
  line-height: 1.6;
}

.botao-estudar {
  margin-top: 15px;
  padding: 14px 22px;
  background: #00d9f5;
  color: #07111f;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}

.botao-estudar:hover {
  background: #66edff;
}
</style>

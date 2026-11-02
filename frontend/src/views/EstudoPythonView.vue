<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { requisicaoAutenticada } from '../auth'

const router = useRouter()
const API = import.meta.env.VITE_API_URL
const materia = 'Python'

let usuario = null
try {
  usuario = JSON.parse(localStorage.getItem('usuario') || 'null')
} catch {
  usuario = null
}

const nomesNiveis = [
  'Iniciante Absoluto', 'Fundamentos Básicos',
  'Lógica de Programação', 'Controle de Fluxo',
  'Manipulação de Dados', 'Funções e Organização',
  'Python Intermediário', 'Orientação a Objetos',
  'Python Avançado', 'Domínio Prático'
]

const carregando = ref(true)
const erro = ref('')
const modo = ref('aula')
const nivel = ref(1)
const pagina = ref(1)
const aula = ref(null)
const paginasConcluidas = ref([])
const horasEstudadas = ref(0)
const segundosEstudados = ref(0)
const resposta = ref('')
const resultadoAula = ref(null)
const salvando = ref(false)
const mensagem = ref('')
const resumo = ref('')
const quiz = ref([])
const respostasQuiz = ref({})
const indiceQuiz = ref(0)
const resultadoQuiz = ref(null)
const recuperacao = ref(false)
const respostasSalvas = ref([])
const acertosAcumulados = ref(0)
const nivelAprovado = ref(false)
const segundosPendentes = ref(0)

let intervaloTempo = null
let intervaloEnvio = null
let enviandoTempo = false
let desmontando = false
let ultimoInstante = 0

const nomeNivel = computed(() => nomesNiveis[nivel.value - 1])
const chavePagina = computed(() => `${nivel.value}:${pagina.value}`)
const paginaConcluida = computed(() =>
  paginasConcluidas.value.includes(chavePagina.value)
)
const progressoGeral = computed(() =>
  Math.round(paginasConcluidas.value.length / 100 * 100)
)
const paginasNivelConcluidas = computed(() =>
  paginasConcluidas.value.filter(p => p.startsWith(`${nivel.value}:`)).length
)
const progressoNivel = computed(() =>
  Math.round(paginasNivelConcluidas.value / 10 * 100)
)
const questaoAtual = computed(() => quiz.value[indiceQuiz.value] || null)
const quantidadeQuiz = computed(() => quiz.value.length)
const numeroQuestao = computed(() => indiceQuiz.value + 1)

async function requisicao(url, opcoes = {}) {
  const respostaApi = await requisicaoAutenticada(`${API}${url}`, {
    ...opcoes,
    headers: {
      'Content-Type': 'application/json',
      ...(opcoes.headers || {})
    }
  })

  const dados = await respostaApi.json().catch(() => ({}))

  if (!respostaApi.ok) {
    throw new Error(
      typeof dados.detail === 'string'
        ? dados.detail
        : 'Não foi possível comunicar com o servidor.'
    )
  }

  return dados
}


function caminhoCurso(sufixo = '') {
  return `/usuarios/${usuario.id}/materias/${materia}/curso${sufixo}`
}

async function carregarCurso() {
  if (!usuario?.id) {
    erro.value = 'Seu login não foi encontrado. Entre novamente na sua conta.'
    carregando.value = false
    return
  }

  try {
    const dados = await requisicao(caminhoCurso())
    const estado = dados.estado || {}

    nivel.value = Number(estado.nivel || 1)
    pagina.value = Number(estado.pagina || 1)

    paginasConcluidas.value = Array.isArray(estado.paginas_concluidas)
      ? estado.paginas_concluidas.map(String)
      : []

    segundosEstudados.value = Number(estado.segundos_estudados || 0)
    horasEstudadas.value = segundosEstudados.value / 3600

    await carregarAula()
  } catch (e) {
    erro.value = `Não foi possível carregar o curso: ${e.message}`
  } finally {
    carregando.value = false
  }
}

async function carregarAula() {
  salvando.value = true
  mensagem.value = ''
  resultadoAula.value = null
  resposta.value = ''

  try {
    aula.value = await requisicao(
      `${caminhoCurso('/aula')}?nivel=${nivel.value}&pagina=${pagina.value}`
    )

    await requisicao(caminhoCurso('/pagina'), {
      method: 'PUT',
      body: JSON.stringify({
        nivel: nivel.value,
        pagina: pagina.value,
        concluir: false
      })
    })
  } catch (e) {
    aula.value = null
    mensagem.value = e.message
  } finally {
    salvando.value = false
  }
}



async function mudarNivel(destino) {
  if (destino < 1 || destino > 10 || salvando.value) return

  try {
    await requisicao(
      `${caminhoCurso('/aula')}?nivel=${destino}&pagina=1`
    )

    nivel.value = destino
    pagina.value = 1
    modo.value = 'aula'
    await carregarAula()
  } catch (e) {
    mensagem.value = e.message
  }
}

async function verificarRespostaAula() {
  if (!resposta.value || salvando.value || !aula.value) {
    mensagem.value = 'Escolha uma alternativa primeiro.'
    return
  }

  salvando.value = true
  mensagem.value = ''

  try {
    const resultado = await requisicao(
      caminhoCurso('/aula/responder'),
      {
        method: 'POST',
        body: JSON.stringify({
          nivel: nivel.value,
          pagina: pagina.value,
          resposta: resposta.value
        })
      }
    )

    paginasConcluidas.value = resultado.paginas_concluidas || []
    resultadoAula.value = { registrada: true }
    mensagem.value = resultado.mensagem
  } catch (e) {
    mensagem.value = e.message
  } finally {
    salvando.value = false
  }
}

async function mudarPagina(destino) {
  if (salvando.value) return

  if (destino < 1) return

  if (destino > 10) {
    if (paginasNivelConcluidas.value < 10) {
      mensagem.value = 'Responda às questões das 10 páginas antes de ir ao resumo.'
      return
    }

    modo.value = 'resumo'
    mensagem.value = ''
    resumo.value = ''
    return
  }

  if (destino > pagina.value && !paginaConcluida.value) {
    mensagem.value = 'Registre sua resposta antes de avançar.'
    return
  }

  pagina.value = destino
  resposta.value = ''
  resultadoAula.value = null
  mensagem.value = ''

  await carregarAula()
}

/*
 * CRONÔMETRO
 *
 * A tela atualiza localmente a cada segundo.
 * O backend recebe os segundos pendentes periodicamente.
 * A sincronização não substitui o contador local por uma resposta antiga.
 */

async function enviarTempo() {
  if (!usuario?.id || segundosPendentes.value <= 0 || enviandoTempo) {
    return
  }

  const segundos = Math.min(segundosPendentes.value, 3600)
  segundosPendentes.value -= segundos
  enviandoTempo = true

  try {
    const dados = await requisicao(caminhoCurso('/tempo'), {
      method: 'POST',
      body: JSON.stringify({ segundos })
    })

    // Usa o valor do servidor somente para confirmar um total válido.
    // Não deixa a resposta atrasada fazer o relógio visual retroceder.
    if (Number.isFinite(Number(dados.segundos_estudados))) {
      segundosEstudados.value = Math.max(
        segundosEstudados.value,
        Number(dados.segundos_estudados)
      )
    }

    horasEstudadas.value = segundosEstudados.value / 3600
  } catch (e) {
    segundosPendentes.value += segundos
    console.error('Erro ao salvar tempo de estudo:', e)
  } finally {
    enviandoTempo = false
  }
}

function atualizarCronometro() {
  if (desmontando || !ultimoInstante) return

  const agora = Date.now()
  const segundosDecorridos = Math.floor((agora - ultimoInstante) / 1000)

  if (segundosDecorridos > 0) {
    ultimoInstante += segundosDecorridos * 1000
    segundosEstudados.value += segundosDecorridos
    segundosPendentes.value += segundosDecorridos
    horasEstudadas.value = segundosEstudados.value / 3600
  }
}

function iniciarCronometro() {
  pararIntervalos()

  desmontando = false
  ultimoInstante = Date.now()

  intervaloTempo = setInterval(atualizarCronometro, 250)
  intervaloEnvio = setInterval(() => {
    void enviarTempo()
  }, 10000)
}

function pararIntervalos() {
  if (intervaloTempo) clearInterval(intervaloTempo)
  if (intervaloEnvio) clearInterval(intervaloEnvio)

  intervaloTempo = null
  intervaloEnvio = null
}

function formatarTempo(segundos) {
  const total = Math.max(0, Math.floor(Number(segundos) || 0))
  const horas = Math.floor(total / 3600)
  const minutos = Math.floor((total % 3600) / 60)
  const segundosRestantes = total % 60

  return `${String(horas).padStart(2, '0')}:${String(minutos).padStart(2, '0')}:${String(segundosRestantes).padStart(2, '0')}`
}

async function concluirResumo() {
  salvando.value = true
  mensagem.value = ''

  try {
    await requisicao(caminhoCurso('/resumo'), {
      method: 'POST',
      body: JSON.stringify({ nivel: nivel.value })
    })

    resumo.value = 'Resumo concluído! Você já pode iniciar o quiz.'
    modo.value = 'resumo'
  } catch (e) {
    mensagem.value = e.message
  } finally {
    salvando.value = false
  }
}

async function iniciarQuiz() {
  salvando.value = true
  mensagem.value = ''

  try {
    const dados = await requisicao(
      `${caminhoCurso('/quiz')}?nivel=${nivel.value}`
    )

    respostasSalvas.value = dados.respostas_salvas || []
    acertosAcumulados.value =
      respostasSalvas.value.filter(r => r.acertou).length

    const jaRespondidas = new Set(
      respostasSalvas.value.map(r => String(r.questao_id))
    )

    const erradas = respostasSalvas.value
      .filter(r => !r.acertou)
      .map(r => String(r.questao_id))

    recuperacao.value = erradas.length > 0 && jaRespondidas.size >= 10
    const questoes = dados.questoes || []

    quiz.value = recuperacao.value
      ? questoes.filter(q => erradas.includes(String(q.id)))
      : questoes.filter(q => !jaRespondidas.has(String(q.id)))

    if (quiz.value.length === 0 && acertosAcumulados.value < 8) {
      recuperacao.value = true
      quiz.value = questoes.filter(q => erradas.includes(String(q.id)))
    }

    respostasQuiz.value = {}
    indiceQuiz.value = 0
    resultadoQuiz.value = null
    nivelAprovado.value = false
    modo.value = 'quiz'

    if (quiz.value.length === 0 && acertosAcumulados.value >= 8) {
      nivelAprovado.value = true
      resultadoQuiz.value = {
        aprovado: true,
        acertos_acumulados: acertosAcumulados.value,
        proximo_nivel: Math.min(10, nivel.value + 1)
      }
      modo.value = 'resultado'
    }
  } catch (e) {
    mensagem.value = e.message
  } finally {
    salvando.value = false
  }
}

async function responderQuestaoQuiz() {
  if (!questaoAtual.value || !respostasQuiz.value[questaoAtual.value.id]) {
    mensagem.value = 'Selecione uma alternativa.'
    return
  }

  salvando.value = true
  mensagem.value = ''

  try {
    const dados = await requisicao(caminhoCurso('/quiz/responder'), {
      method: 'POST',
      body: JSON.stringify({
        nivel: nivel.value,
        questao_id: String(questaoAtual.value.id),
        resposta: respostasQuiz.value[questaoAtual.value.id]
      })
    })

    if (dados.acertou) {
      acertosAcumulados.value = Math.max(
        acertosAcumulados.value,
        Number(dados.acertos_acumulados || 0)
      )
    }

    if (dados.aprovado) {
      nivelAprovado.value = true
      resultadoQuiz.value = dados
      modo.value = 'resultado'
      return
    }

    if (indiceQuiz.value < quiz.value.length - 1) {
      indiceQuiz.value += 1
    } else {
      resultadoQuiz.value = dados
      modo.value = 'resultado'
    }
  } catch (e) {
    mensagem.value = e.message
  } finally {
    salvando.value = false
  }
}

async function tentarQuizNovamente() {
  await iniciarQuiz()
}

async function irParaProximoNivel() {
  if (nivel.value >= 10) {
    mensagem.value = 'Parabéns! Você concluiu todos os níveis de Python.'
    return
  }

  const destino = nivel.value + 1

  try {
    await requisicao(`${caminhoCurso('/aula')}?nivel=${destino}&pagina=1`)
    nivel.value = destino
    pagina.value = 1
    modo.value = 'aula'
    await carregarAula()
  } catch (e) {
    mensagem.value = e.message
  }
}

onMounted(() => {
  // Não usar await no nível superior de <script setup>.
  void (async () => {
    await carregarCurso()

    if (!erro.value && usuario?.id) {
      iniciarCronometro()
    }
  })()
})

onUnmounted(() => {
  desmontando = true
  atualizarCronometro()
  pararIntervalos()

  // Tenta enviar os segundos que ficaram pendentes ao sair.
  void enviarTempo()
})
</script>

<template>
  <main class="pagina-estudos">
    <button class="botao-voltar" @click="router.push('/python')">
      ← Voltar ao curso
    </button>

    <p v-if="carregando" class="aviso">Carregando seu progresso...</p>

    <div v-else-if="erro" class="aviso erro">
      {{ erro }}
      <button class="botao-secundario" @click="carregarCurso">
        Tentar novamente
      </button>
    </div>

    <template v-else>
      <header class="cabecalho-estudo">
        <span class="etiqueta">SGE · PYTHON</span>
        <h1>Estudando Python</h1>
        <p>Aprenda no seu ritmo. Seu progresso fica salvo na sua conta.</p>
      </header>

      <section class="painel-resumo">
        <div>
          <span class="texto-secundario">PROGRESSO GERAL</span>
          <strong class="destaque">{{ progressoGeral }}%</strong>
        </div>
        <div>
          <span class="texto-secundario">TEMPO DE ESTUDO</span>
          <strong class="destaque">{{ formatarTempo(segundosEstudados) }}</strong>
        </div>
        <div>
          <span class="texto-secundario">PÁGINAS CONCLUÍDAS</span>
          <strong class="destaque">{{ paginasConcluidas.length }}/100</strong>
        </div>
      </section>

      <section class="progresso-nivel">
        <span class="texto-secundario">NÍVEL {{ nivel }} DE 10</span>
        <h2>{{ nomeNivel }}</h2>

        <div class="barra-progresso">
          <div class="barra-preenchida" :style="{ width: `${progressoNivel}%` }"></div>
        </div>

        <div class="linha-inferior">
          <span>{{ progressoNivel }}% deste nível concluído</span>
          <span>{{ paginasNivelConcluidas }}/10 páginas</span>
        </div>

        <div class="seletor-niveis">
          <button
            v-for="(nome, indice) in nomesNiveis"
            :key="nome"
            :class="{ ativo: nivel === indice + 1 }"
            @click="mudarNivel(indice + 1)"
          >
            {{ indice + 1 }}
          </button>
        </div>
        <p class="texto-secundario">
          Níveis futuros só podem ser abertos após a aprovação no nível anterior.
        </p>
      </section>

      <section v-if="modo === 'aula' && aula" class="conteudo">
        <div class="cabecalho-pagina">
          <span class="etiqueta">PÁGINA {{ pagina }} DE 10</span>
          <span v-if="paginaConcluida" class="selo-concluido">Concluída</span>
        </div>

        <h2>{{ aula.titulo }}</h2>
        <p class="explicacao">{{ aula.conteudo }}</p>

        <div class="exemplo">
          <span class="texto-secundario">EXEMPLO DE CÓDIGO</span>
          <pre><code>{{ aula.codigo }}</code></pre>
          <p class="texto-secundario">
            Leia o exemplo e tente entender o que cada instrução faz.
          </p>
        </div>

        <div class="atividade">
          <span class="etiqueta">HORA DE PRATICAR</span>
          <h3>{{ aula.pergunta }}</h3>

          <label
            v-for="opcao in aula.opcoes"
            :key="opcao.id"
            class="alternativa"
            :class="{ selecionada: resposta === opcao.id }"
          >
            <input
              v-model="resposta"
              type="radio"
              :value="opcao.id"
              :disabled="paginaConcluida || salvando"
            />
            <span>{{ opcao.texto }}</span>
          </label>

          <p v-if="resultadoAula" class="resultado correto">
  Resposta registrada. Você já pode continuar.
</p>

          <p v-if="mensagem" class="mensagem">{{ mensagem }}</p>

          <button
  v-if="!paginaConcluida"
  class="botao-principal"
  :disabled="salvando || !!resultadoAula"
  @click="verificarRespostaAula"
>
  {{ salvando ? 'Registrando...' : 'Registrar resposta' }}
</button>
        </div>

        <div class="navegacao">
          <button
            class="botao-secundario"
            :disabled="pagina === 1 || salvando"
            @click="mudarPagina(pagina - 1)"
          >
            ← Página anterior
          </button>

          <button
            class="botao-principal botao-proximo"
            :disabled="salvando"
            @click="mudarPagina(pagina + 1)"
          >
            {{ pagina === 10 ? 'Ir para o resumo →' : 'Próxima página →' }}
          </button>
        </div>
      </section>

      <section v-else-if="modo === 'resumo'" class="conteudo">
        <span class="etiqueta">REVISÃO DO NÍVEL {{ nivel }}</span>
        <h2>Resumo: {{ nomeNivel }}</h2>

        <p class="explicacao">
          Você concluiu as páginas deste nível. Antes de avançar, revise os
          conceitos e os exemplos estudados. O quiz verifica se você compreendeu
          os conteúdos.
        </p>

        <div class="lista-resumo">
          <p v-for="n in 10" :key="n">
            <span :class="{ concluido: paginasConcluidas.includes(`${nivel}:${n}`) }">
              {{ paginasConcluidas.includes(`${nivel}:${n}`) ? '✓' : '○' }}
            </span>
            Página {{ n }} — {{ paginasConcluidas.includes(`${nivel}:${n}`) ? 'Concluída' : 'Pendente' }}
          </p>
        </div>

        <p v-if="mensagem" class="mensagem">{{ mensagem }}</p>
        <p v-if="resumo" class="resultado correto">{{ resumo }}</p>

        <button class="botao-principal" :disabled="salvando" @click="concluirResumo">
          {{ salvando ? 'Salvando...' : 'Confirmar conclusão do resumo' }}
        </button>

        <button class="botao-secundario largura-total" :disabled="salvando" @click="iniciarQuiz">
          {{ salvando ? 'Preparando quiz...' : 'Iniciar quiz do nível' }}
        </button>

        <button class="botao-secundario largura-total" @click="modo = 'aula'">
          Voltar às aulas
        </button>
      </section>

      <section v-else-if="modo === 'quiz' && questaoAtual" class="conteudo">
        <span class="etiqueta">
          {{ recuperacao ? 'RECUPERAÇÃO' : 'QUIZ FINAL' }} · NÍVEL {{ nivel }}
        </span>
        <h2>Questão {{ numeroQuestao }} de {{ quantidadeQuiz }}</h2>

        <div class="barra-progresso">
          <div
            class="barra-preenchida"
            :style="{ width: `${numeroQuestao / quantidadeQuiz * 100}%` }"
          ></div>
        </div>

        <h3 class="pergunta-quiz">{{ questaoAtual.pergunta }}</h3>

        <label
          v-for="opcao in questaoAtual.opcoes"
          :key="opcao.id"
          class="alternativa"
          :class="{ selecionada: respostasQuiz[questaoAtual.id] === opcao.id }"
        >
          <input
            v-model="respostasQuiz[questaoAtual.id]"
            type="radio"
            :value="opcao.id"
          />
          <span>{{ opcao.texto }}</span>
        </label>

        <p v-if="mensagem" class="mensagem">{{ mensagem }}</p>

        <button class="botao-principal" :disabled="salvando" @click="responderQuestaoQuiz">
          {{ salvando ? 'Salvando resposta...' : 'Confirmar e continuar' }}
        </button>
      </section>

      <section v-else-if="modo === 'resultado'" class="conteudo">
        <span class="etiqueta">RESULTADO DO QUIZ</span>
        <h2>{{ nivelAprovado || resultadoQuiz?.aprovado ? 'Nível aprovado!' : 'Vamos revisar juntos' }}</h2>

        <p class="explicacao">
          Acertos acumulados: {{ resultadoQuiz?.acertos_acumulados ?? acertosAcumulados }} de 10.
          Você precisa de pelo menos 8 acertos para avançar.
        </p>

        <div v-if="nivelAprovado || resultadoQuiz?.aprovado" class="resultado correto">
          Parabéns! Você concluiu este nível. Seu progresso foi salvo.
        </div>

        <div v-else class="resultado">
          Você ainda não atingiu 8 acertos. As questões erradas ficam disponíveis para recuperação.
        </div>

        <p v-if="mensagem" class="mensagem">{{ mensagem }}</p>

        <button
          v-if="nivelAprovado || resultadoQuiz?.aprovado"
          class="botao-principal"
          @click="irParaProximoNivel"
        >
          {{ nivel === 10 ? 'Finalizar curso' : 'Avançar para o próximo nível →' }}
        </button>

        <button
          v-else
          class="botao-principal"
          :disabled="salvando"
          @click="tentarQuizNovamente"
        >
          Revisar questões erradas
        </button>

        <button class="botao-secundario largura-total" @click="modo = 'aula'">
          Voltar ao conteúdo
        </button>
      </section>

      <p v-else-if="modo === 'aula'" class="aviso">
        {{ mensagem || 'Não foi possível carregar esta aula.' }}
        <button class="botao-secundario" @click="carregarAula">Tentar novamente</button>
      </p>

      <footer class="rodape-estudo">
        <span>Tempo estudado: {{ horasEstudadas.toFixed(2) }} horas</span>
        <span>Progresso salvo na sua conta</span>
      </footer>
    </template>
  </main>
</template>

<style scoped>
*,
*::before,
*::after {
  box-sizing: border-box;
}

.pagina-estudos {
  width: 100%;
  max-width: 1050px;
  min-width: 0;
  margin: 0 auto;
  padding: 32px 26px 40px;
  color: #e2e8f0;
  overflow-wrap: anywhere;
}

.pagina-estudos > *,
.pagina-estudos section,
.pagina-estudos header,
.pagina-estudos footer {
  min-width: 0;
  max-width: 100%;
}

button {
  font: inherit;
  max-width: 100%;
  overflow-wrap: anywhere;
}

.botao-voltar,
.botao-secundario {
  padding: 12px 17px;
  background: #101f33;
  border: 1px solid #334155;
  color: #cbd5e1;
  border-radius: 10px;
  cursor: pointer;
}

.botao-voltar:hover,
.botao-secundario:hover {
  border-color: #22d3ee;
  background: #1e293b;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.cabecalho-estudo {
  margin: 30px 0 26px;
  width: 100%;
  min-width: 0;
}

.cabecalho-estudo h1 {
  margin: 12px 0;
  color: #f8fafc;
  font-size: clamp(28px, 5vw, 40px);
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.cabecalho-estudo p,
.explicacao {
  color: #cbd5e1;
  line-height: 1.9;
  overflow-wrap: anywhere;
}

.etiqueta {
  color: #22d3ee;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1.2px;
  overflow-wrap: anywhere;
}

.texto-secundario {
  color: #94a3b8;
  font-size: 13px;
  overflow-wrap: anywhere;
}

.painel-resumo {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  width: 100%;
  min-width: 0;
  margin-bottom: 24px;
}

.painel-resumo > div {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
  padding: 20px;
  background: #101f33;
  border: 1px solid #334155;
  border-radius: 13px;
}

.destaque {
  color: #22d3ee;
  font-size: 21px;
  overflow-wrap: anywhere;
}

.progresso-nivel,
.conteudo {
  display: block;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding: 30px;
  margin: 0 0 24px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
  overflow: hidden;
}

.progresso-nivel > *,
.conteudo > * {
  min-width: 0;
  max-width: 100%;
}

.progresso-nivel h2,
.conteudo h2 {
  margin: 12px 0 18px;
  color: #f8fafc;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.conteudo > h2 {
  font-size: 27px;
}

.barra-progresso {
  width: 100%;
  max-width: 100%;
  height: 9px;
  margin: 16px 0;
  overflow: hidden;
  background: #0f172a;
  border-radius: 20px;
}

.barra-preenchida {
  height: 100%;
  max-width: 100%;
  background: linear-gradient(90deg, #0891b2, #22d3ee);
  border-radius: 20px;
  transition: width 0.3s;
}

.linha-inferior {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  width: 100%;
  color: #94a3b8;
  font-size: 13px;
}

.seletor-niveis {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-width: 100%;
  margin-top: 22px;
}

.seletor-niveis button {
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  border: 1px solid #475569;
  border-radius: 9px;
  color: #cbd5e1;
  background: #0f172a;
  cursor: pointer;
}

.seletor-niveis button.ativo {
  background: #164e63;
  color: #67e8f9;
  border-color: #22d3ee;
}

.cabecalho-pagina {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  width: 100%;
}

.selo-concluido {
  color: #86efac;
  font-size: 13px;
}

.explicacao {
  white-space: pre-line;
  overflow-wrap: anywhere;
}

.exemplo {
  display: block;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  margin-top: 25px;
  padding: 22px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 12px;
  overflow: hidden;
}

.exemplo > .texto-secundario {
  display: block;
  max-width: 100%;
}

.exemplo pre {
  display: block;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  margin: 14px 0;
  padding: 16px;
  overflow-x: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
  color: #67e8f9;
  background: #080f20;
  border-radius: 8px;
  line-height: 1.8;
}

.exemplo code {
  max-width: 100%;
  white-space: inherit;
  overflow-wrap: anywhere;
  word-break: break-word;
  font-family: Consolas, "Courier New", monospace;
}

.atividade {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  margin-top: 30px;
  padding-top: 25px;
  border-top: 1px solid #334155;
}

.atividade h3,
.pergunta-quiz {
  max-width: 100%;
  min-width: 0;
  color: #f8fafc;
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.alternativa {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding: 16px;
  color: #cbd5e1;
  background: #172437;
  border: 1px solid #334155;
  border-radius: 10px;
  cursor: pointer;
  line-height: 1.7;
  overflow-wrap: anywhere;
}

.alternativa:hover {
  border-color: #0891b2;
}

.alternativa.selecionada {
  border-color: #22d3ee;
  background: #164e63;
}

.alternativa input {
  flex: 0 0 auto;
  margin-top: 5px;
  accent-color: #22d3ee;
}

.alternativa span {
  flex: 1 1 auto;
  min-width: 0;
  overflow-wrap: anywhere;
}

.botao-principal {
  display: block;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding: 15px;
  margin-top: 8px;
  border: 0;
  border-radius: 10px;
  color: #082f49;
  background: #22d3ee;
  font-weight: 800;
  cursor: pointer;
  white-space: normal;
}

.botao-principal:hover:not(:disabled) {
  background: #67e8f9;
}

.botao-proximo {
  width: 100%;
  max-width: 360px;
}

.navegacao {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  width: 100%;
  min-width: 0;
  margin-top: 25px;
}

.navegacao button {
  min-width: 0;
  white-space: normal;
}

.resultado,
.mensagem,
.aviso {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding: 16px;
  border-radius: 10px;
  line-height: 1.7;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.resultado {
  color: #fecaca;
  background: #451a1a;
}

.resultado.correto {
  color: #bbf7d0;
  background: #14532d;
}

.mensagem {
  color: #67e8f9;
  background: #0f172a;
}

.lista-resumo {
  width: 100%;
  max-width: 100%;
  min-width: 0;
  margin: 24px 0;
  padding: 10px 18px;
  background: #0f172a;
  border-radius: 10px;
  overflow: hidden;
}

.lista-resumo p {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
  color: #cbd5e1;
  overflow-wrap: anywhere;
}

.lista-resumo p span {
  flex: 0 0 auto;
  color: #94a3b8;
}

.lista-resumo .concluido {
  color: #86efac;
}

.largura-total {
  width: 100%;
  max-width: 100%;
  margin-top: 12px;
}

.aviso {
  background: #1e293b;
  border: 1px solid #334155;
}

.erro {
  color: #fca5a5;
}

.rodape-estudo {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  width: 100%;
  min-width: 0;
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid #243449;
  color: #94a3b8;
  font-size: 13px;
}

.rodape-estudo span {
  min-width: 0;
  overflow-wrap: anywhere;
}

@media (max-width: 650px) {
  .pagina-estudos {
    padding: 20px 14px 30px;
  }

  .painel-resumo {
    grid-template-columns: minmax(0, 1fr);
  }

  .progresso-nivel,
  .conteudo {
    padding: 19px;
  }

  .exemplo {
    padding: 14px;
  }

  .exemplo pre {
    padding: 12px;
    font-size: 13px;
  }

  .navegacao {
    flex-direction: column;
  }

  .navegacao button {
    width: 100%;
    max-width: 100%;
  }

  .botao-proximo {
    max-width: 100%;
  }

  .rodape-estudo {
    flex-direction: column;
  }
}

@media (max-width: 360px) {
  .pagina-estudos {
    padding-right: 10px;
    padding-left: 10px;
  }

  .progresso-nivel,
  .conteudo {
    padding: 14px;
  }

  .exemplo {
    padding: 10px;
  }

  .alternativa {
    gap: 9px;
    padding: 12px;
  }
}
</style>

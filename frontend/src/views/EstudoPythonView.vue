<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <main class="pagina-estudos">
    <button class="botao-voltar" @click="router.push('/python')">
      ← Voltar ao painel Python
    </button>

    <header>
      <p class="identificador">STUDYCORE / APRENDIZAGEM</p>
      <h1>Estudando Python</h1>
      <p>Construa seu conhecimento passo a passo.</p>
    </header>

    <section class="progresso-nivel">
      <p class="etiqueta">NÍVEL 1 DE 10</p>
      <h2>Iniciante Absoluto</h2>
      <p>
        Aqui você começará a aprender os conceitos fundamentais
        antes de avançar para os próximos níveis.
      </p>

      <div class="informacao-pagina">
        <span>Página 1 de 10</span>
        <span>0% concluído</span>
      </div>
    </section>

    <section class="conteudo">
      <h2>Seu conteúdo de estudo aparecerá aqui</h2>
      <p>
        Cada página terá uma explicação e uma questão para você responder.
        A correção será apresentada ao final do nível, conforme as regras
        do StudyCore.
      </p>
    </section>
  </main>
</template>

<style scoped>
.pagina-estudos {
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

.identificador,
.etiqueta {
  color: #00e5ff;
  font-size: 12px;
  letter-spacing: 2px;
}

h1 {
  color: #00e5ff;
  font-size: 32px;
}

header p:last-child,
.progresso-nivel > p:not(.etiqueta),
.conteudo p {
  color: #9db8d0;
  line-height: 1.7;
}

.progresso-nivel,
.conteudo {
  margin-top: 25px;
  padding: 25px;
  background: #101f33;
  border: 1px solid #24445d;
  border-radius: 12px;
}

.progresso-nivel h2,
.conteudo h2 {
  color: #eaf6ff;
}

.informacao-pagina {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 25px;
  color: #00e5ff;
}
</style>

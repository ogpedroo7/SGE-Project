
<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

function abrirPython() {
  router.push('/python')
}
</script>

<template>
  <main class="dashboard">
    <header>
      <h1>Minhas matérias</h1>
      <p>Escolha uma matéria para continuar sua jornada de estudos.</p>
    </header>

    <section class="materias">
      <div class="card-materia" @click="abrirPython">
        <div>
          <h2>Python</h2>
          <p>Fundamentos e lógica de programação</p>
        </div>

        <span>Entrar na matéria →</span>
      </div>
    </section>
  </main>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 40px;
  background: #07111f;
  color: #eaf6ff;
  font-family: Arial, sans-serif;
}

h1 {
  color: #00e5ff;
  font-size: 32px;
}

header p {
  color: #9db8d0;
}

.materias {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 260px));
  gap: 20px;
  margin-top: 35px;
  align-items: stretch;
}

.card-materia {
  width: 100%;
  box-sizing: border-box;
  padding: 20px;
  background: #101f33;
  border: 1px solid #00bcd4;
  border-radius: 12px;
  cursor: pointer;
  transition: 0.2s;
}

.card-materia:hover {
  border-color: #00e5ff;
  box-shadow: 0 0 15px #00bcd433;
  transform: translateY(-3px);
}

.card-materia h2 {
  color: #00e5ff;
}

.card-materia p {
  color: #9db8d0;
}

.card-materia span {
  display: block;
  margin-top: 20px;
  color: #00e5ff;
}
</style>

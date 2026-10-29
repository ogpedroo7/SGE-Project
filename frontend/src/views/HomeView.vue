```vue
<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <main class="pagina">
    <div class="grade-fundo"></div>
    <div class="luz luz-azul"></div>
    <div class="luz luz-ciano"></div>

    <header class="topo">
      <div class="logo">
        <span class="logo-icone">✦</span>
        <span>SG<span class="destaque">E</span></span>
      </div>

      <span class="status">
        <span class="ponto"></span>
        SISTEMA DE ESTUDOS
      </span>
    </header>

    <section class="hero">
      <div class="etiqueta">
        <span>✧</span> SEU PRÓXIMO NÍVEL COMEÇA AQUI
      </div>

      <h1>
        Sistema de Gerenciamento de <br />
         <span>Estudos.</span>
      </h1>

      <p class="descricao">
        Organize suas matérias, acompanhe seu progresso
        e desbloqueie seu potencial, uma etapa de cada vez.
      </p>

      <div class="acoes">
        <button class="botao botao-principal" @click="router.push('/login')">
          Entrar no sistema
          <span>→</span>
        </button>

        <button class="botao botao-secundario" @click="router.push('/cadastro')">
          Criar minha conta
        </button>
      </div>

      <div class="recursos">
        <div class="recurso">
          <span class="icone">⌘</span>
          <div>
            <strong>Organização</strong>
            <small>Seus estudos em um só lugar</small>
          </div>
        </div>

        <div class="recurso">
          <span class="icone">↗</span>
          <div>
            <strong>Progresso</strong>
            <small>Acompanhe sua evolução</small>
          </div>
        </div>

        <div class="recurso">
          <span class="icone">◇</span>
          <div>
            <strong>Conquistas</strong>
            <small>Avance no seu ritmo</small>
          </div>
        </div>
      </div>
    </section>

    <div class="decoracao">
      <div class="anel anel-externo"></div>
      <div class="anel anel-interno"></div>
      <div class="nucleo">
  <svg
    class="cerebro-tech"
    viewBox="0 0 240 220"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label="Cérebro tecnológico representando o aprendizado"
  >
    <defs>
      <linearGradient id="brainGradient" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#d9f7ff" />
        <stop offset="50%" stop-color="#59c9f5" />
        <stop offset="100%" stop-color="#1478c9" />
      </linearGradient>

      <filter id="brainGlow" x="-40%" y="-40%" width="180%" height="180%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>

    <g
      fill="url(#brainGradient)"
      fill-opacity="0.18"
      stroke="url(#brainGradient)"
      stroke-width="2.5"
      stroke-linecap="round"
      stroke-linejoin="round"
      filter="url(#brainGlow)"
    >
      <path d="M117 45 C106 23 80 29 74 48 C52 43 37 63 46 83 C26 99 35 122 53 132 C47 153 65 171 85 164 C94 184 116 178 119 158 Z" />
      <path d="M123 45 C134 23 160 29 166 48 C188 43 203 63 194 83 C214 99 205 122 187 132 C193 153 175 171 155 164 C146 184 124 178 121 158 Z" />

      <path d="M120 45 V170" stroke="#00e5ff" />

      <path d="M75 49 C96 48 101 66 89 80 C77 94 91 106 106 101" fill="none" />
      <path d="M47 83 C67 78 79 96 68 111 C60 124 79 138 94 128" fill="none" />
      <path d="M72 147 C88 136 101 146 99 160" fill="none" />

      <path d="M165 49 C144 48 139 66 151 80 C163 94 149 106 134 101" fill="none" />
      <path d="M193 83 C173 78 161 96 172 111 C180 124 161 138 146 128" fill="none" />
      <path d="M168 147 C152 136 139 146 141 160" fill="none" />
    </g>

    <g
      fill="#071326"
      stroke="#00e5ff"
      stroke-width="2"
    >
      <circle cx="74" cy="48" r="4" />
      <circle cx="166" cy="48" r="4" />
      <circle cx="46" cy="83" r="4" />
      <circle cx="194" cy="83" r="4" />
      <circle cx="85" cy="164" r="4" />
      <circle cx="155" cy="164" r="4" />
    </g>

    <g
      fill="none"
      stroke="#00e5ff"
      stroke-width="2"
      stroke-linecap="round"
    >
      <path d="M74 48 L49 26 H28" />
      <path d="M166 48 L191 26 H212" />
      <path d="M46 83 H23" />
      <path d="M194 83 H217" />
      <path d="M85 164 L67 187 H46" />
      <path d="M155 164 L173 187 H194" />
    </g>

    <g fill="#00e5ff">
      <circle cx="28" cy="26" r="3" />
      <circle cx="212" cy="26" r="3" />
      <circle cx="23" cy="83" r="3" />
      <circle cx="217" cy="83" r="3" />
      <circle cx="46" cy="187" r="3" />
      <circle cx="194" cy="187" r="3" />
    </g>
  </svg>
</div>
      <span class="orbita orbita-um">S</span>
      <span class="orbita orbita-dois">G</span>
      <span class="orbita orbita-tres">E</span>
      <div class="linha linha-um"></div>
      <div class="linha linha-dois"></div>
      <div class="legenda">LEARN // EVOLVE // REPEAT</div>
    </div>

    <footer>
      <span>SGE © 2026</span>
      <span>SEU FUTURO ESTÁ EM CONSTRUÇÃO<span class="cursor">_</span></span>
    </footer>
  </main>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&display=swap');

:global(*) {
  box-sizing: border-box;
}

:global(body) {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
  background: #050816;
  color: #edf7ff;
  font-family: 'Rajdhani', sans-serif;
}

.pagina {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 30px 7%;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(ellipse at 78% 45%, #10234a66 0%, transparent 45%),
    linear-gradient(135deg, #050816, #080d20 60%, #050816);
}

.grade-fundo {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.15;
  background-image:
    linear-gradient(#244a7a 1px, transparent 1px),
    linear-gradient(90deg, #244a7a 1px, transparent 1px);
  background-size: 45px 45px;
  mask-image: linear-gradient(to bottom, black, transparent 90%);
}

.luz {
  position: absolute;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  filter: blur(110px);
  opacity: 0.17;
  pointer-events: none;
}

.luz-azul {
  background: #1264ff;
  top: 25%;
  right: 12%;
}

.luz-ciano {
  background: #00e5ff;
  bottom: 5%;
  left: 10%;
  width: 180px;
  height: 180px;
  opacity: 0.1;
}

.topo,
.hero,
footer {
  position: relative;
  z-index: 1;
}

.topo {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 2px;
   color: #dbeafe;
}

.logo-icone {
  color: #00e5ff;
  font-size: 30px;
  text-shadow: 0 0 18px #00e5ff;
}

.destaque,
.hero h1 span {
  color: #00e5ff;
}

.status {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #8ba5c8;
  font-size: 13px;
  letter-spacing: 2px;
}

.ponto {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #00ffb3;
  box-shadow: 0 0 12px #00ffb3;
}

.hero {
  width: 58%;
  margin: auto 0;
  padding: 75px 0;
  margin-top: -4px;
}

.etiqueta {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #00e5ff;
  border: 1px solid #00e5ff44;
  background: #00e5ff0a;
  padding: 9px 13px;
  font-size: 20px;
  letter-spacing: 2px;
}

.hero h1 {
  margin: 28px 0 20px;
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(35px, 4.3vw, 64px);
  line-height: 1.2;
  letter-spacing: -2px;
  color: #dbeafe;
  text-align: left;
  font-size: 40px;
}

.hero h1 span {
  text-shadow: 0 0 28px #00e5ff55;
}

.descricao {
  max-width: 500px;
  color: #9bacc8;
  font-size: 20px;
  line-height: 1.6;
}

.acoes {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 32px;
}

.botao {
  min-height: 50px;
  padding: 0 22px;
  border-radius: 5px;
  font-family: 'Rajdhani', sans-serif;
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.25s ease;
}

.botao-principal {
  display: flex;
  align-items: center;
  gap: 22px;
  color: #04101d;
  background: #00e5ff;
  border: 1px solid #00e5ff;
  box-shadow: 0 0 24px #00e5ff22;
}

.botao-principal:hover {
  background: #8bf5ff;
  box-shadow: 0 0 28px #00e5ff66;
  transform: translateY(-2px);
}

.botao-secundario {
  color: #d8e7ff;
  background: #101a30aa;
  border: 1px solid #344767;
}

.botao-secundario:hover {
  border-color: #00e5ff;
  color: #00e5ff;
}

.recursos {
  display: flex;
  flex-wrap: wrap;
  gap: 28px;
  margin-top: 55px;
  color: #dbeafe;
}

.recurso {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #dbeafe;
}

.icone {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  color: #00e5ff;
  border: 1px solid #00e5ff44;
  background: #00e5ff0b;
  font-size: 23px;
}

.recurso strong,
.recurso small {
  display: block;
}

.recurso strong {
  font-size: 16px;
}

.recurso small {
  margin-top: 3px;
  color: #8095b5;
  font-size: 13px;
}

.decoracao {
  position: absolute;
  top: 40%;
  right: 0%;
  width: min(37vw, 470px);
  aspect-ratio: 1;
  transform: translateY(-50%);
  display: grid;
  place-items: center;
}

.anel {
  position: absolute;
  border-radius: 50%;
  border: 1px solid #00e5ff35;
}

.anel-externo {
  inset: 5%;
  border-style: dashed;
  animation: girar 50s linear infinite;
}

.anel-interno {
  inset: 18%;
  border-color: #387bff66;
  box-shadow: 0 0 60px #1264ff0e, inset 0 0 60px #1264ff0e;
  animation: girar 35s linear infinite reverse;
}

.nucleo {
  display: grid;
  place-items: center;
  width: 42%;
  aspect-ratio: 1;
  background: linear-gradient(145deg, #0c2341, #071020);
  border: 1px solid #00e5ff88;
  clip-path: polygon(
    25% 0,
    75% 0,
    100% 25%,
    100% 75%,
    75% 100%,
    25% 100%,
    0 75%,
    0 25%
  );
  filter: drop-shadow(0 0 18px #00e5ff30);
}

.cerebro-tech {
  display: block;
  width: 105%;
  height: auto;
  overflow: visible;
}


.nucleo span {
  color: #00e5ff;
}

.orbita {
  position: absolute;
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border: 1px solid #00e5ff77;
  border-radius: 50%;
  color: #00e5ff;
  background: #09162a;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  box-shadow: 0 0 20px #00e5ff22;
}

.orbita-um {
  top: 12%;
  left: 22%;
}

.orbita-dois {
  right: 8%;
  top: 45%;
}

.orbita-tres {
  bottom: 12%;
  left: 30%;
}

.linha {
  position: absolute;
  width: 20%;
  height: 1px;
  background: linear-gradient(90deg, transparent, #00e5ff99, transparent);
}

.linha-um {
  top: 28%;
  right: 7%;
  transform: rotate(45deg);
}

.linha-dois {
  bottom: 25%;
  left: 8%;
  transform: rotate(-35deg);
}

.legenda {
  position: absolute;
  bottom: 3%;
  color: #6582a8;
  font-size: 11px;
  letter-spacing: 3px;
}

footer {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  color: #526783;
  font-size: 11px;
  letter-spacing: 2px;
}

.cursor {
  color: #00e5ff;
  animation: piscar 1s steps(2) infinite;
}

@keyframes girar {
  to {
    transform: rotate(360deg);
  }
}

@keyframes piscar {
  to {
    opacity: 0;
  }
}

@media (max-width: 850px) {
  .pagina {
    padding: 25px 6%;
  }

  .hero {
    width: 100%;
    padding: 75px 0 40px;
  }

  .decoracao {
    position: relative;
    top: auto;
    right: auto;
    width: min(75vw, 360px);
    margin: 0 auto 40px;
    transform: none;
  }

  .recursos {
    gap: 20px;
  }

  footer {
    flex-wrap: wrap;
    margin-top: auto;
  }
}

@media (max-width: 500px) {
  .status {
    font-size: 9px;
    letter-spacing: 1px;
  }

  .logo {
    font-size: 14px;
  }

  .hero h1 {
    letter-spacing: -1px;
  }

  .descricao {
    font-size: 18px;
  }

  .acoes {
    flex-direction: column;
  }

  .botao {
    justify-content: center;
    width: 100%;
  }

  .recursos {
    flex-direction: column;
  }

  footer {
    font-size: 9px;
    letter-spacing: 1px;
  }
}
</style>
```
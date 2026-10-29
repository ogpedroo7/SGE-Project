<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const nome = ref('')
const email = ref('')
const senha = ref('')
const confirmarSenha = ref('')


async function cadastrar() {
  if (senha.value !== confirmarSenha.value) {
    alert('As senhas não coincidem.')
    return
  }

  try {
    const resposta = await fetch('http://127.0.0.1:8000/usuarios/cadastro', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        nome: nome.value,
        email: email.value,
        senha: senha.value
      })
    })

    const dados = await resposta.json()

    if (!resposta.ok) {
      throw new Error(dados.detail || 'Não foi possível criar a conta.')
    }

    alert('Conta criada com sucesso!')
    router.push('/login')
  } catch (erro) {
    alert(erro.message || 'Não foi possível conectar ao servidor.')
  }
}

</script>

<template>
  <main class="pagina-cadastro">
    <h1>Criar conta</h1>
    <p>Comece sua evolução no SGE.</p>

    <form>
      <form @submit.prevent="cadastrar"></form>
      <label for="nome">Nome completo</label>
      <input
        id="nome"
        v-model="nome"
        type="text"
        placeholder="Digite seu nome"
      />

      <label for="email">E-mail</label>
      <input
        id="email"
        v-model="email"
        type="email"
        placeholder="voce@exemplo.com"
      />

      <label for="senha">Senha</label>
      <input
        id="senha"
        v-model="senha"
        type="password"
        placeholder="Crie uma senha"
      />

      <label for="confirmarSenha">Confirmar senha</label>
      <input
        id="confirmarSenha"
        v-model="confirmarSenha"
        type="password"
        placeholder="Digite a senha novamente"
      />

      <button type="submit">Criar minha conta</button>
    </form>

    <p>
      Já tem uma conta?
      <button @click="router.push('/login')">
        Entrar
      </button>
    </p>
  </main>
</template>

```css
<style scoped>
.pagina-cadastro {
  min-height: 100vh;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  background:
    radial-gradient(ellipse at 50% 30%, #10234a88, transparent 60%),
    #050816;
  color: #edf7ff;
  font-family: 'Rajdhani', sans-serif;
}

h1 {
  margin: 0 0 8px;
  color: #dbeafe;
  font-family: 'Orbitron', sans-serif;
  font-size: 32px;
  text-align: center;
}

.pagina-cadastro > p {
  color: #9bacc8;
  font-size: 18px;
  text-align: center;
}

form {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 400px;
  box-sizing: border-box;
  margin: 20px 0;
  padding: 30px;
  border: 1px solid #25466b;
  border-radius: 8px;
  background: linear-gradient(145deg, #101b30f5, #080e1ef5);
  box-shadow: 0 0 35px #0066ff12;
}

label {
  margin: 14px 0 7px;
  color: #a5bad8;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

input {
  width: 100%;
  box-sizing: border-box;
  padding: 13px;
  border: 1px solid #2b405e;
  border-radius: 4px;
  outline: none;
  background: #080f20;
  color: white;
  font-family: 'Rajdhani', sans-serif;
  font-size: 17px;
  transition: 0.2s;
}

input::placeholder {
  color: #566984;
}

input:focus {
  border-color: #00e5ff;
  box-shadow: 0 0 15px #00e5ff18;
}

form > button {
  margin-top: 25px;
  padding: 14px;
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

form > button:hover {
  background: #8bf5ff;
  box-shadow: 0 0 25px #00e5ff44;
}

.pagina-cadastro > p button {
  border: none;
  background: none;
  color: #00e5ff;
  font-family: 'Rajdhani', sans-serif;
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
}

.pagina-cadastro > p button:hover {
  text-shadow: 0 0 10px #00e5ff;
}

@media (max-width: 480px) {
  h1 {
    font-size: 26px;
  }

  form {
    padding: 22px;
  }
}
</style>
```
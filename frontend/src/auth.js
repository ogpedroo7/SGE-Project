import router from './router'

let redirecionandoLogin = false

export function encerrarSessao() {
  if (redirecionandoLogin) return

  redirecionandoLogin = true

  localStorage.removeItem('token')
  localStorage.removeItem('usuario')

  router.replace({ name: 'login' }).finally(() => {
    redirecionandoLogin = false
  })
}

export async function requisicaoAutenticada(url, opcoes = {}) {
  const token = localStorage.getItem('token')

  if (!token) {
    encerrarSessao()
    throw new Error('Sua sessão expirou. Entre novamente.')
  }

  const resposta = await fetch(url, {
    ...opcoes,
    headers: {
      ...(opcoes.headers || {}),
      Authorization: `Bearer ${token}`
    }
  })

  if (resposta.status === 401) {
    encerrarSessao()
    throw new Error('Sua sessão expirou. Entre novamente.')
  }

  return resposta
}

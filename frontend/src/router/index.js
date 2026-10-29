import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import CadastroView from '../views/CadastroView.vue'
import DashboardView from '../views/DashboardView.vue'
import PythonView from '../views/PythonView.vue'
import EstudoPythonView from '../views/EstudoPythonView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
  path: '/cadastro',
  name: 'cadastro',
  component: CadastroView,
},

{
path: '/dashboard',
name: 'dashboard',
component: DashboardView,

},
{
  path: '/python',
  name: 'python',
  component: PythonView,
},
{
  path: '/python/estudo',
  name: 'estudo-python',
  component: EstudoPythonView,
},
  ],
})

export default router



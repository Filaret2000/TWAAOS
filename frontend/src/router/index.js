import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Componente pentru rutele publice
import Login from '@/views/Login.vue'

// Componente pentru rutele private
import Dashboard from '@/views/Dashboard.vue'
import Schedule from '@/views/Schedule.vue'
import Notifications from '@/views/Notifications.vue'
import UserManagement from '@/views/UserManagement.vue'
import Rooms from '@/views/Rooms.vue'
import ExportData from '@/views/ExportData.vue'
import ImportData from '@/views/ImportData.vue'
import Settings from '@/views/Settings.vue'
import Profile from '@/views/Profile.vue'
import NotFound from '@/views/NotFound.vue'

const routes = [
  // Rute publice
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  
  // Rute private
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: Schedule,
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: Notifications,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true, roles: ['ADM'] }
  },
  {
    path: '/rooms',
    name: 'Rooms',
    component: Rooms,
    meta: { requiresAuth: true, roles: ['ADM', 'SEC', 'CD'] }
  },
  {
    path: '/export',
    name: 'ExportData',
    component: ExportData,
    meta: { requiresAuth: true, roles: ['ADM', 'SEC'] }
  },
  {
    path: '/import',
    name: 'ImportData',
    component: ImportData,
    meta: { requiresAuth: true, roles: ['ADM', 'SEC'] }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  
  // Rută pentru pagini negăsite
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Gardian de navigare pentru a verifica autentificarea și rolurile
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  const user = store.state.auth.user
  
  // Verificăm dacă ruta necesită autentificare
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirecționăm către pagina de login dacă utilizatorul nu este autentificat
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } 
  // Verificăm dacă utilizatorul are rolul necesar pentru a accesa ruta
  else if (to.meta.roles && user && !to.meta.roles.includes(user.role)) {
    // Redirecționăm către dashboard dacă utilizatorul nu are rolul necesar
    next({ name: 'Dashboard' })
  }
  // Redirecționăm către dashboard dacă utilizatorul autentificat încearcă să acceseze pagina de login
  else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Dashboard' })
  }
  // Permitem accesul la rută
  else {
    next()
  }
})

export default router

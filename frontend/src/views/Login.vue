<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header text-center">
        <img src="@/assets/logo.png" alt="Logo FIESC" height="80" class="mb-3" />
        <h1 class="text-3xl font-bold mb-2">Planificare Examene</h1>
        <h2 class="text-xl text-color-secondary mb-4">Facultatea de Inginerie Electrică și Știința Calculatoarelor</h2>
      </div>
      
      <div class="login-body p-4">
        <div v-if="error" class="p-message p-message-error p-3 mb-3">
          <i class="pi pi-exclamation-triangle mr-2"></i>
          <span>{{ error }}</span>
        </div>
        
        <div class="text-center mb-4">
          <p class="mb-3">Autentificați-vă cu contul instituțional USV</p>
          <Button 
            label="Autentificare cu Google" 
            icon="pi pi-google" 
            class="p-button-lg" 
            @click="handleGoogleLogin"
            :loading="loading"
          />
        </div>
      </div>
      
      <div class="login-footer p-3 text-center text-sm text-color-secondary">
        <p>&copy; {{ currentYear }} Universitatea "Ștefan cel Mare" din Suceava</p>
        <p>Toate drepturile rezervate</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const loading = ref(false)
    const error = ref(null)
    const currentYear = computed(() => new Date().getFullYear())
    
    // Funcție pentru autentificarea cu Google
    const handleGoogleLogin = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Inițializăm Google Sign-In API
        const auth2 = window.gapi.auth2.getAuthInstance()
        const googleUser = await auth2.signIn()
        
        // Obținem token-ul ID
        const idToken = googleUser.getAuthResponse().id_token
        
        // Trimitem token-ul către backend pentru autentificare
        await store.dispatch('auth/login', idToken)
        
        // Redirecționăm utilizatorul către pagina solicitată sau dashboard
        const redirectPath = route.query.redirect || '/'
        router.push(redirectPath)
      } catch (err) {
        console.error('Eroare la autentificare:', err)
        error.value = 'Autentificarea a eșuat. Vă rugăm să încercați din nou.'
      } finally {
        loading.value = false
      }
    }
    
    // Inițializăm Google Sign-In API la încărcarea componentei
    onMounted(() => {
      // Verificăm dacă API-ul Google este deja încărcat
      if (window.gapi && window.gapi.auth2) {
        window.gapi.auth2.init({
          client_id: process.env.VUE_APP_GOOGLE_CLIENT_ID
        })
      } else {
        // Încărcăm API-ul Google
        const script = document.createElement('script')
        script.src = 'https://apis.google.com/js/platform.js'
        script.async = true
        script.defer = true
        script.onload = () => {
          window.gapi.load('auth2', () => {
            window.gapi.auth2.init({
              client_id: process.env.VUE_APP_GOOGLE_CLIENT_ID
            })
          })
        }
        document.head.appendChild(script)
      }
    })
    
    return {
      loading,
      error,
      currentYear,
      handleGoogleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--surface-ground);
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 450px;
  background-color: var(--surface-card);
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-header {
  padding: 2rem;
  background-color: var(--primary-color);
  color: var(--primary-color-text);
}

.login-body {
  background-color: var(--surface-card);
}

.login-footer {
  background-color: var(--surface-section);
  border-top: 1px solid var(--surface-border);
}
</style>

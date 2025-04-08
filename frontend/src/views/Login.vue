<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-container">
        <img src="@/assets/logo.svg" alt="FIESC Logo" class="logo" />
        <h1 class="text-3xl font-bold mb-2">FIESC</h1>
        <h2 class="text-xl mb-6">Sistem de planificare examene</h2>
      </div>
      
      <div v-if="error" class="error-message mb-4">
        {{ error }}
      </div>
      
      <div class="login-methods">
        <div v-if="googleAuthAvailable" class="google-login mb-4">
          <Button 
            label="Autentificare cu Google" 
            icon="pi pi-google" 
            class="p-button-raised p-button-secondary w-full"
            @click="handleGoogleLogin"
            :loading="loading"
            :disabled="loading"
          />
        </div>
        
        <div class="divider" v-if="googleAuthAvailable">
          <span>sau</span>
        </div>
        
        <div class="email-login mt-4">
          <form @submit.prevent="handleEmailLogin">
            <div class="field mb-4">
              <label for="email" class="block mb-2">Email</label>
              <InputText 
                id="email" 
                v-model="credentials.email" 
                type="email" 
                class="w-full" 
                placeholder="Adresa de email" 
                required
                :disabled="loading"
              />
            </div>
            
            <div class="field mb-4">
              <label for="password" class="block mb-2">Parolă</label>
              <Password 
                id="password" 
                v-model="credentials.password" 
                class="w-full" 
                placeholder="Parola" 
                toggleMask 
                required
                :disabled="loading"
              />
            </div>
            
            <Button 
              type="submit" 
              label="Autentificare" 
              class="p-button-raised w-full"
              :loading="loading"
              :disabled="loading"
            />
          </form>
        </div>
      </div>
      
      <div class="footer-text mt-6 text-center text-sm text-color-secondary">
        &copy; {{ currentYear }} Facultatea de Inginerie Electrică și Știința Calculatoarelor
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
    const googleAuthAvailable = ref(false)
    const currentYear = computed(() => new Date().getFullYear())
    
    const credentials = ref({
      email: '',
      password: ''
    })
    
    // Funcție pentru autentificarea cu Google
    const handleGoogleLogin = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Verificăm dacă API-ul Google este încărcat și inițializat
        if (!window.gapi || !window.gapi.auth2) {
          throw new Error('API-ul Google nu este încărcat. Vă rugăm să reîncărcați pagina și să încercați din nou.')
        }
        
        // Verificăm dacă avem o instanță auth2
        let auth2
        try {
          auth2 = window.gapi.auth2.getAuthInstance()
          if (!auth2) {
            throw new Error('Instanța auth2 nu este disponibilă')
          }
        } catch (e) {
          console.error('Eroare la obținerea instanței auth2:', e)
          throw new Error('Nu s-a putut inițializa autentificarea Google. Vă rugăm să reîncărcați pagina.')
        }
        
        // Autentificăm utilizatorul
        const googleUser = await auth2.signIn()
        
        // Obținem token-ul ID
        const idToken = googleUser.getAuthResponse().id_token
        
        // Trimitem token-ul către backend pentru autentificare
        await store.dispatch('auth/login', idToken)
        
        // Redirecționăm utilizatorul către pagina de destinație sau dashboard
        const redirectPath = route.query.redirect || '/dashboard'
        router.push(redirectPath)
      } catch (err) {
        console.error('Eroare la autentificare:', err)
        error.value = err.message || 'Eroare la autentificare cu Google. Vă rugăm să încercați din nou.'
      } finally {
        loading.value = false
      }
    }
    
    // Funcție pentru autentificarea cu email și parolă
    const handleEmailLogin = async () => {
      try {
        loading.value = true
        error.value = null
        
        // Trimitem credențialele către backend pentru autentificare
        await store.dispatch('auth/loginWithCredentials', credentials.value)
        
        // Redirecționăm utilizatorul către pagina de destinație sau dashboard
        const redirectPath = route.query.redirect || '/dashboard'
        router.push(redirectPath)
      } catch (err) {
        console.error('Eroare la autentificare:', err)
        error.value = err.message || 'Email sau parolă incorecte. Vă rugăm să încercați din nou.'
      } finally {
        loading.value = false
      }
    }
    
    // Inițializăm Google Sign-In API la încărcarea componentei
    onMounted(() => {
      // Verificăm dacă avem un ID de client Google configurat
      const googleClientId = process.env.VUE_APP_GOOGLE_CLIENT_ID || ''
      
      // Dacă nu avem un ID de client Google configurat, nu încărcăm API-ul Google
      if (googleClientId === '' || googleClientId === 'YOUR_GOOGLE_CLIENT_ID_HERE') {
        console.warn('Google Client ID nu este configurat. Autentificarea Google nu va funcționa.')
        googleAuthAvailable.value = false
        return
      }
      
      // Încercăm să încărcăm API-ul Google
      try {
        // Verificăm dacă API-ul Google este deja încărcat
        if (window.gapi && window.gapi.auth2) {
          window.gapi.auth2.init({
            client_id: googleClientId
          }).then(() => {
            googleAuthAvailable.value = true
          }).catch(err => {
            console.error('Eroare la inițializarea auth2:', err)
            googleAuthAvailable.value = false
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
                client_id: googleClientId
              }).then(() => {
                googleAuthAvailable.value = true
              }).catch(err => {
                console.error('Eroare la inițializarea auth2:', err)
                googleAuthAvailable.value = false
              })
            })
          }
          script.onerror = () => {
            console.error('Eroare la încărcarea API-ului Google')
            googleAuthAvailable.value = false
          }
          document.head.appendChild(script)
        }
      } catch (err) {
        console.error('Eroare la încărcarea API-ului Google:', err)
        googleAuthAvailable.value = false
      }
    })
    
    return {
      loading,
      error,
      googleAuthAvailable,
      credentials,
      currentYear,
      handleGoogleLogin,
      handleEmailLogin
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
  background-color: #f5f7f9;
}

.login-card {
  width: 100%;
  max-width: 450px;
  padding: 2rem;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
}

.logo {
  width: 80px;
  height: 80px;
  margin-bottom: 1rem;
}

.error-message {
  padding: 0.75rem;
  background-color: #ffecec;
  color: #e74c3c;
  border-radius: 4px;
  text-align: center;
}

.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #e0e0e0;
}

.divider span {
  padding: 0 10px;
  color: #666;
  font-size: 0.9rem;
}
</style>

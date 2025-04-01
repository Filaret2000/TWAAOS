<template>
  <div class="profile-container">
    <div class="card">
      <h1 class="text-3xl font-bold mb-4">Profilul meu</h1>
      
      <div v-if="loading" class="p-4 text-center">
        <ProgressSpinner />
        <p class="mt-3">Se încarcă datele profilului...</p>
      </div>
      
      <div v-else>
        <div class="user-info p-4 mb-4">
          <div class="flex align-items-center mb-4">
            <Avatar :label="userInitials" size="xlarge" class="mr-3" />
            <div>
              <h2 class="text-2xl font-bold mb-1">{{ user.firstName }} {{ user.lastName }}</h2>
              <p class="text-color-secondary">{{ userRoleText }}</p>
              <p>{{ user.email }}</p>
            </div>
          </div>
        </div>
        
        <div class="p-4">
          <h3 class="text-xl font-bold mb-3">Informații personale</h3>
          
          <form @submit.prevent="updateProfile">
            <div class="field mb-4">
              <label for="firstName" class="block mb-2">Prenume</label>
              <InputText id="firstName" v-model="form.firstName" class="w-full" />
            </div>
            
            <div class="field mb-4">
              <label for="lastName" class="block mb-2">Nume</label>
              <InputText id="lastName" v-model="form.lastName" class="w-full" />
            </div>
            
            <div class="field mb-4">
              <label for="email" class="block mb-2">Email</label>
              <InputText id="email" v-model="form.email" disabled class="w-full" />
              <small class="text-color-secondary">Adresa de email nu poate fi modificată</small>
            </div>
            
            <div class="field mb-4">
              <label for="password" class="block mb-2">Parolă nouă (opțional)</label>
              <Password id="password" v-model="form.password" toggleMask class="w-full" />
            </div>
            
            <div class="field mb-4">
              <label for="confirmPassword" class="block mb-2">Confirmare parolă</label>
              <Password id="confirmPassword" v-model="form.confirmPassword" toggleMask class="w-full" />
            </div>
            
            <div class="flex justify-content-end">
              <Button type="submit" label="Salvează modificările" :loading="saving" />
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useToast } from 'primevue/usetoast'

export default {
  name: 'Profile',
  setup() {
    const store = useStore()
    const toast = useToast()
    
    const loading = ref(true)
    const saving = ref(false)
    const user = computed(() => store.state.auth.user || {})
    
    const form = reactive({
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: ''
    })
    
    const userInitials = computed(() => {
      if (!user.value) return ''
      return `${user.value.firstName?.charAt(0) || ''}${user.value.lastName?.charAt(0) || ''}`
    })
    
    const userRoleText = computed(() => {
      const roles = {
        'ADMIN': 'Administrator',
        'SEC': 'Secretariat',
        'PROF': 'Cadru didactic',
        'SG': 'Șef de grupă'
      }
      return roles[user.value.role] || user.value.role
    })
    
    onMounted(async () => {
      try {
        await store.dispatch('auth/getCurrentUser')
        form.firstName = user.value.firstName
        form.lastName = user.value.lastName
        form.email = user.value.email
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca datele profilului',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    })
    
    const updateProfile = async () => {
      if (form.password && form.password !== form.confirmPassword) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Parolele nu coincid',
          life: 3000
        })
        return
      }
      
      saving.value = true
      
      try {
        await store.dispatch('auth/updateProfile', {
          firstName: form.firstName,
          lastName: form.lastName,
          password: form.password || undefined
        })
        
        toast.add({
          severity: 'success',
          summary: 'Succes',
          detail: 'Profilul a fost actualizat cu succes',
          life: 3000
        })
        
        form.password = ''
        form.confirmPassword = ''
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: error.message || 'Nu s-a putut actualiza profilul',
          life: 3000
        })
      } finally {
        saving.value = false
      }
    }
    
    return {
      loading,
      saving,
      user,
      form,
      userInitials,
      userRoleText,
      updateProfile
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.user-info {
  background-color: #f8f9fa;
  border-radius: 8px;
}
</style>

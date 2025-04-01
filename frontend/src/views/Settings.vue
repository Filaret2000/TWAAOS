<template>
  <div class="settings-container">
    <div class="card">
      <h1 class="text-3xl font-bold mb-4">Setări</h1>
      
      <TabView>
        <TabPanel header="Notificări">
          <div class="p-3">
            <h2 class="text-xl font-bold mb-3">Preferințe notificări</h2>
            
            <div v-if="loadingNotifications" class="text-center p-4">
              <ProgressSpinner />
              <p class="mt-2">Se încarcă setările...</p>
            </div>
            
            <div v-else>
              <div class="field-checkbox mb-3">
                <Checkbox id="emailNotifications" v-model="notifications.email" binary />
                <label for="emailNotifications" class="ml-2">Primește notificări pe email</label>
              </div>
              
              <div class="field-checkbox mb-3">
                <Checkbox id="scheduleNotifications" v-model="notifications.schedule" binary />
                <label for="scheduleNotifications" class="ml-2">Notificări pentru modificări în planificări</label>
              </div>
              
              <div class="field-checkbox mb-3">
                <Checkbox id="systemNotifications" v-model="notifications.system" binary />
                <label for="systemNotifications" class="ml-2">Notificări de sistem</label>
              </div>
              
              <Button 
                label="Salvează setările" 
                @click="saveNotificationSettings" 
                :loading="savingNotifications"
                class="mt-3"
              />
            </div>
          </div>
        </TabPanel>
        
        <TabPanel header="Interfață">
          <div class="p-3">
            <h2 class="text-xl font-bold mb-3">Preferințe interfață</h2>
            
            <div class="field mb-4">
              <label for="theme" class="block mb-2">Temă</label>
              <Dropdown 
                id="theme" 
                v-model="interfaceSettings.theme" 
                :options="themeOptions" 
                optionLabel="name" 
                optionValue="value"
                class="w-full"
              />
            </div>
            
            <div class="field mb-4">
              <label for="language" class="block mb-2">Limbă</label>
              <Dropdown 
                id="language" 
                v-model="interfaceSettings.language" 
                :options="languageOptions" 
                optionLabel="name" 
                optionValue="value"
                class="w-full"
              />
            </div>
            
            <div class="field-checkbox mb-3">
              <Checkbox id="compactView" v-model="interfaceSettings.compactView" binary />
              <label for="compactView" class="ml-2">Mod compact</label>
            </div>
            
            <Button 
              label="Salvează setările" 
              @click="saveInterfaceSettings" 
              :loading="savingInterface"
              class="mt-3"
            />
          </div>
        </TabPanel>
        
        <TabPanel v-if="isAdmin" header="Sistem">
          <div class="p-3">
            <h2 class="text-xl font-bold mb-3">Setări sistem</h2>
            
            <div class="field mb-4">
              <label for="academicYear" class="block mb-2">An academic curent</label>
              <InputText id="academicYear" v-model="system.academicYear" class="w-full" />
            </div>
            
            <div class="field mb-4">
              <label for="semester" class="block mb-2">Semestru curent</label>
              <Dropdown 
                id="semester" 
                v-model="system.semester" 
                :options="[
                  { name: 'Semestrul 1', value: 1 },
                  { name: 'Semestrul 2', value: 2 }
                ]" 
                optionLabel="name" 
                optionValue="value"
                class="w-full"
              />
            </div>
            
            <Button 
              label="Salvează setările" 
              @click="saveSystemSettings" 
              :loading="savingSystem"
              class="mt-3"
            />
          </div>
        </TabPanel>
      </TabView>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useToast } from 'primevue/usetoast'

export default {
  name: 'Settings',
  setup() {
    const store = useStore()
    const toast = useToast()
    
    const loadingNotifications = ref(true)
    const savingNotifications = ref(false)
    const savingInterface = ref(false)
    const savingSystem = ref(false)
    
    const notifications = reactive({
      email: true,
      schedule: true,
      system: true
    })
    
    const interfaceSettings = reactive({
      theme: 'light',
      language: 'ro',
      compactView: false
    })
    
    const system = reactive({
      academicYear: '2024-2025',
      semester: 2
    })
    
    const themeOptions = [
      { name: 'Luminos', value: 'light' },
      { name: 'Întunecat', value: 'dark' },
      { name: 'Sistem', value: 'system' }
    ]
    
    const languageOptions = [
      { name: 'Română', value: 'ro' },
      { name: 'Engleză', value: 'en' }
    ]
    
    const isAdmin = computed(() => {
      const user = store.state.auth.user
      return user && user.role === 'ADMIN'
    })
    
    onMounted(async () => {
      try {
        // În mod normal, aici ar trebui să facem un apel API pentru a obține setările
        // Simulăm un răspuns de la server
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Setăm valorile implicite
        notifications.email = true
        notifications.schedule = true
        notifications.system = true
        
        interfaceSettings.theme = localStorage.getItem('theme') || 'light'
        interfaceSettings.language = localStorage.getItem('language') || 'ro'
        interfaceSettings.compactView = localStorage.getItem('compactView') === 'true'
        
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut încărca setările',
          life: 3000
        })
      } finally {
        loadingNotifications.value = false
      }
    })
    
    const saveNotificationSettings = async () => {
      savingNotifications.value = true
      
      try {
        // Simulăm un apel API pentru salvarea setărilor
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        toast.add({
          severity: 'success',
          summary: 'Succes',
          detail: 'Setările de notificări au fost salvate',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut salva setările',
          life: 3000
        })
      } finally {
        savingNotifications.value = false
      }
    }
    
    const saveInterfaceSettings = async () => {
      savingInterface.value = true
      
      try {
        // Salvăm setările în localStorage
        localStorage.setItem('theme', interfaceSettings.theme)
        localStorage.setItem('language', interfaceSettings.language)
        localStorage.setItem('compactView', interfaceSettings.compactView)
        
        // Simulăm un apel API pentru salvarea setărilor
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        toast.add({
          severity: 'success',
          summary: 'Succes',
          detail: 'Setările de interfață au fost salvate',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut salva setările',
          life: 3000
        })
      } finally {
        savingInterface.value = false
      }
    }
    
    const saveSystemSettings = async () => {
      savingSystem.value = true
      
      try {
        // Simulăm un apel API pentru salvarea setărilor
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        toast.add({
          severity: 'success',
          summary: 'Succes',
          detail: 'Setările de sistem au fost salvate',
          life: 3000
        })
      } catch (error) {
        toast.add({
          severity: 'error',
          summary: 'Eroare',
          detail: 'Nu s-au putut salva setările',
          life: 3000
        })
      } finally {
        savingSystem.value = false
      }
    }
    
    return {
      loadingNotifications,
      savingNotifications,
      savingInterface,
      savingSystem,
      notifications,
      interfaceSettings,
      system,
      themeOptions,
      languageOptions,
      isAdmin,
      saveNotificationSettings,
      saveInterfaceSettings,
      saveSystemSettings
    }
  }
}
</script>

<style scoped>
.settings-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}
</style>

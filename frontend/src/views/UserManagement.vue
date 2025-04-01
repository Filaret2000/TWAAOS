<template>
  <div class="user-management-container">
    <div class="flex align-items-center justify-content-between mb-4">
      <h1 class="text-3xl font-bold m-0">Gestionare Utilizatori</h1>
      
      <div>
        <Button 
          icon="pi pi-plus" 
          label="Adaugă Utilizator" 
          @click="openNewUserDialog"
          class="mr-2"
        />
        <Button 
          icon="pi pi-upload" 
          label="Import Utilizatori" 
          class="p-button-outlined"
          @click="openImportDialog"
        />
      </div>
    </div>
    
    <Card class="mb-4">
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <InputText 
                id="searchName" 
                v-model="filters.name" 
                class="w-full"
                @input="applyFilters"
              />
              <label for="searchName">Caută după nume</label>
            </span>
          </div>
          
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <InputText 
                id="searchEmail" 
                v-model="filters.email" 
                class="w-full"
                @input="applyFilters"
              />
              <label for="searchEmail">Caută după email</label>
            </span>
          </div>
          
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <Dropdown 
                id="filterRole" 
                v-model="filters.role" 
                :options="roles" 
                optionLabel="name" 
                optionValue="code"
                class="w-full"
                @change="applyFilters"
              />
              <label for="filterRole">Filtrează după rol</label>
            </span>
          </div>
          
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <div class="flex justify-content-end">
              <Button 
                icon="pi pi-filter-slash" 
                label="Resetează filtrele" 
                class="p-button-text"
                @click="resetFilters"
              />
            </div>
          </div>
        </div>
      </template>
    </Card>
    
    <div class="grid">
      <div class="col-12 lg:col-3 mb-4">
        <Card>
          <template #header>
            <h2 class="text-xl font-bold m-0">Statistici Utilizatori</h2>
          </template>
          <template #content>
            <div class="user-stats">
              <div class="user-stat-item mb-3">
                <div class="flex align-items-center justify-content-between">
                  <span class="font-bold">Total utilizatori:</span>
                  <span class="text-xl">{{ userCounts.total }}</span>
                </div>
              </div>
              
              <div class="user-stat-item mb-3">
                <div class="flex align-items-center justify-content-between">
                  <span>Administratori:</span>
                  <Tag value="ADM" severity="info">{{ userCounts.ADM }}</Tag>
                </div>
              </div>
              
              <div class="user-stat-item mb-3">
                <div class="flex align-items-center justify-content-between">
                  <span>Secretariat:</span>
                  <Tag value="SEC" severity="success">{{ userCounts.SEC }}</Tag>
                </div>
              </div>
              
              <div class="user-stat-item mb-3">
                <div class="flex align-items-center justify-content-between">
                  <span>Cadre didactice:</span>
                  <Tag value="CD" severity="warning">{{ userCounts.CD }}</Tag>
                </div>
              </div>
              
              <div class="user-stat-item mb-3">
                <div class="flex align-items-center justify-content-between">
                  <span>Studenți:</span>
                  <Tag value="STD" severity="help">{{ userCounts.STD }}</Tag>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-9">
        <DataTable 
          :value="filteredUsers" 
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[10, 20, 50]"
          :loading="loading"
          v-model:selection="selectedUsers"
          :filters="tableFilters"
          filterDisplay="menu"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <template #empty>
            <div class="text-center p-4">
              <i class="pi pi-users text-5xl text-color-secondary mb-3"></i>
              <p>Nu există utilizatori care să corespundă criteriilor selectate.</p>
            </div>
          </template>
          
          <template #loading>
            <div class="text-center p-4">
              <i class="pi pi-spin pi-spinner text-5xl text-color-secondary mb-3"></i>
              <p>Se încarcă utilizatorii...</p>
            </div>
          </template>
          
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          
          <Column field="lastName" header="Nume" sortable :filter="true" filterMatchMode="contains">
            <template #body="slotProps">
              <span>{{ slotProps.data.lastName }} {{ slotProps.data.firstName }}</span>
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <InputText 
                v-model="filterModel.value" 
                @input="filterCallback()" 
                placeholder="Caută după nume" 
                class="p-column-filter w-full"
              />
            </template>
          </Column>
          
          <Column field="email" header="Email" sortable :filter="true" filterMatchMode="contains">
            <template #filter="{ filterModel, filterCallback }">
              <InputText 
                v-model="filterModel.value" 
                @input="filterCallback()" 
                placeholder="Caută după email" 
                class="p-column-filter w-full"
              />
            </template>
          </Column>
          
          <Column field="role" header="Rol" sortable :filter="true" filterMatchMode="equals">
            <template #body="slotProps">
              <Tag :value="slotProps.data.role" :severity="getRoleSeverity(slotProps.data.role)">
                {{ getRoleLabel(slotProps.data.role) }}
              </Tag>
            </template>
            <template #filter="{ filterModel, filterCallback }">
              <Dropdown 
                v-model="filterModel.value" 
                @change="filterCallback()" 
                :options="roles" 
                optionLabel="name" 
                optionValue="code"
                placeholder="Selectează rol" 
                class="p-column-filter w-full"
              />
            </template>
          </Column>
          
          <Column field="createdAt" header="Data înregistrării" sortable>
            <template #body="slotProps">
              <span>{{ formatDate(slotProps.data.createdAt) }}</span>
            </template>
          </Column>
          
          <Column header="Acțiuni" :exportable="false">
            <template #body="slotProps">
              <div class="flex">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-rounded p-button-text p-button-sm mr-2"
                  @click="editUser(slotProps.data)"
                  v-tooltip.top="'Editează'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-rounded p-button-text p-button-sm p-button-danger"
                  @click="confirmDeleteUser(slotProps.data)"
                  v-tooltip.top="'Șterge'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
    
    <!-- Dialog pentru adăugarea/editarea unui utilizator -->
    <Dialog 
      :visible="userDialog.visible" 
      :style="{ width: '450px' }" 
      :modal="true"
      :closable="false"
      :header="userDialog.isEdit ? 'Editare Utilizator' : 'Adăugare Utilizator'"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="email">Email</label>
          <InputText 
            id="email" 
            v-model="userDialog.user.email" 
            :disabled="userDialog.isEdit"
            placeholder="Introduceți emailul utilizatorului"
            :class="{ 'p-invalid': userDialog.submitted && !userDialog.user.email }"
          />
          <small v-if="userDialog.submitted && !userDialog.user.email" class="p-error">Emailul este obligatoriu.</small>
        </div>
        
        <div class="field">
          <label for="firstName">Prenume</label>
          <InputText 
            id="firstName" 
            v-model="userDialog.user.firstName" 
            placeholder="Introduceți prenumele utilizatorului"
            :class="{ 'p-invalid': userDialog.submitted && !userDialog.user.firstName }"
          />
          <small v-if="userDialog.submitted && !userDialog.user.firstName" class="p-error">Prenumele este obligatoriu.</small>
        </div>
        
        <div class="field">
          <label for="lastName">Nume</label>
          <InputText 
            id="lastName" 
            v-model="userDialog.user.lastName" 
            placeholder="Introduceți numele utilizatorului"
            :class="{ 'p-invalid': userDialog.submitted && !userDialog.user.lastName }"
          />
          <small v-if="userDialog.submitted && !userDialog.user.lastName" class="p-error">Numele este obligatoriu.</small>
        </div>
        
        <div class="field">
          <label for="role">Rol</label>
          <Dropdown 
            id="role" 
            v-model="userDialog.user.role" 
            :options="roles" 
            optionLabel="name" 
            optionValue="code"
            placeholder="Selectați rolul utilizatorului"
            :class="{ 'p-invalid': userDialog.submitted && !userDialog.user.role }"
          />
          <small v-if="userDialog.submitted && !userDialog.user.role" class="p-error">Rolul este obligatoriu.</small>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulează" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideUserDialog"
        />
        <Button 
          label="Salvează" 
          icon="pi pi-check" 
          class="p-button-primary" 
          @click="saveUser"
          :loading="userDialog.saving"
        />
      </template>
    </Dialog>
    
    <!-- Dialog pentru importul utilizatorilor -->
    <Dialog 
      v-model:visible="importDialog.visible" 
      :style="{ width: '450px' }" 
      :modal="true"
      header="Import Utilizatori"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="importFile">Fișier Excel</label>
          <FileUpload 
            id="importFile" 
            mode="basic" 
            accept=".xlsx,.xls" 
            :maxFileSize="1000000"
            chooseLabel="Selectează fișier"
            :auto="true"
            :customUpload="true"
            @uploader="importUsers"
            :class="{ 'p-invalid': importDialog.submitted && !importDialog.file }"
          />
          <small v-if="importDialog.submitted && !importDialog.file" class="p-error">Fișierul este obligatoriu.</small>
        </div>
        
        <div class="field">
          <div class="field-checkbox">
            <Checkbox 
              id="overwriteExisting" 
              v-model="importDialog.overwriteExisting" 
              binary
            />
            <label for="overwriteExisting" class="ml-2">Suprascrie utilizatorii existenți</label>
          </div>
        </div>
        
        <div class="field">
          <div class="field-checkbox">
            <Checkbox 
              id="sendWelcomeEmail" 
              v-model="importDialog.sendWelcomeEmail" 
              binary
            />
            <label for="sendWelcomeEmail" class="ml-2">Trimite email de bun venit</label>
          </div>
        </div>
        
        <div class="mt-3">
          <p class="text-sm text-color-secondary">
            Fișierul Excel trebuie să conțină următoarele coloane: Email, Prenume, Nume, Rol (ADM, SEC, CD sau STD).
          </p>
          <p class="text-sm text-color-secondary mt-2">
            <a href="/api/auth/admin/users/template" class="text-primary">Descarcă template</a>
          </p>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulează" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="importDialog.visible = false"
        />
        <Button 
          label="Importă" 
          icon="pi pi-upload" 
          class="p-button-primary" 
          @click="submitImport"
          :loading="importDialog.importing"
        />
      </template>
    </Dialog>
    
    <!-- Dialog pentru confirmarea ștergerii -->
    <ConfirmDialog></ConfirmDialog>
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useConfirm } from 'primevue/useconfirm'
import moment from 'moment'

export default {
  name: 'UserManagement',
  setup() {
    const store = useStore()
    const confirm = useConfirm()
    
    const loading = ref(false)
    const selectedUsers = ref([])
    
    // Filtre pentru tabel
    const tableFilters = ref({})
    
    // Filtre pentru căutare
    const filters = reactive({
      name: '',
      email: '',
      role: null
    })
    
    // Dialog pentru adăugarea/editarea unui utilizator
    const userDialog = reactive({
      visible: false,
      isEdit: false,
      user: {
        id: null,
        email: '',
        firstName: '',
        lastName: '',
        role: null
      },
      submitted: false,
      saving: false
    })
    
    // Dialog pentru importul utilizatorilor
    const importDialog = reactive({
      visible: false,
      file: null,
      overwriteExisting: false,
      sendWelcomeEmail: true,
      submitted: false,
      importing: false
    })
    
    // Obținem datele din store
    const users = computed(() => store.state.user.users)
    
    // Opțiuni pentru roluri
    const roles = [
      { name: 'Administrator', code: 'ADM' },
      { name: 'Secretariat', code: 'SEC' },
      { name: 'Cadru didactic', code: 'CD' },
      { name: 'Student', code: 'STD' }
    ]
    
    // Calculăm numărul de utilizatori pentru fiecare rol
    const userCounts = computed(() => {
      const counts = {
        total: users.value.length,
        ADM: 0,
        SEC: 0,
        CD: 0,
        STD: 0
      }
      
      users.value.forEach(user => {
        if (counts[user.role] !== undefined) {
          counts[user.role]++
        }
      })
      
      return counts
    })
    
    // Filtrăm utilizatorii în funcție de filtrele selectate
    const filteredUsers = computed(() => {
      let result = [...users.value]
      
      if (filters.name) {
        const searchName = filters.name.toLowerCase()
        result = result.filter(user => {
          const fullName = `${user.lastName} ${user.firstName}`.toLowerCase()
          return fullName.includes(searchName)
        })
      }
      
      if (filters.email) {
        const searchEmail = filters.email.toLowerCase()
        result = result.filter(user => {
          return user.email.toLowerCase().includes(searchEmail)
        })
      }
      
      if (filters.role) {
        result = result.filter(user => user.role === filters.role)
      }
      
      return result
    })
    
    // Funcție pentru formatarea datei
    const formatDate = (dateString) => {
      return moment(dateString).format('DD.MM.YYYY')
    }
    
    // Funcție pentru obținerea severității tag-ului pentru rol
    const getRoleSeverity = (role) => {
      switch (role) {
        case 'ADM': return 'info'
        case 'SEC': return 'success'
        case 'CD': return 'warning'
        case 'STD': return 'help'
        default: return 'secondary'
      }
    }
    
    // Funcție pentru obținerea etichetei rolului
    const getRoleLabel = (role) => {
      switch (role) {
        case 'ADM': return 'Administrator'
        case 'SEC': return 'Secretariat'
        case 'CD': return 'Cadru didactic'
        case 'STD': return 'Student'
        default: return role
      }
    }
    
    // Funcție pentru aplicarea filtrelor
    const applyFilters = () => {
      // Nu este nevoie să facem nimic aici, deoarece filteredUsers este un computed
    }
    
    // Funcție pentru resetarea filtrelor
    const resetFilters = () => {
      filters.name = ''
      filters.email = ''
      filters.role = null
    }
    
    // Funcție pentru deschiderea dialogului de adăugare a unui nou utilizator
    const openNewUserDialog = () => {
      userDialog.user = {
        id: null,
        email: '',
        firstName: '',
        lastName: '',
        role: null
      }
      userDialog.isEdit = false
      userDialog.submitted = false
      userDialog.visible = true
    }
    
    // Funcție pentru deschiderea dialogului de editare a unui utilizator
    const editUser = (user) => {
      userDialog.user = { ...user }
      userDialog.isEdit = true
      userDialog.submitted = false
      userDialog.visible = true
    }
    
    // Funcție pentru ascunderea dialogului de utilizator
    const hideUserDialog = () => {
      userDialog.visible = false
      userDialog.submitted = false
    }
    
    // Funcție pentru salvarea unui utilizator
    const saveUser = async () => {
      userDialog.submitted = true
      
      // Verificăm dacă toate câmpurile obligatorii sunt completate
      if (!userDialog.user.email || !userDialog.user.firstName || !userDialog.user.lastName || !userDialog.user.role) {
        return
      }
      
      try {
        userDialog.saving = true
        
        if (userDialog.isEdit) {
          // Actualizăm utilizatorul existent
          await store.dispatch('user/updateUser', {
            userId: userDialog.user.id,
            userData: {
              firstName: userDialog.user.firstName,
              lastName: userDialog.user.lastName,
              role: userDialog.user.role
            }
          })
          
          // Afișăm un mesaj de succes
          store.dispatch('toast/add', {
            severity: 'success',
            summary: 'Succes',
            detail: 'Utilizatorul a fost actualizat cu succes',
            life: 3000
          })
        } else {
          // Creăm un nou utilizator
          await store.dispatch('user/createUser', {
            email: userDialog.user.email,
            firstName: userDialog.user.firstName,
            lastName: userDialog.user.lastName,
            role: userDialog.user.role
          })
          
          // Afișăm un mesaj de succes
          store.dispatch('toast/add', {
            severity: 'success',
            summary: 'Succes',
            detail: 'Utilizatorul a fost creat cu succes',
            life: 3000
          })
        }
        
        // Închidem dialogul
        hideUserDialog()
      } catch (error) {
        console.error('Eroare la salvarea utilizatorului:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: error.response?.data?.error || 'A apărut o eroare la salvarea utilizatorului',
          life: 3000
        })
      } finally {
        userDialog.saving = false
      }
    }
    
    // Funcție pentru confirmarea ștergerii unui utilizator
    const confirmDeleteUser = (user) => {
      confirm.require({
        message: `Sunteți sigur că doriți să ștergeți utilizatorul ${user.lastName} ${user.firstName}?`,
        header: 'Confirmare ștergere',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: () => deleteUser(user.id),
        reject: () => {}
      })
    }
    
    // Funcție pentru ștergerea unui utilizator
    const deleteUser = async (userId) => {
      try {
        loading.value = true
        
        // Ștergem utilizatorul
        await store.dispatch('user/deleteUser', userId)
        
        // Afișăm un mesaj de succes
        store.dispatch('toast/add', {
          severity: 'success',
          summary: 'Succes',
          detail: 'Utilizatorul a fost șters cu succes',
          life: 3000
        })
      } catch (error) {
        console.error('Eroare la ștergerea utilizatorului:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la ștergerea utilizatorului',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    }
    
    // Funcție pentru deschiderea dialogului de import
    const openImportDialog = () => {
      importDialog.file = null
      importDialog.overwriteExisting = false
      importDialog.sendWelcomeEmail = true
      importDialog.submitted = false
      importDialog.visible = true
    }
    
    // Funcție pentru importul utilizatorilor
    const importUsers = (event) => {
      importDialog.file = event.files[0]
    }
    
    // Funcție pentru trimiterea importului
    const submitImport = async () => {
      importDialog.submitted = true
      
      // Verificăm dacă a fost selectat un fișier
      if (!importDialog.file) {
        return
      }
      
      try {
        importDialog.importing = true
        
        // Creăm un obiect FormData pentru a trimite fișierul
        const formData = new FormData()
        formData.append('file', importDialog.file)
        formData.append('overwriteExisting', importDialog.overwriteExisting)
        formData.append('sendWelcomeEmail', importDialog.sendWelcomeEmail)
        
        // Importăm utilizatorii
        await store.dispatch('user/importUsers', formData)
        
        // Afișăm un mesaj de succes
        store.dispatch('toast/add', {
          severity: 'success',
          summary: 'Succes',
          detail: 'Utilizatorii au fost importați cu succes',
          life: 3000
        })
        
        // Închidem dialogul
        importDialog.visible = false
      } catch (error) {
        console.error('Eroare la importul utilizatorilor:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la importul utilizatorilor',
          life: 3000
        })
      } finally {
        importDialog.importing = false
      }
    }
    
    // Încărcăm datele la montarea componentei
    onMounted(async () => {
      try {
        loading.value = true
        
        // Încărcăm utilizatorii
        await store.dispatch('user/fetchUsers')
      } catch (error) {
        console.error('Eroare la încărcarea utilizatorilor:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la încărcarea utilizatorilor',
          life: 3000
        })
      } finally {
        loading.value = false
      }
    })
    
    return {
      loading,
      selectedUsers,
      tableFilters,
      filters,
      userDialog,
      importDialog,
      users,
      filteredUsers,
      roles,
      userCounts,
      formatDate,
      getRoleSeverity,
      getRoleLabel,
      applyFilters,
      resetFilters,
      openNewUserDialog,
      editUser,
      hideUserDialog,
      saveUser,
      confirmDeleteUser,
      openImportDialog,
      importUsers,
      submitImport
    }
  }
}
</script>

<style scoped>
.user-management-container {
  padding-bottom: 2rem;
}

.user-stat-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--surface-border);
}

.user-stat-item:last-child {
  border-bottom: none;
}
</style>

<template>
  <div class="notifications-container">
    <div class="flex align-items-center justify-content-between mb-4">
      <h1 class="text-3xl font-bold m-0">Notificări</h1>
      
      <div>
        <Button 
          v-if="canSendNotifications" 
          icon="pi pi-send" 
          label="Trimite Notificare" 
          @click="openNewNotificationDialog"
          class="mr-2"
        />
        <Button 
          icon="pi pi-check" 
          label="Marchează toate ca citite" 
          class="p-button-outlined"
          @click="markAllAsRead"
          :disabled="unreadCount === 0"
        />
      </div>
    </div>
    
    <Card class="mb-4">
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.type" 
                :options="notificationTypes" 
                optionLabel="name" 
                optionValue="code"
                class="w-full"
                @change="applyFilters"
              />
              <label>Tip notificare</label>
            </span>
          </div>
          
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <span class="p-float-label">
              <Calendar 
                v-model="filters.date" 
                dateFormat="dd.mm.yy" 
                class="w-full"
                @date-select="applyFilters"
              />
              <label>Data</label>
            </span>
          </div>
          
          <div class="col-12 md:col-6 lg:col-3 mb-3">
            <div class="field-checkbox">
              <Checkbox 
                v-model="filters.unreadOnly" 
                binary 
                inputId="unreadOnly"
                @change="applyFilters"
              />
              <label for="unreadOnly">Doar necitite</label>
            </div>
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
    
    <div v-if="loading" class="text-center p-5">
      <ProgressSpinner />
      <p>Se încarcă notificările...</p>
    </div>
    
    <div v-else-if="filteredNotifications.length === 0" class="text-center p-5">
      <i class="pi pi-inbox text-5xl text-color-secondary mb-3"></i>
      <p>Nu aveți notificări care să corespundă criteriilor selectate.</p>
    </div>
    
    <div v-else class="notification-list">
      <div v-for="notification in filteredNotifications" :key="notification.id" class="notification-item p-3 mb-3">
        <div class="flex align-items-start">
          <div class="notification-icon-container mr-3">
            <i :class="getNotificationIcon(notification.type)" class="notification-icon"></i>
          </div>
          
          <div class="notification-content flex-1">
            <div class="flex align-items-center justify-content-between mb-1">
              <h3 class="text-xl font-bold m-0">{{ notification.title }}</h3>
              <span class="text-sm text-color-secondary">{{ formatTimeAgo(notification.createdAt) }}</span>
            </div>
            
            <p class="notification-message mb-3">{{ notification.message }}</p>
            
            <div class="flex align-items-center justify-content-between">
              <div class="notification-meta">
                <span class="text-sm text-color-secondary">
                  De la: {{ notification.sender ? `${notification.sender.lastName} ${notification.sender.firstName}` : 'Sistem' }}
                </span>
              </div>
              
              <div class="notification-actions">
                <Button 
                  v-if="!notification.read" 
                  icon="pi pi-check" 
                  class="p-button-rounded p-button-text p-button-sm"
                  @click="markAsRead(notification.id)"
                  v-tooltip.top="'Marchează ca citit'"
                />
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-rounded p-button-text p-button-sm"
                  @click="viewNotificationDetails(notification)"
                  v-tooltip.top="'Vizualizează detalii'"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Dialog pentru trimiterea unei noi notificări -->
    <Dialog 
      v-model:visible="newNotificationDialog.visible" 
      :style="{ width: '50vw' }" 
      :modal="true"
      header="Trimite Notificare"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="title">Titlu</label>
          <InputText 
            id="title" 
            v-model="newNotificationDialog.title" 
            placeholder="Introduceți titlul notificării"
            :class="{ 'p-invalid': newNotificationDialog.submitted && !newNotificationDialog.title }"
          />
          <small v-if="newNotificationDialog.submitted && !newNotificationDialog.title" class="p-error">Titlul este obligatoriu.</small>
        </div>
        
        <div class="field">
          <label for="message">Mesaj</label>
          <Textarea 
            id="message" 
            v-model="newNotificationDialog.message" 
            rows="5" 
            placeholder="Introduceți mesajul notificării"
            :class="{ 'p-invalid': newNotificationDialog.submitted && !newNotificationDialog.message }"
          />
          <small v-if="newNotificationDialog.submitted && !newNotificationDialog.message" class="p-error">Mesajul este obligatoriu.</small>
        </div>
        
        <div class="field">
          <label for="recipients">Destinatari</label>
          <Dropdown 
            id="recipients" 
            v-model="newNotificationDialog.recipientType" 
            :options="recipientTypes" 
            optionLabel="name" 
            optionValue="code"
            placeholder="Selectați tipul de destinatari"
            :class="{ 'p-invalid': newNotificationDialog.submitted && !newNotificationDialog.recipientType }"
          />
          <small v-if="newNotificationDialog.submitted && !newNotificationDialog.recipientType" class="p-error">Tipul de destinatari este obligatoriu.</small>
        </div>
        
        <div class="field" v-if="newNotificationDialog.recipientType === 'SPECIFIC'">
          <label for="specificRecipients">Destinatari specifici</label>
          <MultiSelect 
            id="specificRecipients" 
            v-model="newNotificationDialog.specificRecipients" 
            :options="users" 
            optionLabel="fullName" 
            placeholder="Selectați destinatarii"
            :class="{ 'p-invalid': newNotificationDialog.submitted && newNotificationDialog.recipientType === 'SPECIFIC' && (!newNotificationDialog.specificRecipients || newNotificationDialog.specificRecipients.length === 0) }"
            display="chip"
          />
          <small v-if="newNotificationDialog.submitted && newNotificationDialog.recipientType === 'SPECIFIC' && (!newNotificationDialog.specificRecipients || newNotificationDialog.specificRecipients.length === 0)" class="p-error">Cel puțin un destinatar este obligatoriu.</small>
        </div>
        
        <div class="field" v-if="newNotificationDialog.recipientType === 'ROLE'">
          <label for="role">Rol destinatari</label>
          <Dropdown 
            id="role" 
            v-model="newNotificationDialog.role" 
            :options="roles" 
            optionLabel="name" 
            optionValue="code"
            placeholder="Selectați rolul destinatarilor"
            :class="{ 'p-invalid': newNotificationDialog.submitted && newNotificationDialog.recipientType === 'ROLE' && !newNotificationDialog.role }"
          />
          <small v-if="newNotificationDialog.submitted && newNotificationDialog.recipientType === 'ROLE' && !newNotificationDialog.role" class="p-error">Rolul destinatarilor este obligatoriu.</small>
        </div>
        
        <div class="field-checkbox">
          <Checkbox 
            v-model="newNotificationDialog.sendEmail" 
            binary 
            inputId="sendEmail"
          />
          <label for="sendEmail">Trimite și prin email</label>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Anulează" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="newNotificationDialog.visible = false"
        />
        <Button 
          label="Trimite" 
          icon="pi pi-send" 
          class="p-button-primary" 
          @click="sendNotification"
          :loading="newNotificationDialog.sending"
        />
      </template>
    </Dialog>
    
    <!-- Dialog pentru vizualizarea detaliilor unei notificări -->
    <Dialog 
      v-model:visible="notificationDetailsDialog.visible" 
      :style="{ width: '40vw' }" 
      :modal="true"
      :header="notificationDetailsDialog.notification?.title || 'Detalii Notificare'"
    >
      <div v-if="notificationDetailsDialog.notification" class="notification-details">
        <div class="notification-detail-item mb-3">
          <span class="font-bold">De la:</span>
          <span>{{ notificationDetailsDialog.notification.sender ? `${notificationDetailsDialog.notification.sender.lastName} ${notificationDetailsDialog.notification.sender.firstName}` : 'Sistem' }}</span>
        </div>
        
        <div class="notification-detail-item mb-3">
          <span class="font-bold">Data:</span>
          <span>{{ formatDate(notificationDetailsDialog.notification.createdAt) }}</span>
        </div>
        
        <div class="notification-detail-item mb-3">
          <span class="font-bold">Tip:</span>
          <span>{{ getNotificationTypeLabel(notificationDetailsDialog.notification.type) }}</span>
        </div>
        
        <div class="notification-detail-item mb-3">
          <span class="font-bold">Mesaj:</span>
          <p class="mt-2">{{ notificationDetailsDialog.notification.message }}</p>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import moment from 'moment'

export default {
  name: 'Notifications',
  setup() {
    const store = useStore()
    
    const loading = ref(false)
    
    // Filtre pentru notificări
    const filters = reactive({
      type: null,
      date: null,
      unreadOnly: false
    })
    
    // Dialog pentru trimiterea unei noi notificări
    const newNotificationDialog = reactive({
      visible: false,
      title: '',
      message: '',
      recipientType: null,
      specificRecipients: [],
      role: null,
      sendEmail: true,
      submitted: false,
      sending: false
    })
    
    // Dialog pentru vizualizarea detaliilor unei notificări
    const notificationDetailsDialog = reactive({
      visible: false,
      notification: null
    })
    
    // Obținem datele din store
    const user = computed(() => store.state.auth.user)
    const notifications = computed(() => store.state.notification.notifications)
    const unreadCount = computed(() => store.state.notification.unreadCount)
    const users = computed(() => store.state.user.users)
    
    // Opțiuni pentru tipurile de notificări
    const notificationTypes = [
      { name: 'Toate', code: null },
      { name: 'Planificare creată', code: 'SCHEDULE_CREATED' },
      { name: 'Planificare actualizată', code: 'SCHEDULE_UPDATED' },
      { name: 'Planificare ștearsă', code: 'SCHEDULE_DELETED' },
      { name: 'Sistem', code: 'SYSTEM' },
      { name: 'Altele', code: 'OTHER' }
    ]
    
    // Opțiuni pentru tipurile de destinatari
    const recipientTypes = [
      { name: 'Toți utilizatorii', code: 'ALL' },
      { name: 'Utilizatori specifici', code: 'SPECIFIC' },
      { name: 'Utilizatori cu rol specific', code: 'ROLE' }
    ]
    
    // Opțiuni pentru roluri
    const roles = [
      { name: 'Administratori', code: 'ADM' },
      { name: 'Secretariat', code: 'SEC' },
      { name: 'Cadre didactice', code: 'CD' },
      { name: 'Studenți', code: 'STD' }
    ]
    
    // Verificăm permisiunile utilizatorului
    const canSendNotifications = computed(() => {
      return user.value && ['ADM', 'SEC'].includes(user.value.role)
    })
    
    // Filtrăm notificările în funcție de filtrele selectate
    const filteredNotifications = computed(() => {
      let result = [...notifications.value]
      
      if (filters.type) {
        result = result.filter(notification => notification.type === filters.type)
      }
      
      if (filters.date) {
        const filterDate = moment(filters.date).format('YYYY-MM-DD')
        result = result.filter(notification => {
          const notificationDate = moment(notification.createdAt).format('YYYY-MM-DD')
          return notificationDate === filterDate
        })
      }
      
      if (filters.unreadOnly) {
        result = result.filter(notification => !notification.read)
      }
      
      // Sortăm notificările după data creării (cele mai recente primele)
      return result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    })
    
    // Funcție pentru formatarea datei
    const formatDate = (dateString) => {
      return moment(dateString).format('DD.MM.YYYY HH:mm')
    }
    
    // Funcție pentru formatarea timpului relativ
    const formatTimeAgo = (dateString) => {
      return moment(dateString).fromNow()
    }
    
    // Funcție pentru obținerea iconului notificării
    const getNotificationIcon = (type) => {
      switch (type) {
        case 'SCHEDULE_CREATED': return 'pi pi-calendar-plus text-success'
        case 'SCHEDULE_UPDATED': return 'pi pi-calendar-times text-warning'
        case 'SCHEDULE_DELETED': return 'pi pi-calendar-minus text-danger'
        case 'SYSTEM': return 'pi pi-info-circle text-info'
        default: return 'pi pi-bell text-primary'
      }
    }
    
    // Funcție pentru obținerea etichetei tipului de notificare
    const getNotificationTypeLabel = (type) => {
      switch (type) {
        case 'SCHEDULE_CREATED': return 'Planificare creată'
        case 'SCHEDULE_UPDATED': return 'Planificare actualizată'
        case 'SCHEDULE_DELETED': return 'Planificare ștearsă'
        case 'SYSTEM': return 'Sistem'
        default: return 'Altele'
      }
    }
    
    // Funcție pentru aplicarea filtrelor
    const applyFilters = () => {
      // Nu este nevoie să facem nimic aici, deoarece filteredNotifications este un computed
    }
    
    // Funcție pentru resetarea filtrelor
    const resetFilters = () => {
      filters.type = null
      filters.date = null
      filters.unreadOnly = false
    }
    
    // Funcție pentru marcarea unei notificări ca citită
    const markAsRead = async (notificationId) => {
      try {
        await store.dispatch('notification/markAsRead', notificationId)
      } catch (error) {
        console.error('Eroare la marcarea notificării ca citită:', error)
      }
    }
    
    // Funcție pentru marcarea tuturor notificărilor ca citite
    const markAllAsRead = async () => {
      try {
        await store.dispatch('notification/markAllAsRead')
      } catch (error) {
        console.error('Eroare la marcarea tuturor notificărilor ca citite:', error)
      }
    }
    
    // Funcție pentru deschiderea dialogului de trimitere a unei noi notificări
    const openNewNotificationDialog = () => {
      newNotificationDialog.title = ''
      newNotificationDialog.message = ''
      newNotificationDialog.recipientType = null
      newNotificationDialog.specificRecipients = []
      newNotificationDialog.role = null
      newNotificationDialog.sendEmail = true
      newNotificationDialog.submitted = false
      newNotificationDialog.visible = true
    }
    
    // Funcție pentru trimiterea unei notificări
    const sendNotification = async () => {
      newNotificationDialog.submitted = true
      
      // Verificăm dacă toate câmpurile obligatorii sunt completate
      if (!newNotificationDialog.title || !newNotificationDialog.message || !newNotificationDialog.recipientType) {
        return
      }
      
      if (newNotificationDialog.recipientType === 'SPECIFIC' && 
          (!newNotificationDialog.specificRecipients || newNotificationDialog.specificRecipients.length === 0)) {
        return
      }
      
      if (newNotificationDialog.recipientType === 'ROLE' && !newNotificationDialog.role) {
        return
      }
      
      try {
        newNotificationDialog.sending = true
        
        // Pregătim datele pentru trimiterea notificării
        const notificationData = {
          title: newNotificationDialog.title,
          message: newNotificationDialog.message,
          sendEmail: newNotificationDialog.sendEmail,
          type: 'OTHER'
        }
        
        // Adăugăm destinatarii în funcție de tipul selectat
        if (newNotificationDialog.recipientType === 'ALL') {
          notificationData.recipients = null
          notificationData.role = null
        } else if (newNotificationDialog.recipientType === 'SPECIFIC') {
          notificationData.recipients = newNotificationDialog.specificRecipients.map(user => user.id)
          notificationData.role = null
        } else if (newNotificationDialog.recipientType === 'ROLE') {
          notificationData.recipients = null
          notificationData.role = newNotificationDialog.role
        }
        
        // Trimitem notificarea
        await store.dispatch('notification/sendNotification', notificationData)
        
        // Închidem dialogul
        newNotificationDialog.visible = false
        
        // Afișăm un mesaj de succes
        store.dispatch('toast/add', {
          severity: 'success',
          summary: 'Succes',
          detail: 'Notificarea a fost trimisă cu succes',
          life: 3000
        })
        
        // Reîncărcăm notificările
        await store.dispatch('notification/fetchNotifications')
      } catch (error) {
        console.error('Eroare la trimiterea notificării:', error)
        
        // Afișăm un mesaj de eroare
        store.dispatch('toast/add', {
          severity: 'error',
          summary: 'Eroare',
          detail: 'A apărut o eroare la trimiterea notificării',
          life: 3000
        })
      } finally {
        newNotificationDialog.sending = false
      }
    }
    
    // Funcție pentru vizualizarea detaliilor unei notificări
    const viewNotificationDetails = (notification) => {
      notificationDetailsDialog.notification = notification
      notificationDetailsDialog.visible = true
      
      // Marcăm notificarea ca citită dacă nu este deja
      if (!notification.read) {
        markAsRead(notification.id)
      }
    }
    
    // Încărcăm datele la montarea componentei
    onMounted(async () => {
      try {
        loading.value = true
        
        // Încărcăm notificările
        await store.dispatch('notification/fetchNotifications')
        
        // Încărcăm utilizatorii dacă utilizatorul curent poate trimite notificări
        if (canSendNotifications.value && users.value.length === 0) {
          await store.dispatch('user/fetchUsers')
        }
      } catch (error) {
        console.error('Eroare la încărcarea datelor:', error)
      } finally {
        loading.value = false
      }
    })
    
    return {
      loading,
      filters,
      newNotificationDialog,
      notificationDetailsDialog,
      notifications,
      filteredNotifications,
      unreadCount,
      users,
      notificationTypes,
      recipientTypes,
      roles,
      canSendNotifications,
      formatDate,
      formatTimeAgo,
      getNotificationIcon,
      getNotificationTypeLabel,
      applyFilters,
      resetFilters,
      markAsRead,
      markAllAsRead,
      openNewNotificationDialog,
      sendNotification,
      viewNotificationDetails
    }
  }
}
</script>

<style scoped>
.notifications-container {
  padding-bottom: 2rem;
}

.notification-list {
  margin-top: 1rem;
}

.notification-item {
  background-color: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.notification-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.notification-icon-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--surface-ground);
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-icon {
  font-size: 1.2rem;
}

.notification-message {
  white-space: pre-line;
}

.notification-detail-item {
  display: flex;
  flex-direction: column;
}
</style>
